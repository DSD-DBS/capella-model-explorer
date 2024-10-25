# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import logging
import os
import pathlib
import time
import traceback
import typing as t
import urllib.parse as urlparse
from pathlib import Path

import capellambse
import capellambse.model as m
import fastapi
import markupsafe
import prometheus_client
import yaml
from fastapi import APIRouter, FastAPI, HTTPException, Request
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
from pydantic import BaseModel

from capella_model_explorer.backend import model_diff
from capella_model_explorer.backend import templates as tl

from . import __version__

esc = markupsafe.escape

PATH_TO_FRONTEND = Path("./frontend/dist")
ROUTE_PREFIX = os.getenv("ROUTE_PREFIX", "")
LOGGER = logging.getLogger(__name__)


class CommitRange(BaseModel):
    head: str
    prev: str


class ObjectDiffID(BaseModel):
    uuid: str


@dataclasses.dataclass
class CapellaModelExplorerBackend:
    app: FastAPI = dataclasses.field(init=False)
    env: Environment = dataclasses.field(init=False)
    templates: dict[str, t.Any] = dataclasses.field(
        init=False, default_factory=dict
    )
    templates_loader: tl.TemplateLoader = dataclasses.field(init=False)

    templates_path: Path
    model: capellambse.MelodyModel

    templates_index: tl.TemplateCategories | None = dataclasses.field(
        init=False
    )

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
        self.templates_loader = tl.TemplateLoader(self.model)
        self.env = Environment(loader=FileSystemLoader(self.templates_path))
        self.env.finalize = self.__finalize
        self.env.filters["make_href"] = self.__make_href_filter
        self.app.state.templates = Jinja2Templates(directory=PATH_TO_FRONTEND)
        self.configure_routes()
        self.app.include_router(self.router)
        self.idle_time_gauge = prometheus_client.Gauge(
            "idletime_minutes",
            "Time in minutes since the last user interaction",
        )
        self.last_interaction = time.time()
        self.templates_index = self.templates_loader.index_path(
            self.templates_path
        )
        self.diff = {}
        self.object_diff = {}

        @self.app.middleware("http")
        async def update_last_interaction_time(request: Request, call_next):
            if request.url.path not in ("/metrics", "/favicon.ico"):
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

        if isinstance(obj, m.ElementList):
            raise TypeError("Cannot make an href to a list of elements")
        if not isinstance(obj, m.ModelElement | m.AbstractDiagram):
            raise TypeError(f"Expected a model object, got {obj!r}")

        try:
            self.model.by_uuid(obj.uuid)
        except KeyError:
            return "#"

        return self.__make_href(obj)

    def __make_href(
        self, obj: m.ModelElement | m.AbstractDiagram
    ) -> str | None:
        if self.templates_index is None:
            return None

        for idx, template in self.templates_index.flat.items():
            if "type" in dir(template.scope):
                clsname = template.scope.type
                if obj.xtype.rsplit(":", 1)[-1] == clsname:
                    return f"{ROUTE_PREFIX}/{idx}/{obj.uuid}"
        return f"{ROUTE_PREFIX}/__generic__/{obj.uuid}"

    def render_instance_page(self, template_text, base, object=None):
        try:
            # render the template with the object
            template = self.env.from_string(template_text)
            rendered = template.render(
                object=object,
                model=self.model,
                diff_data=self.diff,
                object_diff=self.object_diff,
            )
            return HTMLResponse(content=rendered, status_code=200)
        except TemplateSyntaxError as e:
            error_message = markupsafe.Markup(
                "<p style='color:red'>Template syntax error: {}, line {}</p>"
            ).format(e.message, e.lineno)
            base.error = error_message
            print(base)
            return HTMLResponse(content=error_message)
        except Exception as e:
            LOGGER.exception("Error rendering template")
            trace = markupsafe.escape(traceback.format_exc())
            error_message = markupsafe.Markup(
                '<p style="color:red">'
                f"Unexpected error: {type(e).__name__}: {e}"
                '</p><pre style="font-size:80%;overflow:scroll">'
                f"object={object!r}\nmodel={self.model!r}"
                f"\n\n{trace}"
                "</pre>"
            )
            return HTMLResponse(content=error_message)

    def configure_routes(self):  # noqa: C901
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
            self.templates_index = self.templates_loader.index_path(
                self.templates_path
            )
            return self.templates_index.as_dict

        @self.router.get("/api/objects/{uuid}")
        def read_object(uuid: str):
            obj = self.model.by_uuid(uuid)
            details = tl.simple_object(obj)
            return {
                "idx": details["idx"],
                "name": details["name"],
                "type": obj.xtype,
            }

        @self.router.get("/api/views/{template_name}")
        def read_template(template_name: str):
            template_name = urlparse.unquote(template_name)
            if (
                self.templates_index is None
                or template_name not in self.templates_index.flat
            ):
                return {
                    "error": (
                        f"Template {template_name} not found"
                        " or templates index not initialized"
                    )
                }
            base = self.templates_index.flat[template_name]
            base.compute_instance_list(self.model)
            return base

        @self.router.get("/api/views/{template_name}/{object_id}")
        def render_template(template_name: str, object_id: str):
            content = None
            object = None
            try:
                template_name = urlparse.unquote(template_name)
                if (
                    self.templates_index is None
                    or template_name not in self.templates_index.flat
                ):
                    return {"error": f"Template {template_name} not found"}
                base = self.templates_index.flat[template_name]
                template_filename = base.template
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
            resinfo = info.resources["\x00"]
            return {
                "title": info.title,
                "revision": resinfo.revision,
                "hash": resinfo.rev_hash,
                "capella_version": info.capella_version,
                "branch": resinfo.branch,
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

        @self.router.get("/api/metadata")
        async def version():
            return {"version": self.app.version}

        @self.router.post("/api/compare")
        async def post_compare(commit_range: CommitRange):
            try:
                self.diff = model_diff.get_diff_data(
                    self.model, commit_range.head, commit_range.prev
                )
                self.diff["lookup"] = create_diff_lookup(self.diff["objects"])
                if self.diff["lookup"]:
                    return {"success": True}
                return {"success": False, "error": "No model changes to show"}
            except Exception as e:
                LOGGER.exception("Failed to compare versions")
                return {"success": False, "error": str(e)}

        @self.router.post("/api/object-diff")
        async def post_object_diff(object_id: ObjectDiffID):
            if object_id.uuid not in self.diff["lookup"]:
                raise HTTPException(status_code=404, detail="Object not found")

            self.object_diff = self.diff["lookup"][object_id.uuid]
            return {"success": True}

        @self.router.get("/api/commits")
        async def get_commits():
            try:
                return model_diff.populate_commits(self.model)
            except Exception as e:
                return {"error": str(e)}

        @self.router.get("/api/diff")
        async def get_diff():
            if self.diff:
                return self.diff
            return {
                "error": "No data available. Please compare two commits first."
            }

        @self.router.get("/{rest_of_path:path}")
        async def catch_all(request: Request, rest_of_path: str):
            del rest_of_path
            return self.app.state.templates.TemplateResponse(
                "index.html", {"request": request}
            )


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


def create_diff_lookup(data, lookup=None):
    if lookup is None:
        lookup = {}
    try:
        if isinstance(data, dict):
            for _, obj in data.items():
                if "uuid" in obj:
                    lookup[obj["uuid"]] = {
                        "uuid": obj["uuid"],
                        "display_name": obj["display_name"],
                        "change": obj["change"],
                        "attributes": obj["attributes"],
                    }
                if children := obj.get("children"):
                    create_diff_lookup(children, lookup)
    except Exception:
        LOGGER.exception("Cannot create diff lookup")
    return lookup
