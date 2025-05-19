#!/bin/bash

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export CME_TEMPLATES_DIR="/templates"
exec /app/bin/cme run --skip-rebuild "$@"
