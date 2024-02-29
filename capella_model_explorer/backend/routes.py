# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import operator
import pathlib
import typing as t
import urllib.parse as urlparse

import yaml
from fastapi.responses import HTMLResponse

from . import explorer


def configure_routes(backend: explorer.CapellaModelExplorerBackend):
    @backend.app.get("/")
    def read_root():
        return {"badge": backend.model.description_badge}

    @backend.app.get("/templates")
    def read_templates():
        # list all templates in the templates folder from .yaml
        backend.templates = index_templates(backend.templates_path)
        return [
            {"idx": key, **backend.templates[key]} for key in backend.templates
        ]

    @backend.app.get("/templates/{template_name}")
    def read_template(template_name: str):
        base = backend.templates[urlparse.quote(template_name)]
        variable = base["variable"]
        objects = find_objects(
            backend.model, variable["type"], variable["below"]
        )
        base["objects"] = [
            {"idx": obj.uuid, "name": obj.name} for obj in objects
        ]
        return base

    @backend.app.get("/templates/{template_name}/{object_id}")
    def render_template(template_name: str, object_id: str):
        base = backend.templates[urlparse.quote(template_name)]
        template_filename = base["template"]
        # load the template file from the templates folder
        content = (backend.templates_path / template_filename).read_text(
            encoding="utf8"
        )
        template = backend.env.from_string(content)
        object = backend.model.by_uuid(object_id)
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
