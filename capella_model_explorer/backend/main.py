# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import pathlib
import time
import traceback
import typing as t
import urllib.parse

import capellambse
import capellambse.model
import fastapi
import fastapi.middleware.cors
import fastapi.responses
import fastapi.staticfiles
import fastapi.templating
import jinja2
import markupsafe
import prometheus_client
import prometheus_client.registry
import pydantic

import capella_model_explorer
from capella_model_explorer.backend import model_diff
from capella_model_explorer.backend import templates as tl

FRONTEND_DIR = pathlib.Path("./frontend/dist")
TEMPLATES_DIR = pathlib.Path(os.getenv("TEMPLATES_DIR", "templates"))
ROUTE_PREFIX = os.getenv("ROUTE_PREFIX", "")
logger = logging.getLogger(__name__)


class CommitRange(pydantic.BaseModel):
    head: str
    prev: str


class ObjectDiffID(pydantic.BaseModel):
    uuid: str


def _create_diff_lookup(data, lookup=None):
    if lookup is None:
        lookup = {}
    try:
        if isinstance(data, dict):
            for _, obj in data.items():
                if "uuid" in obj:
                    lookup[obj["uuid"]] = {
                        "uuid": obj["uuid"],
                        "display_name": obj["display_name"],
                        "change": obj["change"],
                        "attributes": obj["attributes"],
                    }
                if children := obj.get("children"):
                    _create_diff_lookup(children, lookup)
    except Exception:
        logger.exception("Cannot create diff lookup")
    return lookup


def _finalize(markup: t.Any) -> object:
    markup = markupsafe.escape(markup)
    return capellambse.helpers.replace_hlinks(
        markup, app.state.model, _make_href
    )


def _make_href(
    obj: capellambse.model.ModelElement | capellambse.model.AbstractDiagram,
) -> str | None:
    if app.state.templates_index is None:
        return None

    for idx, template in app.state.templates_index.flat.items():
        if "type" in dir(template.scope):
            clsname = template.scope.type
            if obj.xtype.rsplit(":", 1)[-1] == clsname:
                return f"{ROUTE_PREFIX}/{idx}/{obj.uuid}"
    return f"{ROUTE_PREFIX}/__generic__/{obj.uuid}"


def _make_href_filter(obj: object) -> str | None:
    if jinja2.is_undefined(obj) or obj is None:
        return "#"

    if isinstance(obj, capellambse.model.ElementList):
        raise TypeError("Cannot make an href to a list of elements")
    if not isinstance(
        obj, capellambse.model.ModelElement | capellambse.model.AbstractDiagram
    ):
        raise TypeError(f"Expected a model object, got {obj!r}")

    try:
        app.state.model.by_uuid(obj.uuid)
    except KeyError:
        return "#"

    return _make_href(obj)


def _render_instance_page(template_text, base, object=None):
    try:
        # render the template with the object
        template = app.state.env.from_string(template_text)
        rendered = template.render(
            object=object,
            model=app.state.model,
            diff_data=app.state.diff,
            object_diff=app.state.object_diff,
        )
        return fastapi.responses.HTMLResponse(
            content=rendered, status_code=200
        )
    except jinja2.TemplateSyntaxError as e:
        error_message = markupsafe.Markup(
            "<p style='color:red'>Template syntax error: {}, line {}</p>"
        ).format(e.message, e.lineno)
        base.error = error_message
        print(base)
        return fastapi.responses.HTMLResponse(content=error_message)
    except Exception as e:
        logger.exception("Error rendering template")
        trace = markupsafe.escape(traceback.format_exc())
        error_message = markupsafe.Markup(
            '<p style="color:red">'
            f"Unexpected error: {type(e).__name__}: {e}"
            '</p><pre style="font-size:80%;overflow:scroll">'
            f"object={object!r}\nmodel={app.state.model!r}"
            f"\n\n{trace}"
            "</pre>"
        )
        return fastapi.responses.HTMLResponse(content=error_message)


app = fastapi.FastAPI(version=capella_model_explorer.__version__)
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = fastapi.APIRouter(prefix=ROUTE_PREFIX)
app.include_router(router)
app.mount(
    f"{ROUTE_PREFIX}/assets",
    fastapi.staticfiles.StaticFiles(directory=FRONTEND_DIR / "assets"),
)
app.mount(
    f"{ROUTE_PREFIX}/static",
    fastapi.staticfiles.StaticFiles(directory=FRONTEND_DIR / "static"),
)

try:
    MODEL_INFO = os.environ["MODEL"]
except KeyError as err:
    raise SystemExit("MODEL environment variable is not set") from err

_MODEL: capellambse.MelodyModel
try:
    _ = _MODEL
except NameError:
    _MODEL = capellambse.loadcli(MODEL_INFO)

app.state.model = _MODEL
app.state.templates = fastapi.templating.Jinja2Templates(
    directory=FRONTEND_DIR
)

