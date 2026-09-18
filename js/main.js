/* Rolls-Royce Motor Cars Palm Beach — home.
   No dependencies. Every behaviour here has a complete static equivalent:
   with JS off the sections stand in their final composition, the films show
   their posters, and the header keeps white ink. */

(function () {
  "use strict";

  var root = document.documentElement;
  /* The entrance states in the stylesheet wait for this class: if this file
     never loads, the page is simply the finished composition. */
  if (root.classList.contains("motion")) root.classList.add("ready");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var compact = window.matchMedia("(max-width: 1023px)");
  var header = document.getElementById("header");

  /* --- Header ---------------------------------------------------------------
     No ground at rest; once the page has moved under the bar, the gradient
     comes up behind it. */
  var toggle = header.querySelector(".header__toggle");
  var scrolled = false;
  var painting = false;

  function paintHeader() {
    painting = false;
    paintExits();
    var past = window.scrollY > 24;
    if (past === scrolled) return;
    scrolled = past;
    if (past) header.setAttribute("data-scrolled", "");
    else header.removeAttribute("data-scrolled");
  }
  function requestPaint() {
    if (!painting) {
      painting = true;
      window.requestAnimationFrame(paintHeader);
    }
  }
  window.addEventListener("scroll", requestPaint, { passive: true });
  window.addEventListener("resize", requestPaint);
  paintHeader();

  /* --- The copy leaves the locked sections ----------------------------------
     Cullinan and Black Badge hold their copy on a standing picture; once the
     section has been read, the copy slides up a line at a time rather than
     being carried off by the scroll. */
  var exits = Array.prototype.slice.call(document.querySelectorAll("[data-exit]"));

  function paintExits() {
    if (!exits) return;                 /* the header paints before this runs */
    for (var i = 0; i < exits.length; i++) {
      var el = exits[i];
      var box = el.getBoundingClientRect();
      var picture = el.querySelector(".cullinan__field, .badge__frame");
      var next = el.nextElementSibling;
      var cover = next ? Math.abs(parseFloat(getComputedStyle(next).marginTop)) || 0 : 0;
      var tail = box.height - (picture ? picture.getBoundingClientRect().height : 0) - cover;
      var passed = -box.top;                      /* how far into the section */
      var out = tail > 80 && passed > tail * 0.18 && passed < box.height;
      if (el.classList.contains("is-out") && !out) el.classList.add("was-out");
      el.classList.toggle("is-out", out);
    }
  }

  /* --- Menu (under 1200) --------------------------------------------------- */
  function setMenu(open) {
    if (open) header.setAttribute("data-open", "");
    else header.removeAttribute("data-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
    if (!open) requestPaint();
  }
  toggle.addEventListener("click", function () {
    setMenu(!header.hasAttribute("data-open"));
  });
  header.querySelector(".header__menu").addEventListener("click", function (e) {
    if (e.target.closest("a")) setMenu(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && header.hasAttribute("data-open")) {
      setMenu(false);
      toggle.focus();
    }
  });

  /* --- Films ----------------------------------------------------------------
     Sources are chosen once by width (720p under 1024). A film plays while its
     section is on screen and pauses when it leaves. The visitor's own pause
     wins over both; with reduced motion nothing starts on its own.          */
  var films = Array.prototype.slice.call(document.querySelectorAll("video[data-src]"));

  films.forEach(function (video) {
    var section = video.closest("section");
    var button = section.querySelector(".film-toggle");
    var heldByVisitor = reduced.matches;
    var visible = false;
    var loaded = false;

    function load() {
      if (loaded) return;
      loaded = true;
      video.src = compact.matches ? video.getAttribute("data-src-small") : video.getAttribute("data-src");
    }

    function show(state) {
      button.setAttribute("data-state", state);
      button.setAttribute("aria-label", state === "playing" ? "Pause film" : "Play film");
    }

    function play() {
      load();
      var p = video.play();
      if (p && p.catch) {
        p.catch(function () { show("paused"); });
      }
      show("playing");
    }

    function pause() {
      video.pause();
      show("paused");
    }

    function sync() {
      if (visible && !heldByVisitor && section.classList.contains("is-in")) play();
      else if (!video.paused) pause();
    }

    button.hidden = false;
    show(heldByVisitor ? "paused" : "playing");

    button.addEventListener("click", function () {
      heldByVisitor = !video.paused ? true : false;
      if (heldByVisitor) pause();
      else play();
    });

    video.addEventListener("pause", function () { show("paused"); });
    video.addEventListener("play", function () { show("playing"); });

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible) load();
        sync();
      }, { threshold: 0.2 }).observe(section);
    } else {
      visible = true;
      sync();
    }

    section.addEventListener("reveal", sync);
  });

  /* --- One gesture, one section ---------------------------------------------
     Asked for: a scroll takes you to the next section, not into the middle of
     one. Pointer devices only — on touch the long sections (service, news,
     the footer) have to stay reachable by ordinary scrolling.
     Stops are the section tops, plus the beat inside a locked section where
     its copy has left, plus the foot of any section taller than the screen.  */
  var stepping = window.matchMedia("(min-width: 1024px) and (pointer: fine)");
  /* Only the home page is a sequence of screens; a listing scrolls freely. */
  var sectioned = document.body.hasAttribute("data-scroll");
  var stops = [];
  var animating = false;
  var lockedUntil = 0;

  function readStops() {
    var vh = window.innerHeight;
    var list = [];
    Array.prototype.forEach.call(document.querySelectorAll("main > section, footer"), function (el) {
      var box = el.getBoundingClientRect();
      var top = Math.round(box.top + window.scrollY);
      list.push(top);
      /* A locked section has a beat of its own: the picture is already in
         place and the copy has just left. Its length is whatever the section
         has beyond the picture and the cover, measured, not parsed. */
      var picture = el.querySelector(".cullinan__field, .badge__frame");
      if (picture) {
        var next = el.nextElementSibling;
        var cover = next ? Math.abs(parseFloat(getComputedStyle(next).marginTop)) || 0 : 0;
        var tail = box.height - picture.getBoundingClientRect().height - cover;
        if (tail > 80) list.push(Math.round(top + tail));
      }
      if (box.height > vh + 8) list.push(Math.round(top + box.height - vh));
    });
    var max = document.documentElement.scrollHeight - vh;
    stops = list
      .map(function (y) { return Math.max(0, Math.min(max, y)); })
      .sort(function (a, b) { return a - b; })
      .filter(function (y, i, arr) { return i === 0 || y - arr[i - 1] > 24; });
  }

  function glideTo(y) {
    /* scrollTo is told "instant" on every frame: the stylesheet's own
       smooth scrolling would otherwise animate each step of this animation. */
    if (reduced.matches) { window.scrollTo({ top: y, behavior: "instant" }); return; }
    var from = window.scrollY;
    var span = y - from;
    if (!span) return;
    var t0 = performance.now();
    var ms = Math.min(1100, Math.max(620, Math.abs(span) * 0.7));
    animating = true;
    (function frame(now) {
      var p = Math.min(1, (now - t0) / ms);
      /* the page's own curve, so a jump feels like the rest of the site */
      var e = 1 - Math.pow(1 - p, 3);
      window.scrollTo({ top: Math.round(from + span * e), behavior: "instant" });
      if (p < 1) window.requestAnimationFrame(frame);
      else { animating = false; lockedUntil = performance.now() + 220; }
    })(performance.now());
  }

  function step(direction) {
    if (animating || performance.now() < lockedUntil) return true;
    if (!stops.length) readStops();
    var y = window.scrollY;
    var next = null;
    for (var i = 0; i < stops.length; i++) {
      if (direction > 0 && stops[i] > y + 8) { next = stops[i]; break; }
      if (direction < 0 && stops[i] < y - 8) next = stops[i];
    }
    if (next === null) return false;
    glideTo(next);
    return true;
  }

  function onWheel(e) {
    if (!sectioned || !stepping.matches || header.hasAttribute("data-open")) return;
    if (Math.abs(e.deltaY) < 4 || Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;   /* a sideways gesture is the rail's */
    if (animating || performance.now() < lockedUntil) { e.preventDefault(); return; }
    if (step(e.deltaY > 0 ? 1 : -1)) e.preventDefault();
  }

  window.addEventListener("wheel", onWheel, { passive: false });
  window.addEventListener("resize", function () { stops = []; });
  window.addEventListener("load", readStops);
  readStops();

  /* The keyboard keeps its own transport on every device. */
  document.addEventListener("keydown", function (e) {
    if (header.hasAttribute("data-open")) return;
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || e.metaKey || e.ctrlKey || e.altKey) return;
    if (!sectioned) return;
    if (e.key === "PageDown") { if (step(1)) e.preventDefault(); }
    else if (e.key === "PageUp") { if (step(-1)) e.preventDefault(); }
  });

  /* --- The inventory rail ---------------------------------------------------
     An arrow moves the rail one screen; the snap lands it on a card. Each
     arrow goes quiet at its end of the rail.                                 */
  Array.prototype.forEach.call(document.querySelectorAll(".stock__rail"), function (rail) {
    var row = rail.querySelector(".stock__row");
    var arrows = Array.prototype.slice.call(rail.querySelectorAll(".stock__arrow"));
    if (!row || !arrows.length) return;
    function settle() {
      var max = row.scrollWidth - row.clientWidth - 1;
      arrows.forEach(function (a) {
        var dir = +a.dataset.dir;
        a.disabled = dir < 0 ? row.scrollLeft <= 0 : row.scrollLeft >= max;
      });
    }
    arrows.forEach(function (a) {
      a.addEventListener("click", function () {
        var gap = parseFloat(getComputedStyle(row).columnGap) || 0;
        row.scrollBy({ left: +a.dataset.dir * (row.clientWidth + gap), behavior: reduced.matches ? "auto" : "smooth" });
      });
    });
    row.addEventListener("scroll", settle, { passive: true });
    window.addEventListener("resize", settle);
    settle();
  });

  /* --- Reveals -------------------------------------------------------------
     The prototype fires each section's Default → Variant2 when the pointer
     enters it. Scrolling past a resting pointer is what made it look scroll-
     driven, so the trigger here is the section's top reaching mid-viewport.
     Once revealed, a section stays revealed.                                 */
  var reveals = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));

  function markIn(el) {
    if (el.classList.contains("is-in")) return;
    el.classList.add("is-in");
    el.dispatchEvent(new CustomEvent("reveal"));
  }

  function revealAll() {
    reveals.forEach(markIn);
  }

  if (!root.classList.contains("motion") || !("IntersectionObserver" in window)) {
    revealAll();
  } else {
    var hero = document.querySelector(".hero");   /* absent on the inventory page */
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          io.unobserve(entry.target);
          markIn(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -50% 0px" });

    reveals.forEach(function (el) {
      if (el !== hero) io.observe(el);
    });

    /* The hero plays its pair once the first frame has painted. */
    if (hero) {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () { markIn(hero); });
      });
    }
  }

  reduced.addEventListener("change", function (e) {
    if (e.matches) {
      root.classList.remove("motion");
      root.classList.remove("ready");
      revealAll();
    }
  });

})();
