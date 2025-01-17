# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import time
import typing as t

import jinja2
import prometheus_client
import pydantic

from capella_model_explorer import reports

if t.TYPE_CHECKING:
    import capellambse

JINJA_ENV: jinja2.Environment


class Breadcrumb(pydantic.BaseModel):
    label: str
    url: str


idle_time_gauge = prometheus_client.Gauge(
    "idletime_minutes",
    "Time in minutes since the last user interaction",
)
last_interaction = time.time()
model: capellambse.MelodyModel
models: dict[str, capellambse.MelodyModel]

show_uuids: bool = False

templates: list[reports.Template] = []
template_categories: list[reports.TemplateCategory] = []
