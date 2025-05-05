# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import pathlib
import typing as t

import capellambse
import capellambse_context_diagrams
from fasthtml import common as fh
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
    return ft.Div(
        ft.H1(state.model.name, cls="text-xl"),
        ft.P(
            f"Capella version: {state.model.info.capella_version}",
        ),
        ft.Div(
            fh.NotStr(state.model.description_badge),
        ),
        cls=(
            "bg-white",
            "dark:bg-neutral-800/50",
            "dark:shadow-none",
            "dark:text-neutral-400",
            "flex",
            "flex-col",
            "max-w-full",
            "m-2",
            "mt-4",
            "p-4",
            "place-items-center",
            "rounded-lg",
            "shadow-primary-500",
            "shadow-xs",
            "svg-display",
            "text-center",
            "text-neutral-700",
        ),
    )


def model_object_button(
    *, template: reports.Template, model_element: dict, selected: bool = False
) -> ft.A:
    return ft.A(
        ft.Div(model_element["name"]),
        ft.Div(model_element["uuid"], cls="text-xs text-sky-700")
        if state.show_uuids
        else None,
        id=f"model-element-{model_element['uuid']}",
        aria_selected="true" if selected else "false",
        cls=(
            "aria-selected:bg-primary-500",
            "aria-selected:dark:hover:bg-primary-500",
            "aria-selected:dark:text-white",
            "aria-selected:text-white",
            "bg-neutral-200",
            "break-words",
            "cursor-pointer",
            "dark:bg-neutral-800",
            "dark:hover:bg-neutral-700",
            "dark:text-neutral-400",
            "duration-300",
            "flex",
            "flex-col",
            "hover:bg-primary-50",
            "hover:scale-[1.02]",
            "model_object_btn",
            "p-4",
            "place-items-left",
            "rounded-md",
            "shadow-sm",
            "text-left",
            "transition",
            "w-full",
        ),
        hx_trigger="click",
        hx_get=app.render_template.to(
            template_id=template.id,
            model_element_uuid=model_element["uuid"],
        ),
        hx_push_url=app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=model_element["uuid"],
        ),
        hx_target="#template_container",
    )


def model_elements_list(
    *,
    template: reports.Template,
    selected_id: str | None,
    search: str = "",
) -> ft.Div:
    search_words = search.lower().split()
    model_elements = [
        obj
        for obj in sorted(template.instances, key=lambda x: x["name"])
        if (n := obj["name"].lower()) and all(w in n for w in search_words)
    ]
    return ft.Div(
        ft.Div(
            *(
                model_object_button(
                    template=template,
                    model_element=model_element,
                    selected=model_element["uuid"] == selected_id,
                )
                for model_element in model_elements
            ),
            cls="flex flex-col space-y-4 pl-2 pr-4 my-2",
        ),
        ft.Script(
            pathlib.Path("static/js/model_object_list.js").read_text(
                encoding="utf8"
            )
        ),
        id="model_object_list",
        cls="overflow-auto grow",
    )


