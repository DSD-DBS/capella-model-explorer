/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

function openDiagramViewer(svgContainer) {
  const plotlyChart = svgContainer.nextElementSibling;
  if (!plotlyChart.classList.contains("plotly-chart")) {
    console.error(
      "clicked svg container is not followed by a plotly container!",
    );
    return;
  }
  plotlyChart.innerHTML = "";
  plotlyChart.style.display = "block";

  const svgElement = svgContainer.firstElementChild;
  const svg_width = parseFloat(svgElement.getAttribute("width")) + 2;
  const svg_height = parseFloat(svgElement.getAttribute("height")) + 2;
  const svgData = svgElement.outerHTML;
  const svgDataUrl =
    "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgData);
  const data = [];
  const layout = {
    images: [
      {
        source: svgDataUrl,
        x: -svg_width / 2,
        y: -svg_height / 2,
        sizex: svg_width,
        sizey: svg_height,
        xref: "x",
        yref: "y",
        xanchor: "left",
        yanchor: "bottom",
        sizing: "stretch",
      },
    ],
    autosize: true,
    margin: { l: 0, r: 0, b: 0, t: 0 },
    width: parseInt(plotlyChart.getAttribute("width")),
    xaxis: {
      range: [-svg_width / 2, svg_width / 2],
      autorange: false,
      visible: false,
    },
    yaxis: {
      range: [-svg_height / 2, svg_height / 2],
      autorange: false,
      scaleanchor: "x",
      scaleratio: 1,
      visible: false,
    },
    plot_bgcolor: "transparent",
    paper_bgcolor: "transparent",
    dragmode: "pan",
  };
  var printIcon = {
    width: 500,
    height: 500,
    name: "Print",
    path: "M128 0C92.7 0 64 28.7 64 64l0 96 64 0 0-96 226.7 0L384 93.3l0 66.7 64 0 0-66.7c0-17-6.7-33.3-18.7-45.3L400 18.7C388 6.7 371.7 0 354.7 0L128 0zM384 352l0 32 0 64-256 0 0-64 0-16 0-16 256 0zm64 32l32 0c17.7 0 32-14.3 32-32l0-96c0-35.3-28.7-64-64-64L64 192c-35.3 0-64 28.7-64 64l0 96c0 17.7 14.3 32 32 32l32 0 0 64c0 35.3 28.7 64 64 64l256 0c35.3 0 64-28.7 64-64l0-64zM432 248a24 24 0 1 1 0 48 24 24 0 1 1 0-48z",
  };
  var closeIcon = {
    width: 500,
    height: 500,
    path: "M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z",
  };

  var config = {
    toImageButtonOptions: {
      format: "svg", // one of png, svg, jpeg, webp
      filename: svgContainer.dataset.diagramTitle,
    },
    modeBarButtonsToRemove: ["autoScale2d"],
    modeBarButtonsToAdd: [
      {
        name: "Print",
        icon: printIcon,
        click: function () {
          Plotly.toImage(plotlyChart, { format: "svg" })
            .then(function (dataUrl) {
              var windowContent = "<!DOCTYPE html>";
              windowContent += "<html>";
              windowContent += "<head><title>Diagram</title></head>";
              windowContent += "<body>";
              if (svg_width >= svg_height) {
                windowContent +=
                  '<img src="' + dataUrl + '" style="width:100% !important;">';
              } else {
                windowContent +=
                  '<img src="' +
                  dataUrl +
                  '" style="height:100% !important;">';
              }
              windowContent += "</body>";
              windowContent += "</html>";
              var printWindow = window.open("", "", "width=800,height=600");
              printWindow.document.open();
              printWindow.document.write(windowContent);
              printWindow.document.close();
              printWindow.focus();
              printWindow.onload = function () {
                printWindow.print();
                printWindow.close();
              };
            })
            .catch(function (error) {
              console.error("Error generating image for print:", error);
            });
        },
      },
      {
        name: "Close",
        icon: closeIcon,
        click: function () {
          const charts = document.querySelectorAll(".plotly-chart");
          for (var chart of charts) {
            chart.style.display = "none";
          }
        },
      },
    ],
    scrollZoom: true,
    displayModeBar: true,
    displaylogo: false,
    responsive: true,
  };

  Plotly.newPlot(plotlyChart, data, layout, config);
}

document.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    const charts = document.querySelectorAll(".plotly-chart");
    for (var chart of charts) {
      chart.style.display = "none";
    }
  }
});
