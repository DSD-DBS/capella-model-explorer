# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import pathlib
import time
import typing as t

import jinja2
import prometheus_client
import pydantic

from capella_model_explorer import templates as tl

if t.TYPE_CHECKING:
    import capellambse


class Breadcrumb(pydantic.BaseModel):
    label: str
    url: str


breadcrumbs: list[Breadcrumb] | None = None
idle_time_gauge = prometheus_client.Gauge(
    "idletime_minutes",
    "Time in minutes since the last user interaction",
)
last_interaction = time.time()
model: capellambse.MelodyModel
model_element: t.Any = None
diff: dict = {}
object_diff: dict = {}

search: str = ""
show_uuids: bool = False
template: tl.Template | None = None
"""Active template"""

templates: list[tl.Template] = []
template_categories: list[tl.TemplateCategory] = []
templates_path: t.Final[pathlib.Path] = pathlib.Path(
    os.getenv("TEMPLATES_DIR", "templates")
)
jinja_env: t.Final[jinja2.Environment] = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates_path)
)
