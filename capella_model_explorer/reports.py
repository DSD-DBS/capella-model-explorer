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
from fasthtml import common as fh
from fasthtml import ft

import capella_model_explorer.constants as c
from capella_model_explorer import app, components, icons, state

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
    below: str | None = p.Field(
        None, title="Model element to search below, scope limiter"
    )
    filters: dict[str, t.Any] | None = p.Field(
        {}, title="Filters to apply to the search"
    )


class TemplateCategory(p.BaseModel):
    idx: str = p.Field(title="Category Identifier")
    templates: list[Template] = p.Field(
        default_factory=list, title="Templates in this category"
    )


def home() -> tuple[ft.Title, ft.Main]:
    """Show reports home/ landing page with all reports in categories."""
    page_content = (
        ft.Main(
            ft.Div(
                components.model_information(),
                components.reports_page(),
                cls="flex flex-col space-y-4 place-items-center mb-4",
            ),
            ft.Div(
                ft.A(
                    ft.Div("Contribute on GitHub"),
                    icons.github_logo(),
                    href="https://github.com/DSD-DBS/capella-model-explorer",
                    target="_blank",
                    cls=(
                        "dark:text-neutral-300",
                        "flex",
                        "hover:underline",
                        "max-w-fit",
                        "place-items-center",
                        "space-x-2",
                    ),
                ),
                cls="w-full pl-8 h-8 py-2 my-8",
            ),
            cls="grow w-full overflow-y-auto place-items-center",
        ),
    )
    return components.application_shell(page_content)


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
    for template in state.templates:
        if template.scope is not None:
            clsname = template.scope.type
            if obj.xtype.rsplit(":", 1)[-1] == clsname:
                return app.app.url_path_for(
                    "template_page",
                    template_id=template.id,
                    model_element_uuid=obj.uuid,
                )
        if "__generic__" in template.path.stem:
            return app.app.url_path_for(
                "template_page",
                template_id=template.id,
                model_element_uuid=obj.uuid,
            )
    return fh.RedirectResponse(app.app.url_path_for("home"))


def finalize(markup: t.Any) -> object:
    if isinstance(markup, m.AbstractDiagram):
        markup = markup.render(None)
    if isinstance(markup, capellambse.diagram.Diagram):
        svg = m.diagram.convert_format(None, "svg", markup)
        return markupsafe.Markup(
            SVG_WRAP_MARKUP.format(
                svg_data=markupsafe.Markup(svg),
                title=markup.name,
            )
        )
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
