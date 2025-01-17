/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
var modelObjBtns = document.querySelectorAll(".model_object_btn");
for (var modelObjBtn of modelObjBtns) {
  modelObjBtn.addEventListener("click", function () {
    for (var element of modelObjBtns) {
      element.setAttribute("aria-selected", element == this);
    }
  });
}
