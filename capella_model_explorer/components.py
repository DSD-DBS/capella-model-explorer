# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import json
import pathlib
import typing as t

import capellambse
import capellambse_context_diagrams
from fasthtml import components as fc
from fasthtml import ft, svg

import capella_model_explorer
from capella_model_explorer import app, core, icons, reports, state


def application_shell(
    *content: t.Any,
    template: reports.Template | None,
    element: str | None,
) -> tuple[ft.Title, ft.Main]:
    return (
        ft.Title(f"{state.model.name} - Model Explorer"),
        ft.Div(
            navbar(template, element),
            ft.Main(
                *content,
                id="root",
                cls=(
                    "grow",
                    "w-full",
                    "overflow-y-auto",
                ),
            ),
            # placeholder for script injection per outerHTML swap
            ft.Script(id="script"),
            cls=(
                "bg-neutral-100",
                "dark:bg-neutral-900",
                "flex",
                "flex-col",
                "h-screen",
                "min-h-screen",
                "print:h-auto",
                "print:min-h-auto",
            ),
        ),
    )


def breadcrumb(*, label: str, url: str) -> ft.Li:
    return (
        ft.Li(
            ft.Div(
                svg.Svg(
                    svg.Path(d="M.293 0l22 22-22 22h1.414l22-22-22-22H.293z"),
                    viewbox="0 0 24 44",
                    preserveaspectratio="none",
                    aria_hidden="true",
                    cls="h-full w-6 stroke-1 stroke-primary-400 dark:stroke-neutral-700",
                ),
                ft.A(
                    label,
                    href=url,
                    cls=(
                        "dark:hover:text-neutral-100",
                        "dark:text-neutral-400",
                        "font-medium",
                        "ml-4",
                        "hover:text-neutral-50",
                        "text-neutral-300",
                        "text-sm",
                    ),
                ),
                cls="flex items-center",
            ),
            cls="flex",
        ),
    )


def breadcrumbs(
    template: reports.Template | None = None,
    element_id: str | None = None,
    /,
    *,
    oob: bool = False,
) -> ft.Nav:
    components = []

    if template is not None:
        components.append(
            ft.Li(
                ft.Div(
                    ft.A(
                        icons.home(),
                        ft.Span("Home", cls="sr-only"),
                        href=app.app.url_path_for("main_home"),
                        hx_get=app.app.url_path_for("main_home"),
                        hx_target="#root",
                        hx_push_url="true",
                    ),
                    cls="flex items-center",
                ),
                cls="flex",
            )
        )

        url = app.app.url_path_for("template_page", template_id=template.id)
        components.append(breadcrumb(label=template.name, url=url))

    if element_id is not None:
        assert template is not None, "Model element passed without template"
        element = state.model.by_uuid(element_id)
        url = app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=element_id,
        )
        components.append(breadcrumb(label=element.name, url=url))

    return ft.Nav(
        ft.Ol(
            *components,
            role="list",
            cls="flex space-x-4 rounded-md px-6",
        ),
        id="breadcrumbs",
        aria_label="Breadcrumb",
        cls="flex grow",
        **({"hx_swap_oob": "true"} if oob else {}),
    )


def model_information() -> ft.Div:
    """Render the model information including the badge."""
    badge = "data:image/svg+xml;base64," + base64.standard_b64encode(
        state.model.description_badge.encode("utf-8")
    ).decode("ascii")
    return ft.Div(
        ft.H1(state.model.name, cls="text-xl"),
        ft.P(
            f"Capella version: {state.model.info.capella_version}",
        ),
        ft.Img(
            src=badge,
            alt="Model description badge",
            cls="object-scale-down",
        ),
        cls=(
            "colors-surface",
            "max-w-full",
            "m-2",
            "mt-4",
            "p-4",
            "rounded-lg",
            "text-center",
        ),
    )


def model_object_button(
    *,
    template: reports.Template,
    element: dict[t.Any, t.Any],
    selected: bool,
):
    if state.show_uuids:
        uuid = ft.Span(element["uuid"], slot="description")
    else:
        uuid = None
    return fc.Mdui_list_item(
        element["name"],
        uuid,
        id=f"model-element-{element['uuid']}",
        rounded=True,
        active=selected,
        hx_trigger="click",
        hx_get=app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=element["uuid"],
        ),
        hx_push_url="true",
        hx_target="#template_container",
    )


