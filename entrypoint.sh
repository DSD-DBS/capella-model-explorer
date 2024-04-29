#!/bin/bash

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

sed -i "s|__ROUTE_PREFIX__|${ROUTE_PREFIX}|g" ./frontend/dist/static/env.js
sed -i "s|href=\"/|href=\"${ROUTE_PREFIX}/|g" ./frontend/dist/index.html
sed -i "s|src=\"/|src=\"${ROUTE_PREFIX}/|g" ./frontend/dist/index.html

exec python -m capella_model_explorer.backend ${MODEL_ENTRYPOINT} /views
