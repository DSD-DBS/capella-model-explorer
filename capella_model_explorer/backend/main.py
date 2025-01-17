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
import capellambse.model as m
import fastapi
import fastapi.middleware.cors
import fastapi.responses
import fastapi.staticfiles
import fastapi.templating
import jinja2
import markupsafe
import prometheus_client
import pydantic

import capella_model_explorer
from capella_model_explorer.backend import model_diff, state
from capella_model_explorer.backend import templates as tl

FRONTEND_DIR = pathlib.Path("./frontend/dist")
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
    return capellambse.helpers.replace_hlinks(markup, state.model, _make_href)


def _make_href(
    obj: m.ModelElement | m.AbstractDiagram,
) -> str | None:
    if state.templates_index is None:
        return None

    for idx, template in state.templates_index.flat.items():
        if "type" in dir(template.scope):
            clsname = template.scope.type
            if obj.xtype.rsplit(":", 1)[-1] == clsname:
                return f"{ROUTE_PREFIX}/{idx}/{obj.uuid}"
    return f"{ROUTE_PREFIX}/__generic__/{obj.uuid}"


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


def _render_instance_page(template_text, base, object=None):
    try:
        # render the template with the object
        template = state.jinja_env.from_string(template_text)
        rendered = template.render(
            object=object,
            model=state.model,
            diff_data=state.diff,
            object_diff=state.object_diff,
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
            f"object={object!r}\nmodel={state.model!r}"
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

try:
    _ = state.model
except AttributeError:
    state.model = capellambse.loadcli(MODEL_INFO)

state.templates = fastapi.templating.Jinja2Templates(directory=FRONTEND_DIR)

state.templates_loader = tl.TemplateLoader(state.model)
state.jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(state.templates_path)
)
state.jinja_env.finalize = _finalize
state.jinja_env.filters["make_href"] = _make_href_filter
state.templates_index = state.templates_loader.index_path(state.templates_path)


@app.middleware("http")
async def update_last_interaction_time(request: fastapi.Request, call_next):
    if request.url.path not in ("/metrics", "/favicon.ico"):
        state.last_interaction = time.time()
    return await call_next(request)


@app.get("/metrics")
def metrics():
    idle_time_minutes = (time.time() - state.last_interaction) / 60
    state.idle_time_gauge.set(idle_time_minutes)
    return fastapi.Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )


@router.get("/api/commits")
async def get_commits():
    try:
        return model_diff.populate_commits(state.model)
    except Exception as e:
        return {"error": str(e)}


@router.post("/api/compare")
async def post_compare(commit_range: CommitRange):
    try:
        state.diff = model_diff.get_diff_data(
            state.model, commit_range.head, commit_range.prev
        )
        state.diff["lookup"] = _create_diff_lookup(state.diff["objects"])
        if state.diff["lookup"]:
            return {"success": True}
        return {"success": False, "error": "No model changes to show"}
    except Exception as e:
        logger.exception("Failed to compare versions")
        return {"success": False, "error": str(e)}


@router.get("/api/diff")
async def get_diff():
    if state.diff:
        return state.diff
    return {"error": "No data available. Please compare two commits first."}


@router.get("/api/metadata")
async def version():
    return {"version": app.version}


@router.get("/api/model-info")
def model_info():
    info = state.model.info
    resinfo = info.resources["\x00"]
    return {
        "title": info.title,
        "revision": resinfo.revision,
        "hash": resinfo.rev_hash,
        "capella_version": info.capella_version,
        "branch": resinfo.branch,
        "badge": state.model.description_badge,
    }


@router.post("/api/object-diff")
async def post_object_diff(object_id: ObjectDiffID):
    if object_id.uuid not in state.diff["lookup"]:
        raise fastapi.HTTPException(status_code=404, detail="Object not found")

    state.object_diff = state.diff["lookup"][object_id.uuid]
    return {"success": True}


@router.get("/api/objects/{uuid}")
def read_object(uuid: str):
    obj = state.model.by_uuid(uuid)
    details = tl.simple_object(obj)
    return {
        "idx": details["idx"],
        "name": details["name"],
        "type": obj.xtype,
    }


@router.get("/api/views")
def read_templates():
    state.templates_index = state.templates_loader.index_path(
        state.templates_path
    )
    return state.templates_index.as_dict


@router.get("/api/views/{template_name}")
def read_template(template_name: str):
    template_name = urllib.parse.unquote(template_name)
    if (
        state.templates_index is None
        or template_name not in state.templates_index.flat
    ):
        return {
            "error": (
                f"Template {template_name} not found"
                " or templates index not initialized"
            )
        }
    base = state.templates_index.flat[template_name]
    base.compute_instance_list(state.model)
    return base


@router.get("/api/views/{template_name}/{object_id}")
def render_template(template_name: str, object_id: str):
    content = None
    object = None
    try:
        template_name = urllib.parse.unquote(template_name)
        if (
            state.templates_index is None
            or template_name not in state.templates_index.flat
        ):
            return {"error": f"Template {template_name} not found"}
        base = state.templates_index.flat[template_name]
        template_filename = base.template
        # load the template file from the templates folder
        content = (state.templates_path / template_filename).read_text(
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
            object = state.model.by_uuid(object_id)
        except Exception as e:
            error_message = markupsafe.Markup(
                "<p style='color:red'>Requested object not found: {}</p>"
            ).format(str(e))
            return fastapi.responses.HTMLResponse(content=error_message)
    return _render_instance_page(content, base, object)


# NOTE: Next endpoint (catch-all route) must be located after all other routes!
@router.get("/{rest_of_path:path}")
async def catch_all(request: fastapi.Request, rest_of_path: str):
    del rest_of_path
    return state.templates.TemplateResponse("index.html", {"request": request})


app.include_router(router)