def model_elements_list(
    *,
    template: reports.Template,
    selected_id: str | None,
    search: str = "",
):
    search_words = search.lower().split()
    model_elements = [
        obj
        for obj in sorted(template.instances, key=lambda x: x["name"])
        if (n := obj["name"].lower()) and all(w in n for w in search_words)
    ]
    return fc.Mdui_list(
        *(
            model_object_button(
                template=template,
                element=el,
                selected=el["uuid"] == selected_id,
            )
            for el in model_elements
        )
    )


def navbar(template: reports.Template | None, element: str | None) -> ft.Nav:
    return ft.Nav(
        breadcrumbs(template, element),
        fc.Mdui_button_icon(
            icon="print--outlined",
            onclick="window.print();",
            title="Print report",
            cls=(
                "text-neutral-300",
                "hover:text-neutral-50",
                "dark:text-neutral-400",
                "dark:hover:text-neutral-100",
            ),
        ),
        fc.Mdui_button_icon(
            icon="brightness_auto--outlined",
            id="dark-mode-button",
            title="Toggle dark mode",
            cls=(
                "text-neutral-300",
                "hover:text-neutral-50",
                "dark:text-neutral-400",
                "dark:hover:text-neutral-100",
            ),
        ),
        id="page-header",
        cls=(
            "bg-primary-500",
            "dark:bg-neutral-800",
            "dark:border-b",
            "dark:border-neutral-700",
            "flex",
            "gap-2",
            "h-12",
            "max-h-12",
            "min-h-12",
            "print:hidden",
            "px-4",
            "py-0",
            "sticky",
            "top-0",
            "w-full",
            "z-50",
        ),
    )


def report_placeholder(
    template: reports.Template | None,
    model_element_uuid: str | None,
) -> t.Any:
    if template is None:
        ph_content = ft.Div(
            ft.Span(
                "Select a model element.",
                cls="text-slate-600 dark:text-slate-500 p-4 italic m-auto",
            ),
            cls="flex justify-center place-items-center h-full w-full",
        )

    else:
        if model_revision := state.model.info.resources["\x00"].rev_hash:
            render_environment = json.dumps(
                {
                    "model-explorer-version": capella_model_explorer.__version__,
                    "capellambse-version": capellambse.__version__,
                    "ctx-diags-version": capellambse_context_diagrams.__version__,
                    "template-hash": core.compute_file_hash(
                        str(template.path)
                    ),
                    "model-revision": model_revision,
                }
            )
            hx_headers = json.dumps({"Render-Environment": render_environment})
        else:
            hx_headers = None

        ph_content = ft.Div(
            icons.spinner(),
            hx_trigger="load",
            hx_get=app.rendered_report.to(
                template_id=template.id,
                model_element_uuid=model_element_uuid,
            ),
            hx_headers=hx_headers,
            hx_target="#template_container",
            cls="flex justify-center place-items-center h-full w-full",
        )

    return ph_content


def reports_page() -> ft.Div:
    categories = []
    for i, cat in enumerate(state.template_categories):
        if i > 0:
            categories.append(fc.Mdui_divider(middle=True))
        categories.append(template_category(cat))
    return ft.Div(
        *categories,
        id="reports-index",
        cls=("colors-surface", "m-2", "p-4", "rounded-lg"),
    )


def search_field(template: reports.Template, search: str) -> ft.Div | None:
    search_field_threshold = 3
    if template.instance_count <= search_field_threshold:
        return None
    return ft.Div(
        fc.Mdui_text_field(
            variant="outlined",
            label="Search",
            id="instance-search",
            name="search",
            value=search,
            icon="search",
            clearable=True,
            hx_trigger="input changed delay:300ms, search",
            hx_get=app.model_object_list.to(
                template_id=template.id,
                selected_model_element_uuid="",
            ),
            hx_swap="outerHTML",
            hx_target="#model_object_list",
        ),
        cls=("grid", "grid-cols-1", "pl-2", "pr-4"),
    )


