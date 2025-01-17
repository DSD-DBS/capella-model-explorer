/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
document.querySelectorAll(".model_object_btn").forEach((item) => {
  item.addEventListener("click", function () {
    document.querySelectorAll(".model_object_btn").forEach((element) => {
      element.setAttribute("aria-selected", element == this);
    });
  });
});
