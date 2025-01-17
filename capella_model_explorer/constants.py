# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import dataclasses
import pathlib
import typing as t

import fasthtml.starlette
from fasthtml import common as fh
from fasthtml import ft

import capella_model_explorer as cme
from capella_model_explorer import core

CONFIG = fasthtml.starlette.Config(env_prefix="CME_")


@dataclasses.dataclass
class Defaults:
    docker_image_name: t.Final[str] = (
        f"capella-model-explorer:{cme.__version__}"
    )
    host: t.Final[str] = "0.0.0.0"
    live_mode: bool = True
    model: t.Final[str] = (
        "git+https://github.com/DSD-DBS/Capella-IFE-sample.git"
    )
    port: t.Final[int] = 8000
    route_prefix: t.Final[str] = ""
    templates_dir: t.Final[pathlib.Path] = pathlib.Path("templates")


DOCKER_IMAGE_NAME: str = CONFIG(
    "DOCKER_IMAGE_NAME", default=Defaults.docker_image_name
)
HOST: str = CONFIG("HOST", default=Defaults.host)
MODEL: str = CONFIG("MODEL", default=Defaults.model)
PORT: int = CONFIG("PORT", cast=int, default=Defaults.port)

LIVE_MODE: t.Final[bool] = CONFIG(
    "LIVE_MODE", cast=bool, default=Defaults.live_mode
)

ROUTE_PREFIX: t.Final[str] = CONFIG(
    "ROUTE_PREFIX", default=Defaults.route_prefix
)
TEMPLATES_DIR: t.Final[pathlib.Path] = CONFIG(
    "TEMPLATES_DIR",
    cast=pathlib.Path,
    default=Defaults.templates_dir.resolve(),
).resolve()

favicon_path = "static/favicon.ico"
favicon_hash = core.compute_file_hash(favicon_path)

diagramViewer_path = "static/js/diagramViewer.js"
diagramViewer_hash = core.compute_file_hash(diagramViewer_path)

theme_path = "static/js/theme.js"
theme_hash = core.compute_file_hash(theme_path)

HEADERS: t.Final[list[fh.Link | ft.Script]] = [
    fh.HighlightJS(langs=["python"]),
    fh.Link(
        rel="stylesheet",
        href=f"{ROUTE_PREFIX}/static/css/main-{cme.__version__}.min.css",
        type="text/css",
    ),
    fh.Link(
        rel="icon",
        href=f"{ROUTE_PREFIX}/static/favicon.ico?v={favicon_hash}",
        type="image/x-icon",
    ),
    ft.Script(
        charset="utf-8",
        src=(
            f"{ROUTE_PREFIX}/static/js/diagramViewer.js"
            f"?v={diagramViewer_hash}",
        ),
    ),
    ft.Script(
        charset="utf-8",
        src=f"{ROUTE_PREFIX}/static/js/plotly-3.0.0.min.js",
    ),
    ft.Script(
        charset="utf-8",
        src=f"{ROUTE_PREFIX}/static/js/theme.js?v={theme_hash}",
    ),
]
LOGGING_COLORS = {
    "WARNING": "\033[33m",  # yellow
    "INFO": "\033[32m",  # green
    "DEBUG": "\033[3;90m",  # Italic and dark gray
    "CRITICAL": "\033[1;31m",  # Bold and red
    "ERROR": "\033[31m",  # red
}