def template_card(template: reports.Template) -> ft.A:
    url = app.app.url_path_for("template_page", template_id=template.id)

    # https://tailwindcss.com/docs/detecting-classes-in-source-files#dynamic-class-names
    colors = ("colors-primary-container", "colors-primary")
    if template.scope:
        if template.scope.below == "oa":
            colors = ("colors-layer-oa-container", "colors-layer-oa")
        elif template.scope.below == "sa":
            colors = ("colors-layer-sa-container", "colors-layer-sa")
        elif template.scope.below == "la":
            colors = ("colors-layer-la-container", "colors-layer-la")
        elif template.scope.below == "pa":
            colors = ("colors-layer-pa-container", "colors-layer-pa")

    chips = []
    if template.isExperimental:
        chips.append(
            fc.Mdui_chip(
                "Experimental",
                icon="science--rounded",
                cls="chip-experimental",
            )
        )

    if template.isStable:
        chips.append(
            fc.Mdui_chip(
                "Stable",
                icon="gpp_good--rounded",
                cls="chip-stable",
            )
        )

    if template.isDocument:
        chips.append(
            fc.Mdui_chip(
                "Document",
                icon="description",
                cls="chip-document",
            )
        )

    if chips:
        chip_container = ft.Div(
            *chips, cls="flex flex-row grow place-items-end p-4"
        )
    else:
        chip_container = None

    return fc.Mdui_card(
        ft.Div(
            ft.Div(
                template.name,
                cls="text-2xl",
            ),
            ft.Div(
                icons.file_stack()
                if template.instance_count > 1
                else icons.report(),
                ft.Span(
                    template.instance_count,
                    cls="hidden" if template.instance_count <= 1 else "block",
                ),
                cls=(
                    "flex",
                    "flex-row",
                    "items-top",
                    "pt-2",
                    "space-x-2",
                ),
            ),
            cls=(
                "_template-card-header",
                "flex",
                "flex-row",
                "justify-between",
                "p-4",
                "rounded-t-lg",
                colors[1],
            ),
        ),
        ft.P(
            template.description,
            cls=(
                "_template-card-description",
                "p-4",
                "text-left",
            ),
        ),
        chip_container,
        cls=(
            "flex",
            "flex-col",
            "m-4",
            "transition",
            "w-80",
            colors[0],
        ),
        href=url,
        hx_get=url,
        hx_target="#root",
        hx_push_url="true",
    )


def template_category(
    template_category: reports.TemplateCategory,
) -> ft.Div:
    return ft.Div(
        ft.P(
            f"{template_category.idx} Reports",
            cls=("font-semibold", "pb-2", "text-2xl", "text-center"),
        ),
        ft.Div(
            *[
                template_card(template)
                for template in template_category.templates
            ],
            cls=(
                "2xl:grid-cols-4",
                "auto-rows-auto",
                "content-around",
                "grid",
                "grid-flow-row",
                "pt-4",
                (
                    " sm:grid-cols-1"
                    " md:grid-cols-1"
                    " lg:grid-cols-2"
                    " xl:grid-cols-3"
                ),
            ),
        ),
        id="template-category",
        cls="rounded-lg w-full my-2 mx-auto justify-center",
    )


def template_container(content: t.Any) -> ft.Div:
    return ft.Div(
        content,
        id="template_container",
        cls=(
            "bg-white",
            "dark:bg-neutral-800",
            "dark:border-b",
            "dark:lg:border-l",
            "dark:border-neutral-700",
            "dark:shadow-neutral-700",
            "min-h-full",
            "html-content",  # copied from v0.2.3
            "items-center",
            "justify-center",
            "p-4",
            "print:bg-white",
            "print:m-0",
            "print:ml-6",
            "print:p-0",
            "svg-display",  # copied from v0.2.3
            "template-container",
            "w-full",
        ),
    )


def template_sidebar(
    *,
    template: reports.Template,
    selected_model_element_uuid: str | None,
    search: str = "",
    oob: bool = False,
) -> ft.Div:
    sidebar_caption = (
        ft.Div(
            ft.H1(
                template.name,
                cls="text-xl text-neutral-700 dark:text-neutral-400",
            ),
            ft.H2(
                template.description,
                cls="text-sm text-neutral-900 dark:text-neutral-400",
            ),
            cls="mx-2",
        ),
    )
    return ft.Div(
        sidebar_caption,
        search_field(template, search=search),
        model_elements_list(
            template=template,
            selected_id=selected_model_element_uuid,
            search=search,
        ),
        id="template-sidebar",
        cls=(
            "dark:bg-neutral-900",
            "flex",
            "flex-col",
            "h-full",
            "lg:max-h-[calc(100vh-12*var(--spacing))]",
            "lg:w-96",
            "max-h-[calc(0.85*(100vh-12*var(--spacing)))]",
            "pl-4",
            "print:hidden",
            "py-4",
            "rounded-lg",
            "space-y-4",
            "sticky",
            "top-0",
        ),
        **({"hx_swap_oob": "true"} if oob else {}),
    )
