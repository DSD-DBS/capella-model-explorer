/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

(function () {
  const query = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme(...args) {
    document.documentElement.classList.toggle("dark", query.matches);
  }

  query.addEventListener("change", applyTheme);
  window.addEventListener("DOMContentLoaded", applyTheme);
})();
