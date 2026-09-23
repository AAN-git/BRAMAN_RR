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

  /* --- The route ---------------------------------------------------------
     The home page's doors arrive with the choice already made:
     ?model=ghost&new · ?trim=black-badge&provenance · ?new · ?provenance.
     A model the picks already carry is set on the pick, so the visitor sees
     it where they would have chosen it; condition and trim have no pick of
     their own and are held here, named above the grid, and dropped by
     "Show all". Without a query none of this exists and the page is the
     page it was. */
  var routeLine = document.querySelector(".srp__route");
  var routeName = routeLine && routeLine.querySelector("[data-route]");
  var routeClear = routeLine && routeLine.querySelector(".srp__route-clear");
  var route = {};                      /* { condition: "new", trim: "Black Badge" } */

  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-"); }

  function readRoute() {
    var q = new URLSearchParams(window.location.search);
    var words = [];
    if (q.has("new")) { route.condition = "new"; words.push("new"); }
    else if (q.has("provenance") || q.get("condition") === "used") { route.condition = "used"; words.push("Provenance pre-owned"); }
    else if (q.get("condition") === "new") { route.condition = "new"; words.push("new"); }

    var wanted = q.get("model");
    if (wanted) {
      var pick = picks.filter(function (p) { return p.dataset.pick === "model"; })[0];
      var option = pick && Array.prototype.filter.call(pick.options, function (o) { return slug(o.value) === slug(wanted); })[0];
      if (option) { pick.value = option.value; words.push(option.value); }
      else { route.model = wanted; words.push(wanted); }
    }
    var trim = q.get("trim");
    if (trim) {
      var match = cards.map(function (c) { return c.dataset.trim; })
        .filter(function (t) { return t && slug(t) === slug(trim); })[0];
      if (match) { route.trim = match; words.push(match); }
    }
    if (routeLine && words.length) {
      routeName.textContent = words.join(" · ");
      routeLine.hidden = false;
    }
  }

  /* A pick left on its first option asks for nothing. Make has one option —
     every card is a Rolls-Royce — so it never narrows. */
  function matches(card) {
    for (var key in route) {
      if (!Object.prototype.hasOwnProperty.call(route, key)) continue;
      var have = card.dataset[key];
      if (key === "trim" ? String(have).indexOf(route[key]) === -1 : slug(have) !== slug(route[key])) return false;
    }
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
  function showAll() {
    route = {};
    picks.forEach(function (p) { p.value = ""; });
    if (routeLine) routeLine.hidden = true;
    if (window.history.replaceState) window.history.replaceState(null, "", window.location.pathname);
    render();
  }
  clear.addEventListener("click", function () { showAll(); picks[0].focus(); });
  if (routeClear) routeClear.addEventListener("click", function () { showAll(); picks[0].focus(); });

  readRoute();
  if (Object.keys(route).length || picks.some(function (p) { return p.value; })) render();

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
