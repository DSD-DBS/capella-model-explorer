# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from urllib.parse import quote

from fasthtml import common as fh
from fasthtml import ft, svg

from capella_model_explorer import icons, state, templates


def application_shell(
    content: ft.Div,
    align: t.Literal["left", "center", "right"] = "center",
) -> t.Any:
    return (
        ft.Title(f"{state.model.name} - Model Explorer"),
        ft.Main(
            page_header(),
            content,
            # placeholder for script injection per outerHTML swap
            ft.Script(id="script"),
            id="root",
            cls=(
                "bg-slate-100",
                "dark:bg-neutral-900",
                "flex",
                "flex-col",
                "h-screen",
                "min-h-screen",
                f"place-items-{align}",
            ),
        ),
    )


def breadcrumb(breadcrumb: state.Breadcrumb) -> t.Any:
    return (
        ft.Li(
            ft.Div(
                svg.Svg(
                    svg.Path(d="M.293 0l22 22-22 22h1.414l22-22-22-22H.293z"),
                    viewbox="0 0 24 44",
                    preserveaspectratio="none",
                    aria_hidden="true",
                    cls="h-full w-6 stroke-1 stroke-neutral-200 dark:stroke-blue-500",
                ),
                ft.A(
                    breadcrumb.label,
                    href=breadcrumb.url,
                    cls=(
                        "dark:hover:text-neutral-100",
                        "dark:text-blue-500",
                        "font-medium",
                        "hover:text-blue-900",
                        "ml-4",
                        "text-neutral-200",
                        "text-sm",
                    ),
                ),
                cls="flex items-center",
            ),
            cls="flex",
        ),
    )


def breadcrumbs() -> t.Any:
    home_item = (
        ft.Li(
            ft.Div(
                ft.A(
                    icons.home(),
                    ft.Span("Home", cls="sr-only"),
                    href="/",
                ),
                cls="flex items-center",
            ),
            cls="flex",
        ),
    )
    breadcrumb_items_ = [home_item]
    if state.breadcrumbs:
        breadcrumb_items_.extend([breadcrumb(b) for b in state.breadcrumbs])
    return ft.Nav(
        ft.Ol(
            *breadcrumb_items_,
            role="list",
            cls="flex space-x-4 rounded-md px-6",
        ),
        id="breadcrumbs",
        aria_label="Breadcrumb",
        cls="flex",
    )


def breadcrumbs_refresh_script() -> t.Any:
    return ft.Script(
        "htmx.ajax("
        "'GET', '/breadcrumbs', {swap: 'outerHTML', target:'#breadcrumbs'}"
        ");"
        "console.log('breadcrumbs refreshed');"
    )


def model_information() -> t.Any:
    """Render the model information including the badge."""
    return ft.Div(
        ft.H1(state.model.name, cls="text-xl"),
        ft.P(
            f"Capella version: {state.model.info.capella_version}",
        ),
        ft.P(
            "Date created: dummy",
        ),
        ft.Div(
            fh.NotStr(state.model.description_badge),
        ),
        cls=(
            "bg-white",
            "dark:bg-neutral-800",
            "dark:shadow-none",
            "dark:text-neutral-400",
            "flex",
            "flex-col",
            "max-w-min",
            "m-2",
            "mt-4",
            "p-4",
            "place-items-center",
            "rounded-lg",
            "shadow-blue-300",
            "shadow-lg",
            "svg-display",
            "text-center",
            "text-gray-700",
        ),
    )


def model_object_button(model_element: dict) -> t.Any:
    template = t.cast(templates.Template, state.template)
    return ft.Div(
        ft.Div(model_element["name"]),
        ft.Div(model_element["uuid"], cls="text-xs text-sky-700")
        if state.show_uuids
        else None,
        id=f"model-element-{model_element['uuid']}",
        cls=(
            "bg-slate-200",
            "break-words",
            "cursor-pointer",
            "dark:bg-neutral-800",
            "dark:hover:bg-neutral-700",
            "dark:text-neutral-400",
            "duration-300",
            "flex",
            "flex-col",
            "hover:bg-slate-100",
            "hover:scale-[1.02]",
            "model_object_btn",
            "p-4",
            "place-items-left",
            "rounded-md",
            "shadow",
            "text-left",
            # "text-slate-900",
            "transition",
            "w-full",
        ),
        hx_trigger="click",
        hx_get=f"/template/{quote(template.id)}/{model_element['uuid']}",
        hx_push_url=(
            f"/templates/{quote(template.id)}"
            f"/model-elements/{model_element['uuid']}"
        ),
        hx_swap="outerHTML",
        hx_target="#template_container",
    )


def model_object_list() -> t.Any:
    template = t.cast(templates.Template, state.template)
    model_objs = [
        obj
        for obj in sorted(template.instances, key=lambda x: x["name"])
        if not state.search or state.search.lower() in obj["name"].lower()
    ]
    return ft.Div(
        ft.Div(
            *[model_object_button(model_obj) for model_obj in model_objs],
            cls="flex flex-col space-y-4 px-2 my-2",
        ),
        ft.Script(src="/static/js/model_object_list.js"),
        id="model_object_list",
        cls="overflow-auto max-h-[calc(100vh-20rem)]",
    )


