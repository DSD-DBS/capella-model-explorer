# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import operator
import pathlib
import re
import traceback
import typing as t

import capellambse
import capellambse.model as m
import jinja2
import markupsafe
import pydantic as p
import yaml

import capella_model_explorer.constants as c
from capella_model_explorer import app, state

SVG_WRAP_MARKUP = markupsafe.Markup(
    '<div class="svg-container relative inline-block cursor-pointer hover:opacity-[.5]"'
    ' onclick="openDiagramViewer(this)" data-diagram-title="{title}">'
    "{svg_data}"
    '<div class="text-wrap text-center absolute bottom-0 left-0'
    " right-0 top-0 flex items-center justify-center bg-black"
    " font-sans text-2xl text-white opacity-0 transition-opacity"
    ' duration-300 hover:opacity-[.5] print:hidden">'
    "Click to enlarge"
    "</div>"
    "</div>"
    '<div class="plotly-chart fixed left-1/2 top-1/2 z-[1000] hidden h-full w-full -translate-x-1/2 -translate-y-1/2 transform bg-black p-5 shadow-lg">&nbsp;</div>'
)


class Template(p.BaseModel):
    id: str = p.Field(title="Template identifier")
    name: str = p.Field(title="Template name")
    category: str = p.Field(title="Template category")
    description: str = p.Field(title="Template description")

    scope: TemplateScope | None = p.Field(default=None, title="Template scope")
    single: bool | None = p.Field(None, title="Single instance flag")
    isStable: bool | None = p.Field(None, title="Stable template flag")
    isDocument: bool | None = p.Field(None, title="Document template flag")
    isExperimental: bool | None = p.Field(
        None, title="Experimental template flag"
    )
    path: pathlib.Path = p.Field(title="Absolute file path to template")
    error: str | None = p.Field(None, title="Broken template flag")
    traceback: str | None = p.Field(None, title="Template error traceback")
    instance_count: int = p.Field(0, title="Number of instances")
    instances: list[dict] = p.Field([], title="List of instances")

    def model_post_init(self, _):
        self._compute_instances()

    def _compute_instances(self) -> None:
        if self.single:
            self.instance_count = 1
            return
        try:
            if self.scope is not None:
                self.instances = [
                    self._simple_object(obj)
                    for obj in self._find_objects(
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

    def _find_objects(
        self, obj_type=None, below=None, attr=None, filters=None
    ):
        if attr:
            getter = operator.attrgetter(attr)
            objects = getter(state.model)
            if hasattr(objects, "_element"):
                objects = [objects]
            elif not isinstance(objects, m.ElementList):
                raise ValueError(
                    f"Expected a list of model objects or a single model object"
                    f" for {attr!r} of the model, got {objects!r}"
                )
        elif below and obj_type:
            getter = operator.attrgetter(below)
            objects = state.model.search(obj_type, below=getter(state.model))
        elif obj_type:
            objects = state.model.search(obj_type)
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

    def _simple_object(self, obj) -> dict[str, t.Any]:
        if not obj:
            return {}
        if obj.name:
            name = obj.name
        else:
            name = obj.long_name if hasattr(obj, "long_name") else "undefined"

        return {"uuid": obj.uuid, "name": str(name)}


class TemplateScope(p.BaseModel):
    type: str | None = p.Field(None, title="Model Element Type")
    below: t.Literal["oa", "sa", "la", "pa"] | None = p.Field(
        None, title="Model element to search below, scope limiter"
    )
    filters: dict[str, t.Any] | None = p.Field(
        {}, title="Filters to apply to the search"
    )

    def applies_to(self, obj: m.ModelElement | m.AbstractDiagram) -> bool:
        if obj.xtype.rsplit(":", 1)[-1] != self.type:
            return False

        if (
            (self.below == "oa" and obj.layer != obj._model.oa)
            or (self.below == "sa" and obj.layer != obj._model.sa)
            or (self.below == "la" and obj.layer != obj._model.la)
            or (self.below == "pa" and obj.layer != obj._model.pa)
        ):
            return False

        for key, value in (self.filters or {}).items():
            try:
                actual = getattr(obj, key)
            except AttributeError:
                return False
            if actual != value:
                return False

        return True


class TemplateCategory(p.BaseModel):
    idx: str = p.Field(title="Category Identifier")
    templates: list[Template] = p.Field(
        default_factory=list, title="Templates in this category"
    )


def template_by_id(id_: str) -> Template | None:
    for template in state.templates:
        if template.id == id_:
            return template
    return None


def _register_template_category(category: str) -> None:
    state.template_categories.append(
        TemplateCategory(
            idx=category,
            templates=[t for t in state.templates if t.category == category],
        )
    )


def _make_href(
    obj: m.ModelElement | m.AbstractDiagram,
) -> str | None:
    generic_template: Template | None = None
    for template in state.templates:
        if template.path.name.startswith("__generic__"):
            generic_template = template
            continue

        if template.single:
            continue

        if template.scope and not template.scope.applies_to(obj):
            continue

        return app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=obj.uuid,
        )

    if generic_template is None:
        return None
    return app.app.url_path_for(
        "template_page",
        template_id=generic_template.id,
        model_element_uuid=obj.uuid,
    )


def finalize(markup: t.Any) -> object:
    if isinstance(markup, m.AbstractDiagram):
        svg = markupsafe.Markup(markup.render("svg"))
        return SVG_WRAP_MARKUP.format(svg_data=svg, title=markup.name)

    if isinstance(markup, capellambse.diagram.Diagram):
        svg = markupsafe.Markup(m.diagram.convert_format(None, "svg", markup))
        return SVG_WRAP_MARKUP.format(svg_data=svg, title=markup.name)

    markup = markupsafe.escape(markup)
    return capellambse.helpers.replace_hlinks(markup, state.model, _make_href)


def make_href_filter(obj: object) -> str | None:
    if jinja2.is_undefined(obj) or obj is None:
        return "#"

    if isinstance(obj, m.ElementList):
        raise TypeError("Cannot make an href to a list of elements")
    if not isinstance(obj, m.ModelElement | m.AbstractDiagram):
        raise TypeError(f"Expected a model object, got {obj!r}")
    try:
        state.model.by_uuid(obj.uuid)
    except KeyError:
        return "#"
    return _make_href(obj)


def load_templates() -> None:
    for idx_path in sorted(c.TEMPLATES_DIR.glob("**/*.yaml")):
        category = re.sub(r"^[A-Za-z0-9]{2}-", "", idx_path.parent.name)
        template_defs = yaml.safe_load(idx_path.read_text(encoding="utf8"))
        for template_def in template_defs:
            template_def["category"] = category
            template_def["path"] = str(
                idx_path.parent / template_def["template"]
            )
            template = Template(**template_def)
            state.templates.append(template)
        _register_template_category(category)
