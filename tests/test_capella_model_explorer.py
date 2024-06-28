# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import capellambse
from pathlib import Path
from capella_model_explorer.backend.templates import TemplateLoader, Template, TemplateCategory


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
