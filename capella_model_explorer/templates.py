# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import operator
import pathlib
import re
import traceback
import typing as t

import capellambse.model as m
import pydantic as p
import yaml

from capella_model_explorer import state
from capella_model_explorer.types import TemplateDef


def simple_object(obj) -> dict[str, t.Any]:
    if not obj:
        return {}
    if obj.name:
        name = obj.name
    else:
        name = obj.long_name if hasattr(obj, "long_name") else "undefined"

    return {"uuid": obj.uuid, "name": str(name)}


class TemplateScope(p.BaseModel):
    type: str | None = p.Field(None, title="Model Element Type")
    below: str | None = p.Field(
        None, title="Model element to search below, scope limiter"
    )
    filters: dict[str, t.Any] | None = p.Field(
        {}, title="Filters to apply to the search"
    )


class Template(p.BaseModel):
    id: str = p.Field(title="Template identifier")
    name: str = p.Field(title="Template name")
    category: str = p.Field(title="Template category")
    template: pathlib.Path = p.Field(title="Index-relative file path")
    description: str = p.Field(title="Template description")

    scope: TemplateScope | None = p.Field(default=None, title="Template scope")
    single: bool | None = p.Field(None, title="Single instance flag")
    isStable: bool | None = p.Field(None, title="Stable template flag")
    isDocument: bool | None = p.Field(None, title="Document template flag")
    isExperimental: bool | None = p.Field(
        None, title="Experimental template flag"
    )
    path: pathlib.Path = p.Field(title="Application-relative file path")
    error: str | None = p.Field(None, title="Broken template flag")
    traceback: str | None = p.Field(None, title="Template error traceback")
    instance_count: int = p.Field(0, title="Number of instances")
    instances: list[dict] = p.Field([], title="List of instances")

    def model_post_init(self, _):
        self.compute_instances()

    def compute_instances(self) -> None:
        if self.single:
            self.instance_count = 1
            return
        try:
            if self.scope is not None:
                self.instances = [
                    simple_object(obj)
                    for obj in find_objects(
                        state.model,
                        obj_type=self.scope.type,
                        below=self.scope.below,
                        attr=None,
                        filters=self.scope.filters,
                    )
                ]
            self.instance_count = len(self.instances)
        except Exception as e:
            self.error = f"Template scope error: {e}"
            self.traceback = traceback.format_exc()


class TemplateCategory(p.BaseModel):
    idx: str = p.Field(..., title="Category Identifier")
    templates: list[Template] = p.Field(
        default_factory=list, title="Templates in this category"
    )


def find_objects(model, obj_type=None, below=None, attr=None, filters=None):
    if attr:
        getter = operator.attrgetter(attr)
        objects = getter(model)
        if hasattr(objects, "_element"):
            objects = [objects]
        elif not isinstance(objects, m.ElementList):
            raise ValueError(
                f"Expected a list of model objects or a single model object"
                f" for {attr!r} of the model, got {objects!r}"
            )
    elif below and obj_type:
        getter = operator.attrgetter(below)
        objects = model.search(obj_type, below=getter(model))
    elif obj_type:
        objects = model.search(obj_type)
    else:
        raise ValueError("No search criteria provided")

    if filters:
        filtered = []
        for object in objects:
            for attr_key, filter in filters.items():
                attr = getattr(object, attr_key)
                if filter == "not_empty":
                    if attr:
                        filtered.append(object)
                elif attr == filter:
                    filtered.append(object)
        objects = filtered
    return objects


def compute_instance_count(template_def: TemplateDef) -> int:
    if template_def.get("single"):
        return 1
    scope: dict[str, str] = template_def.get("scope", {})  # type: ignore
    if scope:
        return len(
            find_objects(
                state.model,
                obj_type=scope.get("type", ""),
                below=scope.get("below", ""),
                attr=None,
                filters=scope.get("filters", ""),
            )
        )
    return 0


def template_by_id(id_: str) -> Template | None:
    for template in state.templates:
        if template.id == id_:
            return template
    return None


def load() -> None:
    for idx_path in sorted(state.templates_path.glob("**/*.yaml")):
        category = re.sub(r"^[A-Za-z0-9]{2}-", "", idx_path.parent.name)
        template_defs = yaml.safe_load(idx_path.read_text(encoding="utf8"))
        for template_def in template_defs:
            template_def["path"] = str(
                idx_path.parent / template_def["template"]
            )
            id_ = str(idx_path.parent / template_def["template"]).replace(
                "/", "|"
            )
            id_ += f"|{template_def.get('id', '')}"
            template_def["id"] = id_
            template_def["category"] = category
            state.templates.append(Template(**template_def))
        state.template_categories.append(
            TemplateCategory(
                idx=category,
                templates=[
                    t for t in state.templates if t.category == category
                ],
            )
        )
