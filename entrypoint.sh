#!/bin/bash

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export MODEL="${MODEL_ENTRYPOINT}"
export TEMPLATES_DIR="/app/templates"
source .venv/bin/activate
if [ "$LIVE" = "1" ]; then
    make dev
else
    make run
fi
