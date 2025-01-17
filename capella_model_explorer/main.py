# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import time
import typing as t
from urllib.parse import quote

import capellambse
import capellambse.model as m
import jinja2
import markupsafe
import prometheus_client
from fasthtml import common as fh
from fasthtml import ft
from starlette.datastructures import URLPath
from starlette.routing import NoMatchFound

import capella_model_explorer.constants as c
from capella_model_explorer import components, icons, state, templates

FRONTEND_DIR = pathlib.Path("./frontend/dist")


def url_path_for(
    endpoint: t.Callable[..., t.Any] | str,
    /,
    **path_params: t.Any,
) -> URLPath:
    name = endpoint if isinstance(endpoint, str) else endpoint.__name__
    for route in app.routes:
        try:
            return route.url_path_for(name, **path_params)
        except NoMatchFound:
            pass
    raise NoMatchFound(name, path_params)


# https://docs.fastht.ml/tutorials/quickstart_for_web_devs.html#other-static-media-file-locations
def _finalize(markup: t.Any) -> object:
    markup = markupsafe.escape(markup)
    return capellambse.helpers.replace_hlinks(markup, state.model, _make_href)


def _jsfromfile(jsfilepath: os.PathLike | str) -> str:
    return pathlib.Path(jsfilepath).read_text(encoding="utf8")


def _make_href(
    obj: m.ModelElement | m.AbstractDiagram,
) -> str | None:
    for template in state.templates:
        if "type" in dir(template.scope):
            clsname = t.cast(templates.TemplateScope, template.scope).type
            if obj.xtype.rsplit(":", 1)[-1] == clsname:
                return (
                    f"{c.ROUTE_PREFIX}/templates/{quote(template.id)}"
                    f"/model-elements/{obj.uuid}"
                )
    # find the generic template
    for template in state.templates:
        if "__generic__" in template.template.stem:
            return (
                f"{c.ROUTE_PREFIX}/templates/{quote(template.id)}"
                f"/model-elements/{obj.uuid}"
            )
    return fh.RedirectResponse("/")


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


def _reset_state() -> None:
    state.diff = {}
    state.object_diff = {}
    state.model_element = None
    state.search = ""
    state.template = None


app = (
    fh.FastHTMLWithLiveReload(**c.FASTHTML_APP_CONFIG)
    if c.LIVE_MODE
    else fh.FastHTML(**c.FASTHTML_APP_CONFIG)
)
ar = fh.APIRouter(prefix=c.ROUTE_PREFIX)
app.static_route_exts(f"{c.ROUTE_PREFIX}/static", "./static")


@app.on_event("startup")
def _app_startup() -> None:
    try:
        MODEL = os.environ["CME_MODEL"]
    except KeyError as err:
        raise SystemExit("CME_MODEL environment variable is not set") from err

    try:
        _1 = state.model
    except AttributeError:
        state.model = capellambse.loadcli(MODEL)
    templates.load()
    state.jinja_env.finalize = _finalize
    state.jinja_env.filters["make_href"] = _make_href_filter


@app.middleware("http")
async def update_last_interaction_time(request: fh.Request, call_next):
    if request.url.path not in ("/metrics", "/favicon.ico"):
        state.last_interaction = time.time()
    return await call_next(request)


@app.get("/metrics")
def metrics():
    idle_time_minutes = (time.time() - state.last_interaction) / 60
    state.idle_time_gauge.set(idle_time_minutes)
    return fh.Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )


@ar.get("/")
def homepage() -> t.Any:
    return fh.RedirectResponse(url=templates_page.to())


