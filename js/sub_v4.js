/* WRITTEN by tools/sub_v4.py from ../BRAMAN_BENTLEY/js/page7.js and sub7.js — do not edit. */
/* the layout width without the scrollbar, for edges aligned to the fixed header */
(function () {
  var root = document.documentElement;
  function set() { root.style.setProperty("--vw", root.clientWidth + "px"); }
  set();
  window.addEventListener("resize", set);
  document.addEventListener("DOMContentLoaded", set);
})();

/* Form labels as bentleymotors.com sets them: the label stands on the field's
   line, in the body size, until the field is chosen or filled; then it rises
   above the line, small. The script only marks which fields hold a value
   (field--float, is-filled); the sheet does the rest. Without it, the labels
   simply stay above their fields. */
(function () {
  function mark(input) {
    var field = input.closest(".field");
    if (field) field.classList.toggle("is-filled", input.value.trim() !== "");
  }
  function init() {
    document.querySelectorAll(".field > .field__input").forEach(function (input) {
      var field = input.parentElement;
      if (!field.querySelector(".field__label")) return;
      field.classList.add("field--float");
      mark(input);
      input.addEventListener("input", function () { mark(input); });
      input.addEventListener("change", function () { mark(input); });
    });
    document.documentElement.classList.add("has-float");
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();

/* The open list of a dropdown as the demo site draws it (Alex, 2026-10-26):
   the closed field stays the browser's own <select> on its ruled line; a press
   opens the site's own list under that line instead of the system's — a white
   plate with a hairline, a choice to a 40px row, the model names in capitals,
   and on the listing's picks how many cars each choice leaves. Its height is
   its choices. Keys: arrows, Home/End, Enter or Space to choose, Escape or
   Tab to close. On a touch screen the phone's own picker stays. */
(function () {
  if (window.matchMedia && window.matchMedia("(pointer: coarse)").matches) return;
  var open = null, uid = 0;

  /* how many cars a choice leaves, the other picks as they stand (the
     listing's own rule: "certified" is the pre-owned cars in Bentley's programme) */
  function counter(sel) {
    var grid = document.getElementById("grid");
    if (!grid || !sel.dataset.pick) return null;
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
    var others = Array.prototype.slice.call(document.querySelectorAll("[data-pick]")).filter(function (p) { return p !== sel; });
    function ok(card, pick, want) {
      if (!want) return true;
      if (pick === "condition" && want === "certified") return card.dataset.certified === "1";
      var have = card.dataset[pick];
      return have === undefined || have === want;
    }
    return function (value) {
      return cards.filter(function (c) {
        return ok(c, sel.dataset.pick, value) && others.every(function (p) { return ok(c, p.dataset.pick, p.value); });
      }).length;
    };
  }

  function close(refocus) {
    if (!open) return;
    var o = open; open = null;
    o.list.remove();
    o.sel.setAttribute("aria-expanded", "false");
    o.sel.removeAttribute("aria-activedescendant");
    o.box.classList.remove("is-open");
    if (refocus) o.sel.focus();
  }

  function activate(i, step) {
    var items = open.items;
    i = Math.max(0, Math.min(items.length - 1, i));
    while (items[i].hidden && i + (step || 1) >= 0 && i + (step || 1) < items.length) i += step || 1;
    while (items[i].hidden && i + 1 < items.length) i += 1;   /* the prompt at the top: the first real choice */
    items.forEach(function (li, k) { li.classList.toggle("is-active", k === i); });
    open.active = i;
    open.sel.setAttribute("aria-activedescendant", items[i].id);
    var li = items[i], l = open.list;
    if (li.offsetTop < l.scrollTop) l.scrollTop = li.offsetTop;
    else if (li.offsetTop + li.offsetHeight > l.scrollTop + l.clientHeight) l.scrollTop = li.offsetTop + li.offsetHeight - l.clientHeight;
  }

  function choose(i) {
    var sel = open.sel, v = sel.options[i].value;
    close(true);
    if (sel.value === v) return;
    sel.value = v;
    sel.dispatchEvent(new Event("input", { bubbles: true }));
    sel.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function show(sel) {
    close(false);
    var box = sel.parentElement;
    var list = document.createElement("ul");
    list.className = "dd" + (sel.name === "model" ? " dd--caps" : "");
    list.id = "dd-" + (++uid);
    list.setAttribute("role", "listbox");
    var count = counter(sel);
    var items = Array.prototype.map.call(sel.options, function (opt, i) {
      var li = document.createElement("li");
      li.className = "dd__opt"; li.id = list.id + "-" + i;
      /* a form's empty first choice is only a prompt — its label already says it */
      if (!opt.value && sel.classList.contains("field__select")) li.hidden = true;
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", opt.selected ? "true" : "false");
      if (opt.disabled) li.setAttribute("aria-disabled", "true");
      var name = document.createElement("span"); name.className = "dd__name"; name.textContent = opt.textContent;
      li.appendChild(name);
      if (count && opt.value) {
        var n = count(opt.value), c = document.createElement("span");
        c.className = "dd__count"; c.textContent = "/" + n;
        if (!n) li.classList.add("is-none");
        li.appendChild(c);
      }
      li.addEventListener("mousedown", function (e) { e.preventDefault(); });
      li.addEventListener("click", function () { if (!opt.disabled) choose(i); });
      li.addEventListener("mousemove", function () { if (open && open.active !== i) activate(i); });
      return li;
    });
    items.forEach(function (li) { list.appendChild(li); });
    box.appendChild(list);
    box.classList.add("is-open");
    sel.setAttribute("aria-controls", list.id);
    sel.setAttribute("aria-expanded", "true");
    /* a list wider than its field keeps inside the window */
    var r = list.getBoundingClientRect();
    if (r.right > document.documentElement.clientWidth - 8) list.classList.add("dd--end");
    open = { sel: sel, box: box, list: list, items: items, active: 0 };
    activate(Math.max(0, sel.selectedIndex));
  }

  function init() {
    document.querySelectorAll("select.pick__select, select.field__select").forEach(function (sel) {
      sel.setAttribute("aria-haspopup", "listbox");
      sel.setAttribute("aria-expanded", "false");
      sel.addEventListener("mousedown", function (e) {
        if (e.button !== 0) return;
        e.preventDefault();
        if (open && open.sel === sel) close(true); else { sel.focus({ focusVisible: false }); show(sel); }
      });
      sel.addEventListener("keydown", function (e) {
        var isOpen = open && open.sel === sel;
        var k = e.key;
        if (!isOpen) {
          if (k === "ArrowDown" || k === "ArrowUp" || k === "Enter" || k === " " || k === "F4") { e.preventDefault(); show(sel); }
          return;
        }
        if (k === "ArrowDown") { e.preventDefault(); activate(open.active + 1); }
        else if (k === "ArrowUp") { e.preventDefault(); activate(open.active - 1, -1); }
        else if (k === "Home") { e.preventDefault(); activate(0); }
        else if (k === "End") { e.preventDefault(); activate(open.items.length - 1, -1); }
        else if (k === "Enter" || k === " ") { e.preventDefault(); choose(open.active); }
        else if (k === "Escape") { e.preventDefault(); close(true); }
        else if (k === "Tab") close(false);
      });
      sel.addEventListener("blur", function () { setTimeout(function () { if (open && open.sel === sel && document.activeElement !== sel) close(false); }, 0); });
    });
    document.addEventListener("mousedown", function (e) { if (open && !open.box.contains(e.target)) close(false); });
    window.addEventListener("resize", function () { close(false); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();

/* Direction 7 inner pages: a row of plates turned by the arrows beside it,
   one plate a press; the spent arrow quieter, never gone (as the home rail). */
(function () {
  document.querySelectorAll(".sub__reviews-frame").forEach(function (frame) {
    var row = frame.querySelector(".sub__review-list");
    var prev = frame.querySelector('[data-dir="-1"]'), next = frame.querySelector('[data-dir="1"]');
    if (!row || !prev || !next) return;
    function step() { var item = row.querySelector("li"); return item ? item.getBoundingClientRect().width + parseFloat(getComputedStyle(row).columnGap || 0) : row.clientWidth; }
    function paint() {
      prev.disabled = row.scrollLeft <= 2;
      next.disabled = row.scrollLeft + row.clientWidth >= row.scrollWidth - 2;
    }
    prev.addEventListener("click", function () { row.scrollBy({ left: -step(), behavior: "smooth" }); });
    next.addEventListener("click", function () { row.scrollBy({ left: step(), behavior: "smooth" }); });
    row.addEventListener("scroll", paint, { passive: true });
    window.addEventListener("resize", paint);
    paint();
  });
})();

/* "Read more": the dealer's longer words, folded as on their own page */
(function () {
  document.querySelectorAll("[data-more]").forEach(function (btn) {
    var box = document.getElementById(btn.getAttribute("aria-controls"));
    if (!box) return;
    btn.addEventListener("click", function () {
      var open = box.hasAttribute("hidden");
      if (open) box.removeAttribute("hidden"); else box.setAttribute("hidden", "");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.firstChild.nodeValue = open ? "Read less" : "Read more";
    });
  });
})();

/* The upload on a form (Sell Your Vehicle, as the demo's): photographs dropped
   on the field or chosen with Upload appear as thumbnails, each with its own
   remove; at most data-max (12), images only, no file twice. The chosen files
   are kept on the input itself, so the form sends them as it is. */
(function () {
  document.querySelectorAll(".sub__upload").forEach(function (box) {
    var input = box.querySelector(".sub__drop-input"), zone = box.querySelector(".sub__drop");
    var list = box.querySelector(".sub__thumbs"), count = box.querySelector(".sub__drop-count");
    var max = parseInt(box.getAttribute("data-max"), 10) || 12, files = [], urls = [];
    if (!input || !zone || !list) return;

    function keep() {
      try { var dt = new DataTransfer(); files.forEach(function (f) { dt.items.add(f); }); input.files = dt.files; } catch (e) {}
    }
    function render() {
      urls.forEach(function (u) { URL.revokeObjectURL(u); }); urls = [];
      list.textContent = "";
      files.forEach(function (f, i) {
        var li = document.createElement("li"), img = document.createElement("img"), name = document.createElement("span"), rm = document.createElement("button");
        var u = URL.createObjectURL(f); urls.push(u);
        img.src = u; img.alt = "";
        name.className = "sub__thumb-name"; name.textContent = f.name;
        rm.type = "button"; rm.className = "sub__thumb-rm"; rm.textContent = "×";
        rm.setAttribute("aria-label", "Remove " + f.name);
        rm.addEventListener("click", function () { files.splice(i, 1); keep(); render(); input.focus(); });
        li.appendChild(img); li.appendChild(name); li.appendChild(rm); list.appendChild(li);
      });
      count.textContent = files.length ? files.length + " of " + max + " images" + (files.length >= max ? " — the most that can be sent" : "") : "";
      box.toggleAttribute("data-full", files.length >= max);
    }
    function add(fl) {
      Array.prototype.forEach.call(fl || [], function (f) {
        if (!/^image\//.test(f.type) || files.length >= max) return;
        if (files.some(function (x) { return x.name === f.name && x.size === f.size; })) return;
        files.push(f);
      });
      keep(); render();
    }
    input.addEventListener("change", function () { var picked = Array.prototype.slice.call(input.files); add(picked); });
    ["dragenter", "dragover"].forEach(function (t) {
      zone.addEventListener(t, function (e) { e.preventDefault(); zone.setAttribute("data-over", ""); });
    });
    ["dragleave", "dragend"].forEach(function (t) {
      zone.addEventListener(t, function () { zone.removeAttribute("data-over"); });
    });
    zone.addEventListener("drop", function (e) { e.preventDefault(); zone.removeAttribute("data-over"); add(e.dataTransfer && e.dataTransfer.files); });
  });
})();

/* The payment calculator (the demo's fields, working): the amount financed is
   the price less the down payment and the trade-in; the monthly payment the
   standard amortised payment at the APR over the term (the amount over the
   months when the rate is 0). An estimate, as the dealer's line under it says. */
(function () {
  var form = document.querySelector(".sub__calc");
  if (!form) return;
  var money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  function num(name) {
    var v = String(form.elements[name].value || "").replace(/[^0-9.]/g, "");
    var n = parseFloat(v); return isFinite(n) && n > 0 ? n : 0;
  }
  function out(key, text) { var el = form.querySelector('[data-out="' + key + '"]'); if (el) el.textContent = text; }
  function calc() {
    var financed = Math.max(0, num("price") - num("down") - num("trade"));
    var apr = num("apr"), months = parseInt(form.elements.term.value, 10) || 60;
    var r = apr / 100 / 12;
    var pay = financed === 0 ? 0 : (r > 0 ? financed * r / (1 - Math.pow(1 + r, -months)) : financed / months);
    out("pay", money.format(Math.round(pay)));
    out("financed", money.format(Math.round(financed)));
    out("term", months + " months");
    out("apr", (apr ? apr.toFixed(2).replace(/\.?0+$/, "") : "0") + "% APR");
  }
  form.addEventListener("input", calc);
  form.addEventListener("change", calc);
  calc();
})();

/* The model page's film: Bentley's own frame stands until a press; only then
   is YouTube asked for the film, and it plays in the frame's place. */
(function () {
  document.querySelectorAll("[data-film]").forEach(function (frame) {
    var play = frame.querySelector(".mdl__play");
    if (!play) return;
    play.addEventListener("click", function () {
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + frame.dataset.film + "?autoplay=1&rel=0";
      f.title = frame.dataset.title || "Film";
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      f.referrerPolicy = "strict-origin-when-cross-origin";
      frame.appendChild(f);
      frame.classList.add("is-playing");
      f.focus();
    });
  });
})();

/* Our model page's film: the hero's photograph is the film's first frame. A
   press plays Bentley's film in the photograph's place (YouTube is asked for
   it only then); the close button, or Escape, puts the photograph back. */
(function () {
  document.querySelectorAll("[data-film-open]").forEach(function (btn) {
    var hero = btn.closest("section"), stage = hero && hero.querySelector("[data-film]");
    if (!stage) return;
    var close = null, frame = null;
    function stop() {
      if (frame) frame.remove();
      if (close) close.remove();
      frame = close = null;
      hero.classList.remove("is-playing");
      btn.focus();
    }
    btn.addEventListener("click", function () {
      frame = document.createElement("iframe");
      frame.className = "mx__film-frame";
      frame.src = "https://www.youtube-nocookie.com/embed/" + stage.dataset.film + "?autoplay=1&rel=0";
      frame.title = stage.dataset.title || "Film";
      frame.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      frame.referrerPolicy = "strict-origin-when-cross-origin";
      close = document.createElement("button");
      close.type = "button"; close.className = "mx__film-close"; close.setAttribute("aria-label", "Close the film");
      close.textContent = "\u00d7";
      close.addEventListener("click", stop);
      stage.appendChild(frame); stage.appendChild(close);
      hero.classList.add("is-playing");
      close.focus();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && frame) stop(); });
  });
})();

/* Our model page's stage loop (Bentley's own, from bentleymotors.com): from
   1024px, and only when the visitor has not asked for less motion, the
   muted loop runs in the hero photograph's place — added here so a phone
   never downloads it. A pause button stops it (moving content longer than
   five seconds can always be stopped); it pauses while the film plays. */
(function () {
  var stage = document.querySelector("[data-loop]");
  if (!stage || !window.matchMedia) return;
  var mq = window.matchMedia("(min-width: 1024px) and (prefers-reduced-motion: no-preference)");
  if (!mq.matches) return;
  var hero = stage.closest("section");
  var v = document.createElement("video");
  v.className = "mx__hero-film";
  v.muted = true; v.loop = true; v.autoplay = true; v.playsInline = true;
  v.setAttribute("muted", ""); v.setAttribute("playsinline", ""); v.setAttribute("aria-hidden", "true");
  v.poster = stage.dataset.loopPoster;
  v.preload = "auto";
  v.src = stage.dataset.loop;
  stage.appendChild(v);
  hero.classList.add("has-loop");
  var btn = document.createElement("button");
  btn.type = "button"; btn.className = "mx__loop-btn";
  var PAUSE = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" fill="currentColor"/></svg>';
  var PLAY = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg>';
  function label() {
    var paused = v.paused;
    btn.innerHTML = paused ? PLAY : PAUSE;
    btn.setAttribute("aria-label", paused ? "Play the background film" : "Pause the background film");
  }
  var userPaused = false;
  btn.addEventListener("click", function () {
    if (v.paused) { userPaused = false; v.play(); } else { userPaused = true; v.pause(); }
  });
  v.addEventListener("play", label); v.addEventListener("pause", label);
  stage.appendChild(btn); label();
  var p = v.play(); if (p && p.catch) p.catch(function () { label(); });
  /* while Bentley's film plays, the loop rests; afterwards it runs again,
     unless the visitor stopped it */
  new MutationObserver(function () {
    if (hero.classList.contains("is-playing")) v.pause();
    else if (!userPaused) v.play();
  }).observe(hero, { attributes: true, attributeFilter: ["class"] });
})();

/* a plate's own button for its film (Informational Videos): the bar under the
   film plays the same film as the button on its frame */
(function () {
  document.querySelectorAll("[data-film-play]").forEach(function (btn) {
    var plate = btn.closest(".sub__promo-plate"), play = plate && plate.querySelector(".mdl__play");
    if (!play) return;
    btn.addEventListener("click", function () { play.click(); btn.disabled = true; });
  });
})();
