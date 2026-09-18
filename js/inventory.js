/* Rolls-Royce Motor Cars Palm Beach — inventory.
   Four picks over the cards already in the page: year, make, model, sort.
   The cards carry their facts as data attributes (generated from
   data/inventory.json, as are the option lists), so a feed can replace the
   markup later and this file will not need to know. */

(function () {
  "use strict";

  var grid = document.getElementById("grid");
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
  var picks = Array.prototype.slice.call(document.querySelectorAll("[data-pick]"));
  var select = document.querySelector(".sort__select");
  var count = document.querySelector("[data-count]");
  var empty = document.querySelector(".srp__empty");
  var query = empty.querySelector("[data-query]");
  var clear = empty.querySelector(".srp__clear");
  var motion = document.documentElement.classList.contains("motion");

  /* Every card remembers where the page put it, so "Featured" is that order. */
  cards.forEach(function (card, i) { card.dataset.featured = i; });

  var sorters = {
    "featured":   function (a, b) { return +a.dataset.featured - +b.dataset.featured; },
    "price-asc":  function (a, b) { return +a.dataset.price - +b.dataset.price; },
    "price-desc": function (a, b) { return +b.dataset.price - +a.dataset.price; },
    "year-desc":  function (a, b) { return +b.dataset.year - +a.dataset.year; },
    "model":      function (a, b) { return a.dataset.model.localeCompare(b.dataset.model); }
  };

  /* A pick left on its first option asks for nothing. Make has one option —
     every card is a Rolls-Royce — so it never narrows. */
  function matches(card) {
    return picks.every(function (p) {
      var want = p.value;
      if (!want) return true;
      var have = card.dataset[p.dataset.pick];
      return have === undefined || have === want;
    });
  }

  var pending = 0;

  function render() {
    var sorter = sorters[select.value] || sorters.featured;
    var shown = cards.filter(matches).sort(sorter);

    /* Off, reorder, then on — so the staircase plays from the new order. */
    if (motion) cards.forEach(function (c) { c.classList.add("is-off"); });

    window.clearTimeout(pending);
    pending = window.setTimeout(function () {
      cards.forEach(function (c) { c.hidden = shown.indexOf(c) === -1; });
      shown.forEach(function (c, i) {
        grid.appendChild(c);
        c.style.setProperty("--i", i);
      });
      count.textContent = shown.length;
      empty.hidden = shown.length > 0;
      query.textContent = picks.filter(function (p) { return p.value; })
        .map(function (p) { return p.options[p.selectedIndex].textContent; })
        .join(" · ") || "your choice";
      if (motion) {
        /* two frames: the off state has to paint before it transitions */
        window.requestAnimationFrame(function () {
          window.requestAnimationFrame(function () {
            shown.forEach(function (c) { c.classList.remove("is-off"); });
          });
        });
      }
    }, motion ? 40 : 0);
  }

  picks.forEach(function (p) { p.addEventListener("change", render); });
  select.addEventListener("change", render);
  clear.addEventListener("click", function () {
    picks.forEach(function (p) { p.value = ""; });
    render();
    picks[0].focus();
  });

  /* First paint: the cards climb in. */
  if (motion) {
    cards.forEach(function (c, i) { c.classList.add("is-off"); c.style.setProperty("--i", i); });
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        cards.forEach(function (c) { c.classList.remove("is-off"); });
      });
    });
  }
})();