@ar.get("/templates")
def templates_page() -> t.Any:
    """Show home/ landing page with all templates in categories."""
    _reset_state()
    page_content = (
        ft.Main(
            ft.Div(
                components.model_information(),
                components.reports(),
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


@ar.get("/model-object-list")
def model_object_list(search: str = "") -> t.Any:
    """Return (filtered) list of model elements for active template."""
    state.search = search
    return components.model_object_list()


@ar.get("/rendered-template")
def rendered_template() -> t.Any:
    """Render and return template.

    Takes the template and model element from the application state and
    returns the rendered template.
    """
    template_content = t.cast(
        templates.Template, state.template
    ).path.read_text(encoding="utf8")
    jinja_template = state.jinja_env.from_string(template_content)
    rendered_template = jinja_template.render(
        object=state.model_element,
        model=state.model,
        diff_data=state.diff,
        object_diff=state.object_diff,
    )
    return components.template_container(
        ft.Div(
            fh.NotStr(rendered_template),
            ft.Script(
                "document.getElementById('root').classList.remove('h-screen');"
                "document.getElementById('print-button').classList.remove('hidden');"
            ),
            cls="prose svg-display dark:prose-invert",
        )
    )


@ar.get("/templates/{template_id}")
@ar.get("/templates/{template_id}/model-elements/{model_element_uuid}")
def template_page(template_id: str, model_element_uuid: str = "") -> t.Any:
    template = templates.template_by_id(template_id)
    state.search = ""
    if template is None:
        template_path = pathlib.Path(template_id.replace("|", "/"))
        return components.application_shell(
            ft.Div(
                ft.Div("Template not found:", cls="text-xl"),
                fh.Code(template_path),
                cls="dark:text-neutral-100 grow content-center",
            )
        )
    state.template = template
    if model_element_uuid:
        state.model_element = state.model.by_uuid(model_element_uuid)
    else:
        state.model_element = None
    script = "document.getElementById('root').classList.add('h-screen');\n"
    if state.template.single:
        # request rendering of template w/o specific model element
        ctxt = "{swap:'outerHTML', target:'#template_container'}"
        url = f"/template/{quote(state.template.id)}"
        if model_element_uuid:
            # request rendering of template with specified model element
            url += f"/{model_element_uuid}"
        script += f"htmx.ajax('GET', '{url}', {ctxt});"
    if (
        not model_element_uuid
        and not template.single
        and template.instance_count == 1
    ):
        # when there is only one element in the model element, select it
        model_element_uuid = template.instances[0]["uuid"]
    if not template.single:
        script += _jsfromfile(
            "static/js/select-model-element-by-uuid.js"
        ).replace("{uuid}", model_element_uuid)
    page_content = ft.Div(
        ft.Div(
            components.template_sidebar(),
            id="template-sidebar",
            cls="fixed min-w-96 w-96 p-4 print:hidden",
        ),
        ft.Div(
            components.template_placeholder(),
            id="template_container",
            cls=(
                "bg-white",
                "border",
                "border-gray-200",
                "dark:bg-neutral-800",
                "dark:border-neutral-700",
                "dark:shadow-neutral-700",
                "dark:shadow-md",
                "flex",
                "grow",
                "m-4",
                "ml-96",
                "rounded-lg",
                "items-center",
                "justify-center",
                "shadow-blue-300",
                "shadow-md",
            ),
        ),
        ft.Script(script),
        id="template-page-content",
        cls=("flex", "flex-row", "w-full", "h-full", "print:bg-white"),
    )
    return components.application_shell(page_content, "left")


@ar.get("/template/{template_id}/{model_element_uuid}")
def render_template(template_id: str, model_element_uuid: str = "") -> t.Any:
    """Request the rendering of a template.

    Returns a template container with loading spinner that itself (htmx)
    requests the rendered template and replaces itself with the rendered
    template.
    """
    state.template = t.cast(
        templates.Template, templates.template_by_id(template_id)
    )
    state.model_element = (
        state.model.by_uuid(model_element_uuid) if model_element_uuid else None
    )
    return components.template_container(
        ft.Div(
            icons.spinner(2.1),
            ft.Script(
                "document.getElementById('root').classList.add('h-screen');"
                "document.getElementById('print-button').classList.add('hidden');"
            ),
            cls=(
                "h-full",
                "justify-center",
                "place-content-center",
                "place-items-center",
                "w-full",
            ),
            hx_trigger="load",
            hx_get=app.url_path_for("rendered_template"),
            hx_swap="outerHTML",
            hx_target="#template_container",
        )
    ), components.breadcrumbs(oob=True)


ar.to_app(app)