def navbar(template: reports.Template | None, element: str | None) -> ft.Nav:
    return ft.Nav(
        breadcrumbs(template, element),
        ft.Button(
            icons.printer(),
            onclick="window.print();",
            id="print-button",
            title="Print report",
            cls="hidden hover:cursor-pointer",
        ),
        ft.Button(
            icons.theme_system(id="dark-mode-icon-system"),
            icons.theme_dark(id="dark-mode-icon-dark", cls=("hidden",)),
            icons.theme_light(id="dark-mode-icon-light", cls=("hidden",)),
            id="dark-mode-button",
            title="Toggle dark mode",
            cls="cursor-pointer",
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
            "min-h-12",
            "max-h-12",
            "px-4",
            "py-0",
            "print:hidden",
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
            hx_push_url=app.app.url_path_for(
                "template_page",
                template_id=template.id,
                model_element_uuid=model_element_uuid,
            ),
            hx_target="#template_container",
            cls="flex justify-center place-items-center h-full w-full",
        )

    return ph_content


def reports_page() -> ft.Div:
    return ft.Div(
        *(template_category(t) for t in state.template_categories),
        id="reports-index",
        cls=(
            "bg-white",
            "dark:bg-neutral-800/50",
            "dark:shadow-none",
            "flex",
            "flex-col",
            "m-2",
            "p-4",
            "place-items-center",
            "rounded-lg",
            "shadow-primary-500",
            "shadow-xs",
            "space-y-16",
        ),
    )


def search_field(template: reports.Template, search: str) -> ft.Div:
    search_field_threshold = 3
    return ft.Div(
        ft.Input(
            icons.magnifying_glass(),
            type="search",
            id="instance-search",
            name="search",
            placeholder="Search",
            value=search,
            cls=(
                "-outline-offset-1",
                "bg-white",
                "block",
                "col-start-1",
                "dark:bg-neutral-800",
                "dark:focus:outline-white",
                "dark:text-neutral-400",
                "focus:-outline-offset-2",
                "focus:outline-2",
                "focus:outline-primary-500",
                "grow",
                "outline",
                "outline-1",
                "outline-neutral-300",
                "pl-8",
                "placeholder:text-neutral-400",
                "pr-3",
                "py-1.5",
                "rounded-md",
                "row-start-1",
                "text-neutral-900",
            ),
            hx_trigger="input changed delay:20ms, search",
            hx_get=app.model_object_list.to(
                template_id=template.id,
                selected_model_element_uuid="",
            ),
            hx_swap="outerHTML",
            hx_target="#model_object_list",
            autofocus="true",
        ),
        cls=(
            "hidden"
            if template.instance_count <= search_field_threshold
            else "",
            "grid",
            "grid-cols-1",
            "pl-2",
            "pr-4",
        ),
    )


def template_card(template: reports.Template) -> ft.A:
    url = app.app.url_path_for("template_page", template_id=template.id)
    return ft.A(
        ft.Div(
            ft.Div(
                template.name,
                cls="text-neutral-100 dark:text-neutral-400 text-2xl",
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
                    "dark:text-neutral-400",
                    "flex",
                    "flex-row",
                    "items-top",
                    "pt-2",
                    "space-x-2",
                    "text-primary-50",
                ),
            ),
            cls=(
                "_template-card-header",
                "bg-primary-500",
                "dark:bg-neutral-900",
                "flex",
                "flex-row",
                "justify-between",
                "p-4",
                "rounded-t-lg",
            ),
        ),
        ft.P(
            template.description,
            cls=(
                "_template-card-description",
                "dark:text-neutral-300",
                "p-4",
                "text-left",
                "text-neutral-800",
            ),
        ),
        ft.Div(
            ft.Div(
                icons.badge_experimental(),
                ft.P("Experimental"),
                cls="hidden"
                if not template.isExperimental
                else (
                    "bg-yellow-100",
                    "border",
                    "border-yellow-800",
                    "dark:border-yellow-600",
                    "dark:bg-yellow-900",
                    "dark:text-yellow-300",
                    "flex",
                    "flex-row",
                    "font-medium",
                    "max-h-7",
                    "me-2",
                    "px-2.5",
                    "py-1",
                    "rounded-full",
                    "space-x-2",
                    "text-xs",
                    "text-yellow-800",
                ),
            ),
            ft.Div(
                icons.badge_stable(),
                ft.P("Stable"),
                cls="hidden"
                if not template.isStable
                else (
                    "bg-green-100",
                    "border",
                    "border-green-800",
                    "dark:bg-green-700",
                    "dark:border-green-500",
                    "dark:text-green-200",
                    "flex",
                    "flex-row",
                    "font-medium",
                    "max-h-7",
                    "me-2",
                    "px-2.5",
                    "py-1",
                    "rounded-full",
                    "space-x-2",
                    "text-green-800",
                    "text-xs",
                ),
            ),
            ft.Div(
                icons.badge_document(),
                ft.P("Document"),
                cls="hidden"
                if not template.isDocument
                else (
                    "bg-blue-200",
                    "border",
                    "border-blue-800",
                    "dark:bg-blue-700",
                    "dark:border-blue-400",
                    "dark:text-blue-200",
                    "flex",
                    "flex-row",
                    "font-medium",
                    "max-h-7",
                    "me-2",
                    "px-2.5",
                    "py-1",
                    "rounded-full",
                    "space-x-2",
                    "text-blue-800",
                    "text-xs",
                ),
            ),
            cls="hidden"
            if not template.isDocument
            and not template.isExperimental
            and not template.isStable
            else "flex flex-row grow place-items-end p-4",
        ),
        cls=(
            "_template-card",
            "active:border-blue-600",
            "bg-white",
            "dark:bg-neutral-800",
            "dark:hover:bg-neutral-700",
            "dark:shadow-neutral-900",
            "dark:shadow-xs",
            "duration-300",
            "flex",
            "flex-col",
            "hover:bg-primary-50",
            "hover:cursor-pointer",
            "hover:scale-105",
            "m-4",
            "rounded-lg",
            "shadow-lg",
            "transition",
            "w-80",
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
            cls=(
                "border-b",
                "border-neutral-900",
                "dark:border-neutral-700",
                "dark:text-neutral-400",
                "font-semibold",
                "pb-2",
                "text-2xl",
                "text-center",
                "text-neutral-800",
            ),
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
    )
