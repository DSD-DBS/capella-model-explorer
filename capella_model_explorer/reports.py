# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import re
import typing as t

import capellambse
import capellambse.model as m
import jinja2
import markupsafe
import yaml
from fasthtml import common as fh
from fasthtml import ft

import capella_model_explorer.constants as c
from capella_model_explorer import components, icons, main, state
from capella_model_explorer.types import (
    Template,
    TemplateCategory,
    TemplateScope,
)

app: fh.FastHTML
app, rt = fh.fast_app()


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


def _template_from_def(
    idx_path: pathlib.Path, category: str, template_def: dict
) -> Template:
    template_def["path"] = str(idx_path.parent / template_def["template"])
    id_ = str(idx_path.parent / template_def["template"]).replace("/", "|")
    id_ += f"|{template_def.get('id', '')}"
    template_def["id"] = id_
    template_def["category"] = category
    return Template(**template_def)


def _make_href(
    obj: m.ModelElement | m.AbstractDiagram,
) -> str | None:
    for template in state.templates:
        if "type" in dir(template.scope):
            clsname = t.cast(TemplateScope, template.scope).type
            if obj.xtype.rsplit(":", 1)[-1] == clsname:
                return main.app.url_path_for(
                    "template_page",
                    template_id=template.id,
                    model_element_uuid=obj.uuid,
                )
        if "__generic__" in template.template.stem:
            return main.app.url_path_for(
                "template_page",
                template_id=template.id,
                model_element_uuid=obj.uuid,
            )
    return fh.RedirectResponse(main.app.url_path_for("home"))


def _finalize(markup: t.Any) -> object:
    if isinstance(markup, m.AbstractDiagram):
        markup = markup.render(None)
    if isinstance(markup, capellambse.diagram.Diagram):
        svg = m.diagram.convert_format(None, "svg", markup)
        return markupsafe.Markup(
            (
                '<div class="svg-container relative inline-block cursor-pointer hover:opacity-[.5]"'
                ' onclick="openDiagramViewer(this)" >'
            )
            + svg
            + (
                '<div class="text-wrap text-center absolute bottom-0 left-0'
                " right-0 top-0 flex items-center justify-center bg-black"
                " font-sans text-2xl text-white opacity-0 transition-opacity"
                ' duration-300 hover:opacity-[.5] print:hidden" style="@media print { display: none; }">'
                "Click to enlarge"
                "</div>"
                "</div>"
                '<div class="plotly-chart fixed left-1/2 top-1/2 z-[1000] hidden h-full w-full -translate-x-1/2 -translate-y-1/2 transform bg-black p-5 shadow-lg"></div>'
            )
        )
    markup = markupsafe.escape(markup)
    return capellambse.helpers.replace_hlinks(markup, state.model, _make_href)


def _make_href_filter(obj: object) -> str | None:
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
            template = _template_from_def(idx_path, category, template_def)
            state.templates.append(template)
        _register_template_category(category)
