/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

var API_BASE_URL = "http://localhost:8000__ROUTE_PREFIX__/api";
var ROUTE_PREFIX = "__ROUTE_PREFIX__";
if (!process.env.NODE_ENV || process.env.NODE_ENV === "development") {
    API_BASE_URL = "http://localhost:8000/api";
    ROUTE_PREFIX = "";
}
export { API_BASE_URL, ROUTE_PREFIX };
