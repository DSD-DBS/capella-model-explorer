import operator
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import capellambse
import yaml
from pydantic import BaseModel, Field


def find_objects(model, obj_type=None, below=None, attr=None, filters=None):
    if attr:
        getter = operator.attrgetter(attr)
        objects = getter(model)
        if hasattr(objects, "_element"):
            objects = [objects]
        elif not isinstance(objects, capellambse.model.ElementList):
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
        objects = [
            obj
            for obj in objects
            if all(
                operator.attrgetter(key)(obj) == value
                for key, value in filters.items()
            )
        ]

    return objects


class InstanceDetails(BaseModel):
    idx: str = Field(..., title="Instance Identifier")
    name: str = Field(..., title="Instance Name")


class TemplateScope(BaseModel):
    type: str = Field(..., title="Model Element Type")
    below: Optional[str] = Field(
        None, title="Model element to search below, scope limiter"
    )
    filters: Optional[Dict[str, Any]] = Field(
        {}, title="Filters to apply to the search"
    )


class Template(BaseModel):
    idx: str = Field(..., title="Template Identifier")
    name: str = Field(..., title="Template Name")
    template: Path = Field(..., title="Template File Path")
    description: str = Field(..., title="Template Description")
    scope: TemplateScope = Field(..., title="Template Scope")

    single: Optional[bool] = Field(None, title="Single Instance Flag")
    isDocument: Optional[bool] = Field(None, title="Document Template Flag")
    isExperimental: Optional[bool] = Field(
        None, title="Experimental Template Flag"
    )
    error: Optional[str] = Field(None, title="Broken Template Flag")
    traceback: Optional[str] = Field(None, title="Template Error Traceback")
    instanceCount: Optional[int] = Field(None, title="Number of Instances")
    instanceList: Optional[List[InstanceDetails]] = Field(
        None, title="List of Instances"
    )

    def find_instances(self, model: capellambse.MelodyModel):
        if self.single:
            return [
                None,
            ]
        try:
            return find_objects(
                model,
                obj_type=self.scope.type,
                below=self.scope.below,
                attr=None,
                filters=self.scope.filters,
            )
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


def simple_object(obj) -> InstanceDetails:
    if obj.name:
        name = obj.name
    else:
        name = obj.long_name if hasattr(obj, "long_name") else "undefined"

    return InstanceDetails(idx=obj.uuid, name=str(name))


class TemplateCategory(BaseModel):
    idx: str = Field(..., title="Category Identifier")
    templates: list[Template] = Field([], title="Templates in this category")

    def __getitem__(self, template_id: str):
        return next(
            template
            for template in self.templates
            if template.idx == template_id
        )

    def __add__(self, other):
        if not isinstance(other, TemplateCategory):
            return NotImplemented

        # FIXME: What about mixing categories? Is that allowed?
        return TemplateCategory(
            idx=self.idx, templates=self.templates + other.templates
        )


class TemplateCategories(BaseModel):
    categories: dict[str, TemplateCategory] = Field(
        {}, title="Template Categories"
    )

    def __getitem__(self, category_id: str):
        return self.categories[category_id]

    def __add__(self, other: "TemplateCategories"):
        if not isinstance(other, TemplateCategories):
            return NotImplemented  # type: ignore[unreachable]

        for category_id, category in other.categories.items():
            if category_id in self.categories:
                self[category_id].templates += category.templates
            else:
                self.categories[category_id] = TemplateCategory(
                    idx=category_id, templates=category.templates
                )
        return self

    def __len__(self):
        return len(self.categories)

    @property
    def as_dict(self):
        return {
            category.idx: category.templates
            for category in self.categories.values()
        }

    @property
    def flat(self):
        return {
            template.idx: template
            for category in self.categories.values()
            for template in category.templates
        }


class TemplateLoader:
    def __init__(self, model: capellambse.MelodyModel) -> None:
        self.model = model
        self.templates = TemplateCategories(categories={})

    def index_path(self, path: Path) -> TemplateCategories:
        self.templates = TemplateCategories(categories={})  # reset templates
        for template_file in path.glob("**/*.yaml"):
            templates_data = yaml.safe_load(
                template_file.read_text(encoding="utf8")
            )
            self.templates += TemplateCategories(
                categories={
                    category["idx"]: TemplateCategory(
                        idx=category["idx"], templates=category["templates"]
                    )
                    for category in templates_data.get("categories", [])
                }
            )
        for cat in self.templates.categories.values():
            for template in cat.templates:
                template.compute_instance_count(self.model)

        return self.templates
