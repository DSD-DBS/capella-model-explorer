from pydantic import BaseModel, Field
from pathlib import Path
from typing import List, Dict, Optional
import yaml
import capellambse


class TemplateScope(BaseModel):
    type: str = Field(..., title="Model Element Type")
    below: Optional[str] = Field(None, title="Model element to search below, scope limiter")

class Template(BaseModel):
    idx: str = Field(..., title="Template Identifier")
    name: str = Field(..., title="Template Name")
    template: Path = Field(..., title="Template File Path")
    description: str = Field(..., title="Template Description")
    scope: TemplateScope = Field(..., title="Template Scope")

    @property
    def instances(self):
        # eval the scope and return object list
        pass


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
        return [cat for cat in self.categories if cat.idx == category_id].first()

    def __add__(self, other):
        if not isinstance(other, TemplateCategories):
            return NotImplemented
        for category in other.categories:
            category_id = category.idx
            if category_id in [cat.idx for cat in self.categories]:
                self.categories[category_id].templates += category.templates
            else:
                self.categories.append(TemplateCategory(idx=category_id, templates=category.templates))
        return self
    
    def __len__(self):
        return len(self.categories)

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
        self.templates = TemplateCategories()  # reset templates
        for template_file in path.glob("**/*.yaml"):
            with template_file.open() as f:
                templates_data = yaml.safe_load(template_file.read_text(encoding="utf8"))
                if "categories" in templates_data:
                    self.templates += TemplateCategories(**templates_data)
        return self.templates
    
