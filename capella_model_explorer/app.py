# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import contextlib
import logging
import pathlib
import tempfile
import time
import traceback
import typing as t

import capellambse
import jinja2
import prometheus_client
import starlette
import starlette.middleware
from fasthtml import common as fh
from fasthtml import ft

import capella_model_explorer.constants as c
from capella_model_explorer import components, icons, reports, state

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(_):
    logger.info("Configuration:")
    logger.info("\tRoute prefix: '%s'", c.ROUTE_PREFIX)
    logger.info("\tLive mode: %s", c.LIVE_MODE)
    logger.info("\tHost: '%s'", c.HOST)
    logger.info("\tCapella model: '%s'", c.MODEL)
    logger.info("\tTemplates directory: '%s'", c.TEMPLATES_DIR)

    model_spec = capellambse.loadinfo(c.MODEL)
    logger.info("Loading model from: %s", model_spec["path"])
    state.model = capellambse.MelodyModel(**model_spec)
    logger.info("Loading templates from: %s", c.TEMPLATES_DIR)
    reports.load_templates()
    state.jinja_env = jinja2.Environment(
        autoescape=True, loader=jinja2.FileSystemLoader(c.TEMPLATES_DIR)
    )
    state.jinja_env.finalize = reports.finalize
    state.jinja_env.filters["make_href"] = reports.make_href_filter
    yield


class UpdateLastInteractionTimeMiddleware(
    starlette.middleware.base.BaseHTTPMiddleware
):
    async def dispatch(self, request, call_next):
        if request.url.path not in ("/metrics", "/favicon.ico"):
            state.last_interaction = time.time()
        return await call_next(request)


if c.LIVE_MODE:
    _app_cls = fh.FastHTMLWithLiveReload
else:
    _app_cls = fh.FastHTML


app = _app_cls(
    hdrs=c.HEADERS,
    key_fname=pathlib.Path(tempfile.gettempdir()) / ".sesskey",
    live=c.LIVE_MODE,
    lifespan=lifespan,
    middleware=[
        starlette.middleware.Middleware(UpdateLastInteractionTimeMiddleware),
    ],
    pico=False,
)
ar = fh.APIRouter(prefix=c.ROUTE_PREFIX)
app.static_route_exts(f"{c.ROUTE_PREFIX}/static", "./static")


@app.get("/metrics")
def metrics() -> t.Any:
    idle_time_minutes = (time.time() - state.last_interaction) / 60
    state.idle_time_gauge.set(idle_time_minutes)
    return fh.Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )


@app.get("/")
def prefix_redirect(request) -> t.Any:
    if c.ROUTE_PREFIX:
        return fh.RedirectResponse(url=app.url_path_for("main_home"))
    return home(request)


@ar.get("/", name="main_home")
def home(request) -> t.Any:
    """Show home/ landing page with all reports in categories."""
    page_content = (
        ft.Div(
            components.model_information(),
            components.reports_page(),
            cls="flex flex-col space-y-4 place-items-center mx-auto mb-4",
        ),
        ft.Div(
            ft.A(
                ft.Div("Contribute on GitHub"),
                icons.github_logo(),
                href="https://github.com/DSD-DBS/capella-model-explorer",
                target="_blank",
                cls=(
                    "dark:text-gray-300",
                    "flex",
                    "hover:underline",
                    "max-w-fit",
                    "place-items-center",
                    "space-x-2",
                ),
            ),
            cls="w-full pl-8 h-8 py-2 mx-auto my-8",
        ),
    )
    return _maybe_wrap_content(request, None, None, page_content)


@ar.get("/model-object-list")
def model_object_list(
    template_id: str, selected_model_element_uuid: str = "", search: str = ""
) -> t.Any:
    """Return (filtered) list of model elements for active template."""
    template = reports.template_by_id(template_id)
    assert template is not None
    return components.model_elements_list(
        template=template,
        selected_id=selected_model_element_uuid,
        search=search,
    )


