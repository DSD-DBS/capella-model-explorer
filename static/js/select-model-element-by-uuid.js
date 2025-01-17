document.addEventListener("DOMContentLoaded", function () {
  var btn = document.getElementById("model-element-{uuid}");
  if (btn) {
    btn.classList.toggle("transition");
    btn.click();
    btn.classList.toggle("transition");
    btn.scrollIntoView({ behavior: "auto", block: "center" });
  }
});
