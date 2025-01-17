/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

const darkModeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

function handleThemeChange(event) {
  document.documentElement.classList.toggle("dark", event.matches);
}
handleThemeChange(darkModeMediaQuery);
darkModeMediaQuery.addEventListener("change", handleThemeChange);
