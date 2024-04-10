#!/bin/bash

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

find "./frontend/dist/assets" -type f -name '*.js' -print0 | xargs -0 sed -i "s|__ROUTE_PREFIX__|$ROUTE_PREFIX|g"
sed -i "s|href=\"/|href=\"${ROUTE_PREFIX}/|g" ./frontend/dist/index.html
sed -i "s|src=\"/|src=\"${ROUTE_PREFIX}/|g" ./frontend/dist/index.html
exec "$@"
