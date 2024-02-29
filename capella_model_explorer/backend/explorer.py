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
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from jinja2 import Environment


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
        self.env = Environment()
        self.templates = index_templates(self.templates_path)

        self.configure_routes()

    def configure_routes(self):
        @self.app.get("/")
        def read_root():
            return {"badge": self.model.description_badge}

        @self.app.get("/templates")
        def read_templates():
            # list all templates in the templates folder from .yaml
            self.templates = index_templates(self.templates_path)
            return [
                {"idx": key, **template}
                for key, template in self.templates.items()
            ]

        @self.app.get("/templates/{template_name}")
        def read_template(template_name: str):
            base = self.templates[urlparse.quote(template_name)]
            variable = base["variable"]
            objects = find_objects(
                self.model, variable["type"], variable["below"]
            )
            base["objects"] = [
                {"idx": obj.uuid, "name": obj.name} for obj in objects
            ]
            return base

        @self.app.get("/templates/{template_name}/{object_id}")
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


def index_templates(path: pathlib.Path) -> dict[str, t.Any]:
    templates: dict[str, t.Any] = {}
    for template_file in path.glob("*.yaml"):
        template = yaml.safe_load(template_file.read_text(encoding="utf8"))
        name = template.get("name", template_file.name.replace(".yaml", ""))
        templates[urlparse.quote(name)] = template
        # later we could add here count of objects that can be rendered
        # with this template
    return templates


def find_objects(model, obj_type, below=None):
    if below:
        getter = operator.attrgetter(below)
        return model.search(obj_type, below=getter(model))
    return model.search(obj_type)
