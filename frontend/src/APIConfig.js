/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

export const ROUTE_PREFIX = window.env?.ROUTE_PREFIX ?? '';
export const API_BASE_URL =
  window.env?.API_BASE_URL ?? `http://localhost:8000${ROUTE_PREFIX}/api`;
