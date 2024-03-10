# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import operator
import pathlib
import typing as t
import urllib.parse as urlparse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import capellambse
import yaml
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment

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
        self.templates = index_templates(self.templates_path)
        self.app.templates =templates = Jinja2Templates(directory=PATH_TO_FRONTEND)

        self.configure_routes()

    def configure_routes(self):
        self.app.mount("/assets", StaticFiles(directory=PATH_TO_FRONTEND.joinpath("assets"), html=True))

        @self.app.get("/api/templates")
        def read_templates():
            # list all templates in the templates folder from .yaml
            self.templates = index_templates(self.templates_path)
            return [
                {"idx": key, **template}
                for key, template in self.templates.items()
            ]

        @self.app.get("/api/templates/{template_name}")
        def read_template(template_name: str):
            base = self.templates[urlparse.quote(template_name)]
            variable = base["variable"]
            below = variable.get("below") or None
            attr = variable.get("attr") or None
            objects = find_objects(
                self.model, variable["type"], below=below, attr=attr
            )
            base["objects"] = [
                {"idx": obj.uuid, "name": obj.name} for obj in objects
            ]
            return base

        @self.app.get("/api/templates/{template_name}/{object_id}")
        def render_template(template_name: str, object_id: str):
            base = self.templates[urlparse.quote(template_name)]
            template_filename = base["template"]
            # load the template file from the templates folder
            content = (self.templates_path / template_filename).read_text(
                encoding="utf8"
            )
            template = self.env.from_string(content)
            object = self.model.by_uuid(object_id)
            # render the template with the object
            rendered = template.render(object=object)
            return HTMLResponse(content=rendered, status_code=200)
        
        @self.app.get("/{rest_of_path:path}")
        async def catch_all(request: Request, rest_of_path: str):
            return self.app.templates.TemplateResponse("index.html", {"request": request})


def index_templates(path: pathlib.Path) -> dict[str, t.Any]:
    templates: dict[str, t.Any] = {}
    for template_file in path.glob("*.yaml"):
        template = yaml.safe_load(template_file.read_text(encoding="utf8"))
        name = template_file.name.replace(".yaml", "")
        templates[urlparse.quote(name)] = template
        # later we could add here count of objects that can be rendered
        # with this template
    return templates


def find_objects(model, obj_type, below=None, attr=None):
    if attr:
        getter = operator.attrgetter(attr)
        return getter(model)
    if below:
        getter = operator.attrgetter(below)
        return model.search(obj_type, below=getter(model))
    return model.search(obj_type)