app.state.templates_path = pathlib.Path(
    os.getenv("TEMPLATES_DIR", str(TEMPLATES_DIR))
)
app.state.last_interaction = time.time()
app.state.diff = {}
app.state.object_diff = {}
app.state.templates_loader = tl.TemplateLoader(app.state.model)
app.state.env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(app.state.templates_path)
)
app.state.env.finalize = _finalize
app.state.env.filters["make_href"] = _make_href_filter
app.state.templates_index = app.state.templates_loader.index_path(
    app.state.templates_path
)
app.state.idle_time_gauge = prometheus_client.Gauge(
    "idletime_minutes",
    "Time in minutes since the last user interaction",
)


@app.middleware("http")
async def update_last_interaction_time(request: fastapi.Request, call_next):
    if request.url.path not in ("/metrics", "/favicon.ico"):
        app.state.last_interaction = time.time()
    return await call_next(request)


@app.get("/metrics")
def metrics():
    idle_time_minutes = (time.time() - app.state.last_interaction) / 60
    app.state.idle_time_gauge.set(idle_time_minutes)
    return fastapi.Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )


@app.router.get("/api/commits")
async def get_commits():
    try:
        return model_diff.populate_commits(app.state.model)
    except Exception as e:
        return {"error": str(e)}


@app.router.post("/api/compare")
async def post_compare(commit_range: CommitRange):
    try:
        app.state.diff = model_diff.get_diff_data(
            app.state.model, commit_range.head, commit_range.prev
        )
        app.state.diff["lookup"] = _create_diff_lookup(
            app.state.diff["objects"]
        )
        if app.state.diff["lookup"]:
            return {"success": True}
        return {"success": False, "error": "No model changes to show"}
    except Exception as e:
        logger.exception("Failed to compare versions")
        return {"success": False, "error": str(e)}


@app.router.get("/api/diff")
async def get_diff():
    if app.state.diff:
        return app.state.diff
    return {"error": "No data available. Please compare two commits first."}


@app.router.get("/api/metadata")
async def version():
    return {"version": app.version}


@app.router.get("/api/model-info")
def model_info():
    info = app.state.model.info
    resinfo = info.resources["\x00"]
    return {
        "title": info.title,
        "revision": resinfo.revision,
        "hash": resinfo.rev_hash,
        "capella_version": info.capella_version,
        "branch": resinfo.branch,
        "badge": app.state.model.description_badge,
    }


@app.router.post("/api/object-diff")
async def post_object_diff(object_id: ObjectDiffID):
    if object_id.uuid not in app.state.diff["lookup"]:
        raise fastapi.HTTPException(status_code=404, detail="Object not found")

    app.state.object_diff = app.state.diff["lookup"][object_id.uuid]
    return {"success": True}


@app.router.get("/api/objects/{uuid}")
def read_object(uuid: str):
    obj = app.state.model.by_uuid(uuid)
    details = tl.simple_object(obj)
    return {
        "idx": details["idx"],
        "name": details["name"],
        "type": obj.xtype,
    }


@app.router.get("/api/views")
def read_templates():
    app.state.templates_index = app.state.templates_loader.index_path(
        app.state.templates_path
    )
    return app.state.templates_index.as_dict


@app.router.get("/api/views/{template_name}")
def read_template(template_name: str):
    template_name = urllib.parse.unquote(template_name)
    if (
        app.state.templates_index is None
        or template_name not in app.state.templates_index.flat
    ):
        return {
            "error": (
                f"Template {template_name} not found"
                " or templates index not initialized"
            )
        }
    base = app.state.templates_index.flat[template_name]
    base.compute_instance_list(app.state.model)
    return base


@app.router.get("/api/views/{template_name}/{object_id}")
def render_template(template_name: str, object_id: str):
    content = None
    object = None
    try:
        template_name = urllib.parse.unquote(template_name)
        if (
            app.state.templates_index is None
            or template_name not in app.state.templates_index.flat
        ):
            return {"error": f"Template {template_name} not found"}
        base = app.state.templates_index.flat[template_name]
        template_filename = base.template
        # load the template file from the templates folder
        content = (app.state.templates_path / template_filename).read_text(
            encoding="utf8"
        )
    except Exception as e:
        error_message = markupsafe.Markup(
            "<p style='color:red'>Template not found: {}</p>"
        ).format(str(e))
        return fastapi.responses.HTMLResponse(content=error_message)
    if object_id == "render":
        object = None
    else:
        try:
            object = app.state.model.by_uuid(object_id)
        except Exception as e:
            error_message = markupsafe.Markup(
                "<p style='color:red'>Requested object not found: {}</p>"
            ).format(str(e))
            return fastapi.responses.HTMLResponse(content=error_message)
    return _render_instance_page(content, base, object)


# NOTE: Next endpoint (catch-all route) must be located after all other routes!
@app.router.get("/{rest_of_path:path}")
async def catch_all(request: fastapi.Request, rest_of_path: str):
    del rest_of_path
    return app.state.templates.TemplateResponse(
        "index.html", {"request": request}
    )
