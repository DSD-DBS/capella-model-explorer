# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import typing as t

from fasthtml import common as fh
from fasthtml import ft

import capella_model_explorer as cme

# defaults that are shared with the cli (`__main__.py`)
LIVE_MODE_DEFAULT: t.Final[str] = "1"
ROUTE_PREFIX_DEFAULT: t.Final[str] = ""

LIVE_MODE: t.Final[bool] = os.getenv("CME_LIVE_MODE", LIVE_MODE_DEFAULT) != "0"
ROUTE_PREFIX: t.Final[str] = os.getenv(
    "CME_ROUTE_PREFIX", ROUTE_PREFIX_DEFAULT
)


HEADERS: t.Final[list[fh.Link | ft.Script]] = [
    fh.Link(
        rel="stylesheet",
        href=f"{ROUTE_PREFIX}/static/css/main-{cme.__version__}.min.css",
        type="text/css",
    ),
    fh.Link(
        rel="icon",
        href=f"{ROUTE_PREFIX}/static/favicon.ico",
        type="image/x-icon",
    ),
    ft.Script(
        src=f"{ROUTE_PREFIX}/static/js/theme.js",
    ),
]
FASTHTML_APP_CONFIG: t.Final[dict] = {
    "hdrs": HEADERS,
    "key_fname": "/tmp/.sesskey",
    "pico": False,
    "live": LIVE_MODE,
}
