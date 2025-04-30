# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import dataclasses
import importlib.resources as imr
import pathlib
import sys
import typing as t

import fasthtml.starlette
from fasthtml import common as fh
from fasthtml import ft

from capella_model_explorer import core

CONFIG = fasthtml.starlette.Config(env_prefix="CME_")


@dataclasses.dataclass
class Defaults:
    docker_image_name: t.Final[str] = "capella-model-explorer:latest"
    host: t.Final[str] = "0.0.0.0"
    live_mode: bool = True
    model: t.Final[str] = (
        "git+https://github.com/DSD-DBS/Capella-IFE-sample.git"
    )
    port: t.Final[int] = 8000
    primary_color_hue: t.Final[int] = 231
    route_prefix: t.Final[str] = ""
    templates_dir: t.Final[pathlib.Path] = pathlib.Path("templates")


DOCKER_IMAGE_NAME: str = CONFIG(
    "DOCKER_IMAGE_NAME", default=Defaults.docker_image_name
)
HOST: str = CONFIG("HOST", default=Defaults.host)
MODEL: str = CONFIG("MODEL", default=Defaults.model)
PORT: int = CONFIG("PORT", cast=int, default=Defaults.port)
PRIMARY_COLOR_HUE: int = CONFIG(
    "PRIMARY_COLOR_HUE", cast=int, default=Defaults.primary_color_hue
)
LIVE_MODE: t.Final[bool] = CONFIG(
    "LIVE_MODE", cast=bool, default=Defaults.live_mode
)

ROUTE_PREFIX: t.Final[str] = CONFIG(
    "ROUTE_PREFIX", default=Defaults.route_prefix
).rstrip("/")
TEMPLATES_DIR: t.Final[pathlib.Path] = CONFIG(
    "TEMPLATES_DIR",
    cast=pathlib.Path,
    default=Defaults.templates_dir.resolve(),
).resolve()

diagram_viewer_path = "static/js/diagramViewer.js"
diagram_viewer_hash = core.compute_file_hash(diagram_viewer_path)

favicon_path = "static/favicon.svg"
favicon_hash = core.compute_file_hash(favicon_path)

main_css_path = "static/css/main.min.css"
main_css_hash = core.compute_file_hash(main_css_path)

HEADERS: t.Final[list[fh.Link | ft.Script]] = [
    fh.HighlightJS(langs=["python"]),
    fh.Link(
        rel="stylesheet",
        href=f"{ROUTE_PREFIX}/{main_css_path}?v={main_css_hash}",
        type="text/css",
    ),
    fh.Link(
        rel="icon",
        href=f"{ROUTE_PREFIX}/{favicon_path}?v={favicon_hash}",
        type="image/x-icon",
    ),
    ft.Script(
        charset="utf-8",
        src=f"{ROUTE_PREFIX}/{diagram_viewer_path}?v={diagram_viewer_hash}",
    ),
    ft.Script(
        charset="utf-8",
        src=f"{ROUTE_PREFIX}/static/js/plotly-3.0.0.min.js",
    ),
    ft.Script(
        imr.read_text(__name__.rsplit(".", 1)[0], "inline-dark-mode.js")
    ),
    ft.Style(f":root {{ --primary-color-hue: {PRIMARY_COLOR_HUE}; }}"),
]
if sys.stderr.isatty():
    LOGGING_COLORS = {
        "CRITICAL": "\x1b[1;31m",  # Bold and red
        "ERROR": "\x1b[31m",  # red
        "WARNING": "\x1b[33m",  # yellow
        "INFO": "\x1b[32m",  # green
        "DEBUG": "\x1b[3;90m",  # Italic and dark gray
        "RESET": "\x1b[m",
    }
else:
    LOGGING_COLORS = {
        "CRITICAL": "",
        "ERROR": "",
        "WARNING": "",
        "INFO": "",
        "DEBUG": "",
        "RESET": "",
    }
