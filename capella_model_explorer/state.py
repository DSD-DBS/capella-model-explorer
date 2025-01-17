# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import time
import typing as t

import prometheus_client

if t.TYPE_CHECKING:
    import capellambse
    import jinja2

    from capella_model_explorer import reports

jinja_env: jinja2.Environment


idle_time_gauge = prometheus_client.Gauge(
    "idletime_minutes",
    "Time in minutes since the last user interaction",
)
last_interaction = time.time()
model: capellambse.MelodyModel

show_uuids: bool = False

templates: list[reports.Template] = []
template_categories: list[reports.TemplateCategory] = []