@ar.get("/rendered-report")
def rendered_report(template_id: str, model_element_uuid: str = "") -> t.Any:
    """Render and return report.

    Takes the template and model element from the application state and
    returns the rendered template.
    """
    template = reports.template_by_id(template_id)
    assert template is not None
    model_element = (
        state.model.by_uuid(model_element_uuid) if model_element_uuid else None
    )
    template_content = template.path.read_text(encoding="utf8")
    jinja_template = state.jinja_env.from_string(template_content)
    try:
        rendered_template = jinja_template.render(
            object=model_element,
            model=state.model,
            diff_data={},
            object_diff={},
        )
    except Exception:
        full_traceback = traceback.format_exc()
        print(full_traceback)
        return ft.Div(
            ft.Div("Error rendering template:", cls="text-xl"),
            fh.Pre(
                full_traceback,
                cls="text-xs prose dark:prose-invert",
            ),
            cls="dark:text-neutral-100 grow content-center",
        )
    content = ft.Div(
        fh.NotStr(rendered_template),
        ft.Script(
            "document.getElementById('root').classList.remove('h-screen');"
            "document.getElementById('print-button').classList.remove('hidden');"
        ),
        cls="prose svg-display dark:prose-invert",
    )
    max_age = 31536000 if state.model.info.resources["\x00"].rev_hash else 0
    return (
        content,
        fh.HttpHeader(k="Cache-Control", v=f"max-age={max_age}"),
        fh.HttpHeader(k="Vary", v="Render-Environment"),
    )


@ar.get("/template/{template_id}")
@ar.get("/report/{template_id}/{model_element_uuid}")
def template_page(
    request: starlette.requests.Request,
    template_id: str,
    model_element_uuid: str | None = None,
) -> t.Any:
    template = reports.template_by_id(template_id)
    if template is None:
        template_path = pathlib.Path(template_id.replace("|", "/"))
        content = ft.Div(
            ft.Div("Template not found:", cls="text-xl"),
            fh.Code(template_path),
            cls="dark:text-neutral-100 grow content-center",
        )
        return _maybe_wrap_content(request, None, None, content)

    if template.single:
        placeholder = components.report_placeholder(template, None)
    elif model_element_uuid:
        placeholder = components.report_placeholder(
            template, model_element_uuid
        )
    elif len(template.instances) == 1:
        model_element_uuid = template.instances[0]["uuid"]
        placeholder = components.report_placeholder(
            template, model_element_uuid
        )
    else:
        placeholder = components.report_placeholder(None, None)

    page_content = ft.Div(
        components.template_sidebar(
            template=template,
            selected_model_element_uuid=model_element_uuid,
        ),
        components.template_container(placeholder),
        id="template-page-content",
        cls=(
            "flex",
            "flex-col-reverse",
            "justify-between",
            "lg:flex-row",
            "min-h-full",
            "print:bg-white",
            "print:min-h-auto",
            "w-full",
        ),
    )
    return _maybe_wrap_content(
        request, template, model_element_uuid, page_content
    )


def _maybe_wrap_content(
    request: starlette.requests.Request,
    template: reports.Template | None,
    element: str | None,
    content: t.Any,
) -> t.Any:
    if request.headers.get("HX-Request") == "true":
        return content, components.breadcrumbs(template, element, oob=True)
    return components.application_shell(
        content, template=template, element=element
    )


@ar.get("/render")
def render_template(
    template_id: str,
    model_element_uuid: str | None = None,
) -> t.Any:
    """Request the rendering of a template.

    Returns a template container with loading spinner that itself (htmx)
    requests the rendered template and replaces itself with the rendered
    template.
    """
    template = reports.template_by_id(template_id)
    return (
        components.report_placeholder(template, model_element_uuid),
        components.breadcrumbs(template, model_element_uuid, oob=True),
    )


ar.to_app(app)
