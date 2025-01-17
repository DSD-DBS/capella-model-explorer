# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import pathlib
import time
import typing as t

import prometheus_client

if t.TYPE_CHECKING:
    import capellambse
    import fastapi.templating
    import jinja2

    import capella_model_explorer.backend.templates

diff: dict = {}
idle_time_gauge = prometheus_client.Gauge(
    "idletime_minutes",
    "Time in minutes since the last user interaction",
)
jinja_env: jinja2.Environment
last_interaction = time.time()
model: capellambse.MelodyModel
object_diff: dict = {}
templates: fastapi.templating.Jinja2Templates
templates_loader: capella_model_explorer.backend.templates.TemplateLoader
templates_index: (
    capella_model_explorer.backend.templates.TemplateCategories | None
)
templates_path = pathlib.Path(os.getenv("TEMPLATES_DIR", "templates"))
