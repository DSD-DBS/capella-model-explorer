# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import operator
import traceback
from pathlib import Path
from typing import Any

import capellambse
import capellambse.model as m
import yaml
from pydantic import BaseModel, Field


def simple_object(obj) -> dict[str, Any]:
    if not obj:
        return {}
    if obj.name:
        name = obj.name
    else:
        name = obj.long_name if hasattr(obj, "long_name") else "undefined"

    return {"idx": obj.uuid, "name": str(name)}


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


class InstanceDetails(BaseModel):
    idx: str = Field(..., title="Instance Identifier")
    name: str = Field(..., title="Instance Name")


class TemplateScope(BaseModel):
    type: str | None = Field(None, title="Model Element Type")
    below: str | None = Field(
        None, title="Model element to search below, scope limiter"
    )
    filters: dict[str, Any] | None = Field(
        {}, title="Filters to apply to the search"
    )


class Template(BaseModel):
    idx: str = Field(..., title="Template Identifier")
    name: str = Field(..., title="Template Name")
    template: Path = Field(..., title="Template File Path")
    description: str = Field(..., title="Template Description")

    scope: TemplateScope | None = Field(
        default_factory=dict, title="Template Scope"
    )
    single: bool | None = Field(None, title="Single Instance Flag")
    isStable: bool | None = Field(None, title="Stable Template Flag")
    isDocument: bool | None = Field(None, title="Document Template Flag")
    isExperimental: bool | None = Field(
        None, title="Experimental Template Flag"
    )
    error: str | None = Field(None, title="Broken Template Flag")
    traceback: str | None = Field(None, title="Template Error Traceback")
    instanceCount: int | None = Field(None, title="Number of Instances")
    instanceList: list[dict] | None = Field(None, title="List of Instances")

    def find_instances(self, model: capellambse.MelodyModel):
        if self.single:
            return [
                None,
            ]
        try:
            if self.scope is not None:
                return find_objects(
                    model,
                    obj_type=self.scope.type,
                    below=self.scope.below,
                    attr=None,
                    filters=self.scope.filters,
                )
            return []
        except Exception as e:
            self.error = f"Template scope error: {e}"
            self.traceback = traceback.format_exc()
            return []

    def compute_instance_count(self, model: capellambse.MelodyModel):
        self.instanceCount = len(self.find_instances(model))

    def compute_instance_list(self, model: capellambse.MelodyModel):
        self.instanceList = [
            simple_object(obj) for obj in self.find_instances(model)
        ]


class TemplateCategory(BaseModel):
    idx: str = Field(..., title="Category Identifier")
    templates: list[Template] = Field(
        default_factory=list, title="Templates in this category"
    )

    def __add__(self, other):
        if not isinstance(other, TemplateCategory):
            return NotImplemented
        return TemplateCategory(
            idx=self.idx, templates=self.templates + other.templates
        )


class TemplateCategories(BaseModel):
    categories: list[TemplateCategory] = Field(
        default_factory=list, title="Template Categories"
    )

    def __getitem__(self, category_id: str):
        results = [cat for cat in self.categories if cat.idx == category_id]
        return results[0] if results else None

    def __add__(self, other):
        if not isinstance(other, TemplateCategories):
            return NotImplemented
        for category in other.categories:
            category_id = category.idx
            if category_id in [cat.idx for cat in self.categories]:
                for template in other[category_id].templates:
                    if template.idx not in [
                        t.idx for t in self[category_id].templates
                    ]:
                        self[category_id].templates.append(template)
            else:
                self.categories.append(
                    TemplateCategory(
                        idx=category_id, templates=category.templates
                    )
                )
        return self

    def __len__(self):
        return len(self.categories)

    @property
    def as_dict(self):
        return {
            category.idx: category.templates for category in self.categories
        }

    @property
    def flat(self):
        return {
            template.idx: template
            for category in self.categories
            for template in category.templates
        }


class TemplateLoader:
    def __init__(self, model: capellambse.MelodyModel) -> None:
        self.model = model
        self.templates = TemplateCategories()

    def index_path(self, path: Path) -> TemplateCategories:
        self.templates = TemplateCategories()  # reset templates
        for template_file in path.glob("**/*.yaml"):
            templates_data = yaml.safe_load(
                template_file.read_text(encoding="utf8")
            )
            if "categories" in templates_data:
                self.templates += TemplateCategories(**templates_data)
        for cat in self.templates.categories:
            for template in cat.templates:
                template.compute_instance_count(self.model)

        return self.templates
