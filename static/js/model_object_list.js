var lightModeOtherButtons = ["bg-slate-200", "hover:bg-slate-100"];
var darkModeOtherButtons = ["dark:bg-neutral-800", "dark:hover:bg-neutral-700"];
var clickedButton = ["bg-blue-500", "dark:text-white", "text-white"];
var allClasses = [
  ...lightModeOtherButtons,
  ...darkModeOtherButtons,
  ...clickedButton,
];
document.querySelectorAll(".model_object_btn").forEach((item) => {
  item.addEventListener("click", function () {
    document.querySelectorAll(".model_object_btn").forEach((i) => {
      for (const cls of allClasses) {
        i.classList.remove(cls);
      }
      if (i !== this) {
        for (const cls of [...lightModeOtherButtons, ...darkModeOtherButtons]) {
          i.classList.add(cls);
        }
      }
    });
    // current button
    for (const cls of clickedButton) {
      this.classList.add(cls);
    }
  });
});
