/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

var API_BASE_URL = window.env.API_BASE_URL;
var ROUTE_PREFIX = window.env.ROUTE_PREFIX;
if (!process.env.NODE_ENV || process.env.NODE_ENV === "development") {
    API_BASE_URL = "http://localhost:8000/api";
    ROUTE_PREFIX = "";
}
export { API_BASE_URL, ROUTE_PREFIX };
