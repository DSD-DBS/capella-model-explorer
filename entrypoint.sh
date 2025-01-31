#!/bin/bash

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export CME_TEMPLATES_DIR="/app/templates"
uv run -m capella_model_explorer run local
