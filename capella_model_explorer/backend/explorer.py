# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import logging
import operator
import os
import pathlib
import time
import typing as t
import urllib.parse as urlparse
from pathlib import Path

import capellambse
import fastapi
import markupsafe
import prometheus_client
import yaml
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateSyntaxError,
    is_undefined,
)

from capella_model_explorer.backend.templates import TemplateLoader

from . import __version__, makers

esc = markupsafe.escape

PATH_TO_FRONTEND = Path("./frontend/dist")
ROUTE_PREFIX = os.getenv("ROUTE_PREFIX", "")
LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class CapellaModelExplorerBackend:
    app: FastAPI = dataclasses.field(init=False)
    env: Environment = dataclasses.field(init=False)
    templates: dict[str, t.Any] = dataclasses.field(
        init=False, default_factory=dict
    )
    templates_loader: TemplateLoader = dataclasses.field(init=False)

    templates_path: Path
    model: capellambse.MelodyModel

    templates_index: t.Optional[t.Any] = dataclasses.field(init=False)

    def __post_init__(self):
        self.app = FastAPI(version=__version__)
        self.router = APIRouter(prefix=ROUTE_PREFIX)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.templates_loader = TemplateLoader(self.model)
        self.env = Environment(loader=FileSystemLoader(self.templates_path))
        self.env.finalize = self.__finalize
        self.env.filters["make_href"] = self.__make_href_filter
        #self.grouped_templates, self.templates = index_templates(
        #    self.templates_path
        #)
        self.app.state.templates = Jinja2Templates(directory=PATH_TO_FRONTEND)
        self.configure_routes()
        self.app.include_router(self.router)
        self.idle_time_gauge = prometheus_client.Gauge(
            "idletime_minutes",
            "Time in minutes since the last user interaction",
        )
        self.last_interaction = time.time()

        @self.app.middleware("http")
        async def update_last_interaction_time(request: Request, call_next):
            if (
                not request.url.path == "/metrics"
                and not request.url.path == "/favicon.ico"
            ):
                self.last_interaction = time.time()
            return await call_next(request)

    def __finalize(self, markup: t.Any) -> object:
        markup = markupsafe.escape(markup)
        return capellambse.helpers.replace_hlinks(
            markup, self.model, self.__make_href
        )

    def __make_href_filter(self, obj: object) -> str | None:
        if is_undefined(obj) or obj is None:
            return "#"

        if isinstance(obj, capellambse.model.ElementList):
            raise TypeError("Cannot make an href to a list of elements")
        if not isinstance(
            obj,
            (
                capellambse.model.GenericElement,
                capellambse.model.diagram.AbstractDiagram,
            ),
        ):
            raise TypeError(f"Expected a model object, got {obj!r}")

        try:
            self.model.by_uuid(obj.uuid)
        except KeyError:
            return "#"

        return self.__make_href(obj)

    def __make_href(
        self,
        obj: (
            capellambse.model.GenericElement
            | capellambse.model.diagram.AbstractDiagram
        ),
    ) -> str | None:
        for idx, template in self.templates.items():
            clsname = template.get("variable", {}).get("type")
            if obj.__class__.__name__ == clsname:
                return f"{ROUTE_PREFIX}/{idx}/{obj.uuid}"

        return f"{ROUTE_PREFIX}/__generic__/{obj.uuid}"

    def render_instance_page(self, template_text, base, object=None):
        try:
            # render the template with the object
            template = self.env.from_string(template_text)
            rendered = template.render(object=object, model=self.model)
            return HTMLResponse(content=rendered, status_code=200)
        except TemplateSyntaxError as e:
            error_message = markupsafe.Markup(
                "<p style='color:red'>Template syntax error: {}, line {}</p>"
            ).format(e.message, e.lineno)
            base["isBroken"] = True
            print(base)
            return HTMLResponse(content=error_message)
        except Exception as e:
            error_message = markupsafe.Markup(
                '<p style="color:red">'
                "Unexpected error: {etype}: {emsg}"
                '</p><pre style="font-size:80%;overflow:scroll">'
                "object={obj}\nmodel={model}"
                "</pre>"
            ).format(
                etype=type(e).__name__,
                emsg=str(e),
                obj=repr(object),
                model=repr(self.model),
            )
            base["isBroken"] = True
            return HTMLResponse(content=error_message)

    def configure_routes(self):
        self.app.mount(
            f"{ROUTE_PREFIX}/assets",
            StaticFiles(
                directory=PATH_TO_FRONTEND.joinpath("assets"), html=True
            ),
        )
        self.app.mount(
            f"{ROUTE_PREFIX}/static",
            StaticFiles(
                directory=PATH_TO_FRONTEND.joinpath("static"), html=True
            ),
        )

        @self.router.get("/api/views")
        def read_templates():
            self.templates_index = self.templates_loader.index_path(self.templates_path)
            return self.templates_index.as_dict

        @self.router.get("/api/objects/{uuid}")
        def read_object(uuid: str):
            obj = self.model.by_uuid(uuid)
            return makers.typed_object(obj)

        @self.router.get("/api/views/{template_name}")
        def read_template(template_name: str):
            template_name = urlparse.unquote(template_name)
            if not template_name in self.templates_index.flat:
                return {"error": f"Template {template_name} not found"}
            base = self.templates_index.flat[template_name]
            base.compute_instance_list(self.model)
            return base

        @self.router.get("/api/views/{template_name}/{object_id}")
        def render_template(template_name: str, object_id: str):
            content = None
            object = None
            try:
                base = self.templates[urlparse.quote(template_name)]
                template_filename = base["template"]
                # load the template file from the templates folder
                content = (self.templates_path / template_filename).read_text(
                    encoding="utf8"
                )
            except Exception as e:
                error_message = markupsafe.Markup(
                    "<p style='color:red'>Template not found: {}</p>"
                ).format(str(e))
                return HTMLResponse(content=error_message)
            if object_id == "render":
                object = None
            else:
                try:
                    object = self.model.by_uuid(object_id)
                except Exception as e:
                    error_message = markupsafe.Markup(
                        "<p style='color:red'>"
                        "Requested object not found: {}</p>"
                    ).format(str(e))
                    return HTMLResponse(content=error_message)
            return self.render_instance_page(content, base, object)

        @self.router.get("/api/model-info")
        def model_info():
            info = self.model.info
            return {
                "title": info.title,
                "revision": info.revision,
                "hash": info.rev_hash,
                "capella_version": info.capella_version,
                "branch": info.branch,
                "badge": self.model.description_badge,
            }

        @self.app.get("/metrics")
        def metrics():
            idle_time_minutes = (time.time() - self.last_interaction) / 60
            self.idle_time_gauge.set(idle_time_minutes)
            return fastapi.Response(
                content=prometheus_client.generate_latest(),
                media_type="text/plain",
            )

        @self.router.get("/{rest_of_path:path}")
        async def catch_all(request: Request, rest_of_path: str):
            del rest_of_path
            return self.app.state.templates.TemplateResponse(
                "index.html", {"request": request}
            )

        @self.app.get(f"{ROUTE_PREFIX}/api/metadata")
        async def version():
            return {"version": self.app.version}


def index_template(template, templates, templates_grouped, filename=None):
    idx = filename if filename else template["idx"]
    record = {"idx": idx, **template}
    if "category" in template:
        category = template["category"]
        if category not in templates_grouped:
            templates_grouped[category] = []
        templates_grouped[category].append(record)
    else:
        templates_grouped["other"].append(record)
    templates[idx] = template


def index_templates(
    path: pathlib.Path,
) -> tuple[dict[str, t.Any], dict[str, t.Any]]:
    templates_grouped: dict[str, t.Any] = {"other": []}
    templates: dict[str, t.Any] = {}
    for template_file in path.glob("**/*.yaml"):
        template = yaml.safe_load(template_file.read_text(encoding="utf8"))
        if "templates" in template:
            for template_def in template["templates"]:
                index_template(template_def, templates, templates_grouped)
        else:
            idx = urlparse.quote(template_file.name.replace(".yaml", ""))
            index_template(
                template, templates, templates_grouped, filename=idx
            )
    return templates_grouped, templates


