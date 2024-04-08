# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import operator
import pathlib
import typing as t
import urllib.parse as urlparse
from pathlib import Path

import capellambse
import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, TemplateSyntaxError

PATH_TO_FRONTEND = Path("./frontend/dist")


@dataclasses.dataclass
class CapellaModelExplorerBackend:
    app: FastAPI = dataclasses.field(init=False)
    env: Environment = dataclasses.field(init=False)
    templates: dict[str, t.Any] = dataclasses.field(
        init=False, default_factory=dict
    )

    templates_path: Path
    model: capellambse.MelodyModel

    def __post_init__(self):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.env = Environment()
        self.grouped_templates, self.templates = index_templates(
            self.templates_path
        )
        self.app.state.templates = Jinja2Templates(directory=PATH_TO_FRONTEND)

        self.configure_routes()

    def configure_routes(self):
        self.app.mount(
            "/assets",
            StaticFiles(
                directory=PATH_TO_FRONTEND.joinpath("assets"), html=True
            ),
        )

        @self.app.get("/api/views")
        def read_templates():
            # list all templates in the templates folder from .yaml
            self.grouped_templates, self.templates = index_templates(
                self.templates_path
            )
            return self.grouped_templates

        @self.app.get("/api/objects/{uuid}")
        def read_object(uuid: str):
            obj = self.model.by_uuid(uuid)
            return {"idx": obj.uuid, "name": obj.name, "type": obj.xtype}

        @self.app.get("/api/views/{template_name}")
        def read_template(template_name: str):
            template_name = urlparse.unquote(template_name)
            if not template_name in self.templates:
                return {"error": f"Template {template_name} not found"}
            base = self.templates[urlparse.quote(template_name)]
            base["single"] = base.get("single", False)
            filters = base.get("filters")
            variable = base["variable"]
            below = variable.get("below") or None
            attr = variable.get("attr") or None
            try:
                objects = find_objects(
                    self.model,
                    variable["type"],
                    below=below,
                    attr=attr,
                    filters=filters,
                )
                base["objects"] = [
                    {"idx": obj.uuid, "name": obj.name} for obj in objects
                ]
            except Exception as e:
                base["objects"] = []
                base["error"] = str(e)
            return base

        @self.app.get("/api/views/{template_name}/{object_id}")
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
                error_message = (
                    f"<p style='color:red'>Template not found: {str(e)}</p>"
                )
                return HTMLResponse(content=error_message)
            try:
                object = self.model.by_uuid(object_id)
            except Exception as e:
                error_message = (
                    "<p style='color:red'>Requested object "
                    f"not found: {str(e)}</p>"
                )
                return HTMLResponse(content=error_message)
            try:
                # render the template with the object
                template = self.env.from_string(content)
                rendered = template.render(object=object)
                return HTMLResponse(content=rendered, status_code=200)
            except TemplateSyntaxError as e:
                error_message = (
                    "<p style='color:red'>Template syntax error: "
                    f"{e.message}, line {e.lineno}</p>"
                )
                return HTMLResponse(content=error_message)
            except Exception as e:
                error_message = (
                    f"<p style='color:red'>Unexpected error: {str(e)}</p>"
                )
                return HTMLResponse(content=error_message)

        @self.app.get("/api/model-info")
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

        @self.app.get("/{rest_of_path:path}")
        async def catch_all(request: Request, rest_of_path: str):
            del rest_of_path
            return self.app.state.templates.TemplateResponse(
                "index.html", {"request": request}
            )


def index_templates(
    path: pathlib.Path,
) -> tuple[dict[str, t.Any], dict[str, t.Any]]:
    templates_grouped: dict[str, t.Any] = {"other": []}
    templates: dict[str, t.Any] = {}
    for template_file in path.glob("*.yaml"):
        template = yaml.safe_load(template_file.read_text(encoding="utf8"))
        idx = urlparse.quote(template_file.name.replace(".yaml", ""))
        record = {"idx": idx, **template}
        if "category" in template:
            category = template["category"]
            if category not in templates_grouped:
                templates_grouped[category] = []
            templates_grouped[category].append(record)
        else:
            templates_grouped["other"].append(record)
        templates[idx] = template
        name = template_file.name.replace(".yaml", "")
        templates[urlparse.quote(name)] = template
        # later we could add here count of objects that can be rendered
        # with this template
    return templates_grouped, templates


def find_objects(model, obj_type=None, below=None, attr=None, filters=None):
    if attr:
        getter = operator.attrgetter(attr)
        objects = getter(model)
        if objects and not isinstance(objects, list):
            objects = [objects]
    elif below and obj_type:
        getter = operator.attrgetter(below)
        objects = model.search(obj_type, below=getter(model))
    elif obj_type:
        objects = model.search(obj_type)
    else:
        raise ValueError("No search criteria provided")

    if filters:
        objects = [
            obj
            for obj in objects
            if all(
                getattr(obj, key) == value for key, value in filters.items()
            )
        ]

    return objects