def page_header() -> t.Any:
    return (
        ft.Nav(
            breadcrumbs(),
            ft.Button(
                icons.printer(),
                onclick="window.print();",
                id="print-button",
                cls="hidden",
                title="Print report",
            ),
            id="page-header",
            cls=(
                "bg-blue-500",
                "dark:bg-neutral-800",
                "dark:border-b",
                "dark:border-neutral-700",
                "flex",
                "h-16",
                "justify-between",
                "min-h-16",
                "max-h-16",
                "p-4",
                "print:hidden",
                "sticky",
                "top-0",
                "w-full",
                # ensure that SVGs from rendered templates won't overlap in
                # dark mode due to CSS filters
                "z-50",
            ),
        ),
    )


def reports() -> t.Any:
    template_category_views = [
        template_category(t) for t in state.template_categories
    ]
    return ft.Div(
        *template_category_views,
        id="index",
        cls=(
            "bg-white",
            "dark:bg-neutral-800",
            "dark:shadow-none",
            "flex",
            "flex-col",
            "m-2",
            "p-4",
            "place-items-center",
            "rounded-lg",
            "shadow-blue-300",
            "shadow-lg",
            "space-y-16",
        ),
    )


def search_field() -> t.Any:
    template = t.cast(templates.Template, state.template)
    search_field_threshold = 3
    return ft.Div(
        ft.Input(
            icons.magnifying_glass(),
            type="search",
            id="instance-search",
            name="search",
            placeholder="Search",
            value=state.search,
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
                "focus:outline-blue-500",
                "grow",
                "mx-2",
                "outline",
                "outline-1",
                "outline-gray-300",
                "pl-8",
                "placeholder:text-gray-400",
                "pr-3",
                "py-1.5",
                "rounded-md",
                "row-start-1",
                "text-gray-900",
            ),
            hx_trigger="input changed delay:20ms, search",
            # the input has the name "search". This is why a request
            hx_get="/model-object-list",
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
        ),
    )


def template_card(template: templates.Template) -> t.Any:
    url = f"/templates/{quote(template.id)}"
    return ft.A(
        ft.Div(
            ft.Div(
                template.name,
                cls="text-gray-900 dark:text-neutral-400 text-2xl",
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
                ),
            ),
            cls="flex flex-row justify-between",
        ),
        ft.P(
            template.description,
            cls=(
                "dark:text-neutral-400",
                "py-4",
                "text-gray-700",
                "text-left",
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
                    "dark:text-yellow-600",
                    "flex",
                    "flex-row",
                    "font-medium",
                    "inline-block",
                    "me-2",
                    "px-2.5",
                    "py-1",
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
                    "dark:text-green-500",
                    "flex",
                    "flex-row",
                    "font-medium",
                    "inline-block",
                    "me-2",
                    "px-2.5",
                    "py-1",
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
                    "dark:text-blue-400",
                    "flex",
                    "flex-row",
                    "font-medium",
                    "inline-block",
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
            else "flex flex-row pt-4",
        ),
        cls=(
            "active:border-blue-600",
            "bg-slate-200",
            "dark:bg-neutral-900",
            "dark:hover:bg-neutral-700",
            "duration-300",
            "flex",
            "flex-col",
            "hover:bg-slate-100",
            "hover:cursor-pointer",
            "hover:scale-105",
            "m-4",
            "p-4",
            "rounded-lg",
            "shadow-2xl",
            "transition",
            "w-80",
        ),
        hx_get=url,
        hx_swap="outerHTML",
        hx_target="#root",
        hx_push_url="true",
        href=url,
    )


def template_category(
    template_category: templates.TemplateCategory,
) -> t.Any:
    return ft.Div(
        ft.P(
            f"{template_category.idx} Reports",
            cls=(
                "border-b",
                "border-gray-900",
                "dark:border-neutral-700",
                "dark:text-neutral-400",
                "font-semibold",
                "pb-2",
                "text-2xl",
                "text-center",
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


def template_container(content: t.Any) -> t.Any:
    return ft.Div(
        content,
        id="template_container",
        cls=(
            "bg-white",
            "dark:bg-neutral-800",
            "dark:border-l",
            "dark:border-neutral-700",
            "dark:shadow-neutral-700",
            "items-center",
            "justify-center",
            "ml-96",
            "overflow-x-auto",
            "p-4",
            "print:bg-white",
            "print:m-0",
            "print:ml-6",
            "print:p-0",
            "template-container",
            "w-full",
        ),
    )


def template_placeholder() -> t.Any:
    return ft.Span(
        "Select a model element.",
        cls="text-slate-600 dark:text-slate-500 p-4 italic",
    )


def template_sidebar() -> t.Any:
    template = t.cast(templates.Template, state.template)
    sidebar_caption = (
        ft.Div(
            ft.H1(
                template.name,
                cls="text-xl text-gray-700 dark:text-neutral-400",
            ),
            ft.H2(
                template.description,
                cls="text-sm text-gray-900 dark:text-neutral-400",
            ),
            cls="mx-2",
        ),
    )
    return ft.Div(
        sidebar_caption,
        search_field(),
        model_object_list(),
        cls=(
            "dark:bg-neutral-900",
            "flex",
            "flex-col",
            "rounded-lg",
            "space-y-4",
        ),
    )


def theme_button(theme: t.Literal["dark", "light"]) -> t.Any:
    return ft.Button(
        icons.dark_theme() if theme == "dark" else icons.light_theme(),
        id="theme-button",
        cls=(
            "bg-slate-200",
            "h-10",
            "hover:bg-slate-100",
            "place-content-center",
            "place-items-center",
            "rounded-full",
            "w-10",
        ),
        onclick="toggleTheme()",
    )
