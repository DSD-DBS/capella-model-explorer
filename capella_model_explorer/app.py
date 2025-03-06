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
import starlette.responses
from fasthtml import common as fh
from fasthtml import ft

import capella_model_explorer.constants as c
from capella_model_explorer import components, core, reports, state

logger = logging.getLogger("uvicorn")
core.setup_logging(logger)


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
def prefix_redirect() -> t.Any:
    if c.ROUTE_PREFIX:
        return fh.RedirectResponse(url=app.url_path_for("main_home"))
    return home()


@ar.get("/", name="main_home")
def home() -> t.Any:
    """Show home/ landing page with all reports in categories."""
    return reports.home()


@ar.get("/model-object-list")
def model_object_list(
    template_id: str, selected_model_element_uuid: str = "", search: str = ""
) -> t.Any:
    """Return (filtered) list of model elements for active template."""
    template = reports.template_by_id(template_id)
    assert template is not None
    return components.model_elements_list(
        template=template,
        selected_model_element_uuid=selected_model_element_uuid,
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
        return components.template_container(
            ft.Div(
                ft.Div("Error rendering template:", cls="text-xl"),
                fh.Pre(
                    full_traceback,
                    cls="text-xs prose dark:prose-invert",
                ),
                cls="dark:text-neutral-100 grow content-center",
            )
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


@ar.get("/template/{template_id}")
@ar.get("/report/{template_id}/{model_element_uuid}")
def template_page(template_id: str, model_element_uuid: str = "") -> t.Any:
    template = reports.template_by_id(template_id)
    if template is None:
        template_path = pathlib.Path(template_id.replace("|", "/"))
        return components.application_shell(
            ft.Div(
                ft.Div("Template not found:", cls="text-xl"),
                fh.Code(template_path),
                cls="dark:text-neutral-100 grow content-center",
            )
        )
    report = ft.Span(
        "Select a model element.",
        cls="text-slate-600 dark:text-slate-500 p-4 italic",
    )
    script = "document.getElementById('root').classList.add('h-screen');\n"
    if template.instances and template.instance_count == 1:
        model_element_uuid = template.instances[0]["uuid"]
        report = components.report_loader(template_id, model_element_uuid)
    elif template.single:
        # request rendering of template w/o specific model element
        url = render_template.to(
            template_id=template.id, model_element_uuid=""
        )
        if model_element_uuid:
            # request rendering of template with specified model element
            url = render_template.to(
                template_id=template.id,
                model_element_uuid=model_element_uuid,
            )
        ctxt = "{swap:'outerHTML', target:'#template_container'}"
        script += f"htmx.ajax('GET', '{url}', {ctxt});"
    if (
        not model_element_uuid
        and not template.single
        and template.instance_count == 1
    ):
        # when there is only one element in the model element, select it
        model_element_uuid = template.instances[0]["uuid"]
    if not template.single:
        script += (
            pathlib.Path("static/js/select-model-element-by-uuid.js")
            .read_text(encoding="utf8")
            .replace("{uuid}", model_element_uuid)
        )
    page_content = (
        ft.Div(
            ft.Div(
                components.template_sidebar(
                    template=template,
                    selected_model_element_uuid=model_element_uuid,
                ),
                id="template-sidebar",
                cls="fixed min-w-96 w-96 p-4 print:hidden",
            ),
            ft.Div(
                report,
                id="template_container",
                cls=(
                    "bg-white",
                    "border",
                    "border-neutral-200",
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
        ),
    )
    return components.application_shell(page_content, "left")


@ar.get("/render")
def render_template(template_id: str, model_element_uuid: str = "") -> t.Any:
    """Request the rendering of a template.

    Returns a template container with loading spinner that itself (htmx)
    requests the rendered template and replaces itself with the rendered
    template.
    """
    template = reports.template_by_id(template_id)
    return components.template_container(
        components.report_loader(template_id, model_element_uuid)
    ), components.breadcrumbs(
        template=template,
        model_element_uuid=model_element_uuid,
        oob=True,
    )


ar.to_app(app)
