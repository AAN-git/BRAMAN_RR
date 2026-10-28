/* Version 4 — the dealer's menu (css/menu_v4.css): a group's caret opens its
   list and closes any other; a group with no page of its own opens by its
   name; a press elsewhere or Escape closes them all. In the bar (from 1024,
   no carets) the pointer opens a list by resting on it and the keyboard by
   focus; a touch screen's first press on a name shows its list as a hover
   (Safari's own behaviour for content shown on hover). Browsers can report
   no hover with a mouse attached, so nothing here asks. */
(function () {
  var groups = document.querySelectorAll(".header__group");
  if (!groups.length) return;

  function set(group, open) {
    var button = group.querySelector(".header__more");
    if (open) group.setAttribute("data-open", ""); else group.removeAttribute("data-open");
    if (button) button.setAttribute("aria-expanded", open ? "true" : "false");
  }
  function closeAll(except) {
    groups.forEach(function (g) { if (g !== except) set(g, false); });
  }

  // the list hangs from the bar's foot: the gap from the name's foot to it
  var bar = document.querySelector(".header");
  function hang(group) {
    if (!bar) return;
    var gap = bar.getBoundingClientRect().bottom - group.getBoundingClientRect().bottom;
    group.style.setProperty("--drop-gap", Math.max(0, Math.round(gap)) + "px");
  }

  groups.forEach(function (group) {
    var button = group.querySelector(".header__more");
    group.addEventListener("mouseenter", function () { hang(group); });
    group.addEventListener("focusin", function () { hang(group); });
    // the pointer leaving a group closes a list a press had opened
    group.addEventListener("mouseleave", function () { if (!bar || !bar.hasAttribute("data-open")) set(group, false); });
    var name = group.querySelector(".header__group-name");
    function toggle(e) {
      e.stopPropagation();
      var open = !group.hasAttribute("data-open");
      closeAll(group);
      hang(group);
      set(group, open);
    }
    if (button) button.addEventListener("click", toggle);
    if (name) name.addEventListener("click", toggle);
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest || !e.target.closest(".header__group")) closeAll(null);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAll(null);
  });
})();
