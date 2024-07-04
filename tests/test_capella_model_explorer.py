# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from pathlib import Path

import capellambse
import pytest

from capella_model_explorer.backend import explorer
from capella_model_explorer.backend.templates import (
    Template,
    TemplateCategory,
    TemplateLoader,
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
    template = Template(**template_raw)


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
    category = TemplateCategory(**category_raw)


def test_index_templates():
    model = capellambse.loadcli("coffee-machine")

    templates = TemplateLoader(model).index_path(Path("."))

    assert len(templates.flat) == 3
    assert len(templates) == 1
