#!/bin/bash

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export CME_TEMPLATES_DIR="/templates"
. /app/.venv/bin/activate
exec cme run --skip-rebuild "$@"
