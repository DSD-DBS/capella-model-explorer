# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from pathlib import Path

import capellambse
import pytest

from capella_model_explorer.backend.templates import (
    Template,
    TemplateCategory,
    TemplateLoader,
    find_objects,
)

TEST_SYSTEM_COMPONENT_UUIDS = {
    "5357012d-0479-49d3-a6e7-26c0da89fed7",
    "20b7666e-9810-4a3f-82f8-a6088c6ebdf0",
    "11790d2d-4b5f-48ea-a2c3-7f53cf7eda21",
}


def test_template_loading():
    template_raw = {
        "idx": "test",
        "name": "Test Template",
        "template": "test_template.jinja",
        "description": "This is a test template",
        "scope": {"type": "System", "below": "System"},
    }
    Template(**template_raw)


def test_category_loading():
    template_raw = {
        "idx": "test",
        "name": "Test Template",
        "template": "test_template.jinja",
        "description": "This is a test template",
        "scope": {"type": "System", "below": "System"},
    }
    category_raw = {
        "idx": "test",
        "templates": [template_raw],
    }
    TemplateCategory(**category_raw)


def test_index_templates():
    model = capellambse.loadcli("coffee-machine")

    templates = TemplateLoader(model).index_path(Path("tests"))

    assert len(templates.flat) == 3
    assert len(templates) == 1


@pytest.mark.parametrize(
    ("params", "expected_uuids"),
    [
        pytest.param(
            {"obj_type": "SystemComponent", "below": "sa"},
            TEST_SYSTEM_COMPONENT_UUIDS,
            id="Test below",
        ),
        pytest.param(
            {"obj_type": "SystemComponent", "filters": {"is_actor": True}},
            TEST_SYSTEM_COMPONENT_UUIDS
            - {"5357012d-0479-49d3-a6e7-26c0da89fed7"},
            id="Test filters",
        ),
        pytest.param(
            {"obj_type": "SystemComponent", "attr": "sa.all_components"},
            TEST_SYSTEM_COMPONENT_UUIDS,
            id="Test attr",
        ),
    ],
)
def test_find_objects(params: dict[str, t.Any], expected_uuids: list[str]):
    model = capellambse.loadcli("coffee-machine")

    objects = find_objects(model, **params)

    assert {obj.uuid for obj in objects} == expected_uuids
