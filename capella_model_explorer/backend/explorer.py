# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import typing as t
from pathlib import Path

import capellambse
from fastapi import FastAPI
from jinja2 import Environment

from . import routes


@dataclasses.dataclass
class CapellaModelExplorerBackend:
    app: FastAPI = dataclasses.field(init=False)
    env: Environment = dataclasses.field(init=False)
    templates: dict[str, t.Any] = dataclasses.field(
        init=False, default_factory=dict
    )

    templates_path: Path
    model: capellambse.MelodyModel

    def __post_init__(self):
        self.app = FastAPI()
        self.env = Environment()
        self.templates = routes.index_templates(self.templates_path)

        routes.configure_routes(self)
