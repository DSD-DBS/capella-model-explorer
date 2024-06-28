from pydantic import BaseModel, Field
from pathlib import Path
from typing import List, Dict, Optional, Any
import yaml
import capellambse
import operator
from capella_model_explorer.backend import makers
import traceback


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
                getattr(obj, key) == value for key, value in filters.items()
            )
        ]

    return objects



class InstanceDetails(BaseModel):
    idx: str = Field(..., title="Instance Identifier")
    name: str = Field(..., title="Instance Name")

class TemplateScope(BaseModel):
    type: str = Field(..., title="Model Element Type")
    below: Optional[str] = Field(None, title="Model element to search below, scope limiter")
    filters: Optional[Dict[str, Any]] = Field({}, title="Filters to apply to the search")

class Template(BaseModel):
    idx: str = Field(..., title="Template Identifier")
    name: str = Field(..., title="Template Name")
    template: Path = Field(..., title="Template File Path")
    description: str = Field(..., title="Template Description")
    scope: TemplateScope = Field(..., title="Template Scope")

    single: Optional[bool] = Field(None, title="Single Instance Flag")
    isDocument: Optional[bool] = Field(None, title="Document Template Flag")
    isExperimental: Optional[bool] = Field(None, title="Experimental Template Flag")
    error: Optional[str] = Field(None, title="Broken Template Flag")
    traceback: Optional[str] = Field(None, title="Template Error Traceback")
    instanceCount: Optional[int] = Field(None, title="Number of Instances")
    instanceList: Optional[List[InstanceDetails]] = Field(None, title="List of Instances")

    def find_instances(self, model: capellambse.MelodyModel):
        if self.single:
            return [None, ]
        try:
            return find_objects(model, obj_type=self.scope.type, below=self.scope.below, attr=None, filters=self.scope.filters)
        except Exception as e:
            self.error = f"Template scope error: {e}"
            self.traceback = traceback.format_exc()
            return []

    def compute_instance_count(self, model: capellambse.MelodyModel):
        self.instanceCount = len(self.find_instances(model))

    def compute_instance_list(self, model: capellambse.MelodyModel):
        self.instanceList =  [
                    makers.simple_object(obj) for obj in self.find_instances(model)
                ]


class TemplateCategory(BaseModel):
    idx: str = Field(..., title="Category Identifier")
    templates: List[Template] = Field([], title="Templates in this category")

    def __getitem__(self, template_id: str):
        return self.by_id(template_id)
    
    def __add__(self, other):
        if not isinstance(other, TemplateCategory):
            return NotImplemented
        return TemplateCategory(templates=self.templates + other.templates)
    
    

class TemplateCategories(BaseModel):
    categories: List[TemplateCategory] = Field([], title="Template Categories")

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
                    if template.idx not in [t.idx for t in self[category_id].templates]:
                        self[category_id].templates.append(template)
            else:
                self.categories.append(TemplateCategory(idx=category_id, templates=category.templates))
        return self
    
    def __len__(self):
        return len(self.categories)
    
    @property
    def as_dict(self):
        return {category.idx: category.templates for category in self.categories}

    @property
    def flat(self):
        return {
                template.idx: template 
                for category in self.categories
                for template in category.templates
            }

class TemplateLoader():
    def __init__(self, model: capellambse.MelodyModel) -> None:
        self.model = model
        self.templates = TemplateCategories()

    def index_path(self, path: Path) -> TemplateCategories:
        self.templates = TemplateCategories(categories=[])  # reset templates
        for template_file in path.glob("**/*.yaml"):
            templates_data = yaml.safe_load(template_file.read_text(encoding="utf8"))
            if "categories" in templates_data:
                self.templates += TemplateCategories(**templates_data)
        for cat in self.templates.categories:
            for template in cat.templates:
                template.compute_instance_count(self.model)
        
        return self.templates

    
