/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import "bigger-picture/dist/bigger-picture.css";
import BiggerPicture from "bigger-picture/dist/bigger-picture.mjs";

import "mdui/mdui.css";
import * as mdui from "mdui";

import "./compiled.css";

window.mdui = mdui;

window.openDiagramViewer = function (svgContainer) {
  if (typeof window.lightbox === "undefined") {
    window.lightbox = BiggerPicture({ target: document.body });
  }
  lightbox.open({ items: [svgContainer], el: svgContainer });
};

window.addEventListener("load", function () {
  mdui.setColorScheme("#4f008b", {
    customColors: [
      { name: "layer-oa", value: "#ffdd87" },
      { name: "layer-sa", value: "#91cc84" },
      { name: "layer-la", value: "#a5c2e6" },
      { name: "layer-pa", value: "#f89f9f" },
      { name: "chip-experimental", value: "#fef9c2" },
      { name: "chip-document", value: "#bedbff" },
      { name: "chip-stable", value: "#dcfce7" },
    ],
  });
});
