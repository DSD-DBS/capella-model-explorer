# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib
import pathlib
import typing as t

import capellambse
import pytest
from starlette import testclient

from capella_model_explorer import app as app_module
from capella_model_explorer import constants, state


@pytest.fixture
def server(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> t.Iterator[testclient.TestClient]:
    """Run the application with the built-in coffee-machine model."""
    route_prefix = getattr(request, "param", "")
    monkeypatch.setattr(constants, "MODEL", "coffee-machine")
    monkeypatch.setattr(constants, "ROUTE_PREFIX", route_prefix)
    model_info = capellambse.loadinfo("coffee-machine")
    local_model = (
        pathlib.Path(__file__).parents[2]
        / "capellambse/tests/data/models/test7_0/Model Test 7.0.aird"
    )
    if local_model.is_file():
        model_info["path"] = local_model
    monkeypatch.setattr(app_module.capellambse, "loadinfo", lambda _: model_info)

    original_model = state.model
    original_templates = state.templates[:]
    original_categories = state.template_categories[:]
    state.templates.clear()
    state.template_categories.clear()

    importlib.reload(app_module)
    try:
        with testclient.TestClient(app_module.app) as client:
            yield client
    finally:
        state.model = original_model
        state.templates[:] = original_templates
        state.template_categories[:] = original_categories
        monkeypatch.undo()
        importlib.reload(app_module)
