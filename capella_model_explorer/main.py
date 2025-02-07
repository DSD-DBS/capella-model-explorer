# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import http
import logging
import os
import pathlib
import signal
import threading
import time
import traceback
import typing as t

import capellambse
import jinja2
import prometheus_client
from fasthtml import common as fh
from fasthtml import ft, starlette

import capella_model_explorer.constants as c
from capella_model_explorer import components, core, icons, reports, state

LOG_LEVEL = "INFO"
ROUTES = [
    fh.Mount(f"{c.ROUTE_PREFIX}/reports", reports.app),
]
logger = logging.getLogger("uvicorn")
logger.setLevel("INFO")
core.setup_logging(logger)

logger.info("Configuration:")
logger.info("\tRoute prefix: '%s'", c.ROUTE_PREFIX)
logger.info("\tLive mode: %s", c.LIVE_MODE)
logger.info("\tHost: '%s'", c.HOST)
logger.info("\tRoute prefix: '%s'", c.ROUTE_PREFIX)
logger.info("\tCapella model: '%s'", c.MODEL)
logger.info("\tTemplates directory: '%s'", c.TEMPLATES_DIR)

if c.LIVE_MODE:
    _app_cls = fh.FastHTMLWithLiveReload
else:
    _app_cls = fh.FastHTML

app = _app_cls(
    hdrs=c.HEADERS,
    key_fname="/tmp/.sesskey",
    live=c.LIVE_MODE,
    pico=False,
    routes=ROUTES,
)
ar = fh.APIRouter(prefix=c.ROUTE_PREFIX)
app.static_route_exts(f"{c.ROUTE_PREFIX}/static", "./static")


def _delayed_shutdown() -> None:
    time.sleep(0.05)
    os.kill(os.getpid(), signal.SIGINT)


@app.on_event("startup")
async def startup() -> None:
    logger.info("Waiting for model to load from specification '%s'", c.MODEL)
    state.model = capellambse.loadcli(c.MODEL)
    state.models = {core.model_id(state.model): state.model}
    logger.info("Model load complete.")
    logger.info(
        "Waiting for templates to load from directory '%s'", c.TEMPLATES_DIR
    )
    reports.load_templates()
    state.JINJA_ENV = jinja2.Environment(
        loader=jinja2.FileSystemLoader(c.TEMPLATES_DIR)
    )
    state.JINJA_ENV.finalize = reports._finalize
    state.JINJA_ENV.filters["make_href"] = reports._make_href_filter
    logger.info("Templates load complete.")


@app.post("/shutdown")
def shutdown() -> t.Any:
    if c.LIVE_MODE:
        return starlette.Response(
            content=(
                "Shutdown not supported in live mode."
                " Set environment variable CME_LIVE_MODE=0"
                " to be able to shut down the server via HTTP request."
            ),
            status_code=http.HTTPStatus.NOT_IMPLEMENTED,
        )
    # delay shutdown to allow response to be sent
    thread = threading.Thread(target=_delayed_shutdown)
    thread.start()
    return starlette.Response(
        content="Will shut down server.",
        status_code=http.HTTPStatus.ACCEPTED,
    )


@app.middleware("http")
async def update_last_interaction_time(request: fh.Request, call_next):
    if request.url.path not in ("/metrics", "/favicon.ico"):
        state.last_interaction = time.time()
    return await call_next(request)


@app.get("/metrics")
def metrics() -> t.Any:
    idle_time_minutes = (time.time() - state.last_interaction) / 60
    state.idle_time_gauge.set(idle_time_minutes)
    return fh.Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )


@ar.get("/", name="main_home")
def home() -> t.Any:
    """Show home/ landing page with all reports in categories."""
    return reports.home()


@ar.get("/model-object-list")
def model_object_list(
    template_id: str, selected_model_element_uuid: str = "", search: str = ""
) -> t.Any:
    """Return (filtered) list of model elements for active template."""
    template = t.cast(reports.Template, reports.template_by_id(template_id))
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
    model_element = (
        state.model.by_uuid(model_element_uuid) if model_element_uuid else None
    )
    template_content = t.cast(reports.Template, template).path.read_text(
        encoding="utf8"
    )
    jinja_template = state.JINJA_ENV.from_string(template_content)
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


@ar.get("/templates/{template_id}")
@ar.get("/templates/{template_id}/model-elements/{model_element_uuid}")
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
    script = "document.getElementById('root').classList.add('h-screen');\n"
    if template.single:
        # request rendering of template w/o specific model element
        ctxt = "{swap:'outerHTML', target:'#template_container'}"
        url = render_template.to(
            template_id=template.id, model_element_uuid=""
        )
        if model_element_uuid:
            # request rendering of template with specified model element
            url = app.url_path_for(
                "render_template",
                template_id=template.id,
                model_element_uuid=model_element_uuid,
            )
        script += f"htmx.ajax('GET', '{url}', {ctxt});"
    if (
        not model_element_uuid
        and not template.single
        and template.instance_count == 1
    ):
        # when there is only one element in the model element, select it
        model_element_uuid = template.instances[0]["uuid"]
    if not template.single:
        script += core.jsfromfile(
            "static/js/select-model-element-by-uuid.js"
        ).replace("{uuid}", model_element_uuid)
    page_content = ft.Div(
        ft.Div(
            components.template_sidebar(
                template=template,
                selected_model_element_uuid=model_element_uuid,
            ),
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
    template = t.cast(reports.Template, reports.template_by_id(template_id))
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
            hx_get=rendered_report.to(
                template_id=template_id,
                model_element_uuid=model_element_uuid,
            ),
            hx_swap="outerHTML",
            hx_target="#template_container",
        )
    ), components.breadcrumbs(
        template=template,
        model_element_uuid=model_element_uuid,
        oob=True,
    )


ar.to_app(app)
