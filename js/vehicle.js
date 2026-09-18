/* Rolls-Royce Motor Cars Palm Beach — vehicle page.
   The rail of photographs: it scrolls, snaps and drags; the line beneath
   says where it is; the arrows move it a frame; any frame opens
   full-screen, where the keyboard's arrows and a swipe step through. On a
   small screen the offer bar follows the page once the figure at the top
   has scrolled off. */

(function () {
  "use strict";

  var film = document.querySelector(".film");
  if (!film) return;

  var photos = [];
  try { photos = JSON.parse(film.getAttribute("data-photos") || "[]"); } catch (e) { photos = []; }
  var row = film.querySelector(".film__row");
  var frames = Array.prototype.slice.call(film.querySelectorAll(".film__frame"));
  var opens = Array.prototype.slice.call(film.querySelectorAll(".film__open"));
  var arrows = Array.prototype.slice.call(film.querySelectorAll(".film__nav .film__arrow"));
  var counter = film.querySelector(".film__count [data-index]");
  var thumb = film.querySelector(".film__thumb");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var motion = document.documentElement.classList.contains("motion");
  var mode = "photos", turn = null;   /* the 360° view, set up further down */

  /* The rail arrives after the head. */
  var head = document.querySelector(".vdp__head");
  if (motion && head && !head.classList.contains("is-in")) {
    film.setAttribute("data-wait", "");
    head.addEventListener("reveal", function () { film.removeAttribute("data-wait"); });
    window.setTimeout(function () { film.removeAttribute("data-wait"); }, 2000);
  }

  function padLeft() { return parseFloat(getComputedStyle(row).paddingLeft) || 0; }

  /* Which frame stands on the measure? */
  function current() {
    var edge = row.getBoundingClientRect().left + padLeft();
    var best = 0, dist = Infinity;
    frames.forEach(function (f, i) {
      var d = Math.abs(f.getBoundingClientRect().left - edge);
      if (d < dist) { dist = d; best = i; }
    });
    return best;
  }

  var photoFrames = frames.filter(function (f) { return !f.classList.contains("film__frame--spin"); });
  function settle() {
    if (mode === "spin") return;
    var i = current();
    var f = frames[i];
    var onTile = f && f.classList.contains("film__frame--spin");
    if (counter) {
      counter.textContent = onTile ? "360°" : (photoFrames.indexOf(f) + 1);
      var total = counter.parentNode.querySelector(".film__total");
      if (total) total.hidden = onTile;
    }
    var max = row.scrollWidth - row.clientWidth;
    arrows.forEach(function (a) {
      var dir = +a.dataset.dir;
      a.disabled = dir < 0 ? row.scrollLeft <= 1 : row.scrollLeft >= max - 1;
    });
    if (thumb && max > 0) {
      var share = row.clientWidth / row.scrollWidth;
      thumb.style.width = (share * 100) + "%";
      thumb.style.transform = "translateX(" + (row.scrollLeft / max) * (100 / share - 100) + "%)";
    } else if (thumb) {
      thumb.style.width = "100%";
      thumb.style.transform = "none";
    }
  }

  function go(i) {
    i = Math.max(0, Math.min(frames.length - 1, i));
    row.scrollTo({ left: frames[i].offsetLeft - padLeft(), behavior: reduced.matches ? "auto" : "smooth" });
  }

  arrows.forEach(function (a) {
    a.addEventListener("click", function () { if (mode !== "spin") go(current() + (+a.dataset.dir)); });
  });
  row.addEventListener("scroll", settle, { passive: true });
  window.addEventListener("resize", settle);
  window.addEventListener("load", settle);
  settle();

  /* --- Drag: the rail follows a held mouse, and snaps when let go. A press
     that moves less than a few pixels is still a click and opens the frame. */
  var drag = null;
  row.addEventListener("pointerdown", function (e) {
    if (e.pointerType !== "mouse" || e.button !== 0) return;
    drag = { x: e.clientX, left: row.scrollLeft, moved: false, id: e.pointerId, t: performance.now(), v: 0 };
  });
  row.addEventListener("pointermove", function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x;
    if (!drag.moved && Math.abs(dx) > 5) {
      drag.moved = true;
      row.setAttribute("data-dragging", "");
      row.setPointerCapture(drag.id);
    }
    if (drag.moved) {
      var now = performance.now();
      drag.v = (row.scrollLeft - (drag.left - dx)) / Math.max(1, now - drag.t);   /* px per ms, for the throw */
      drag.t = now;
      row.scrollLeft = drag.left - dx;
      e.preventDefault();
    }
  });
  function release() {
    if (!drag) return;
    var moved = drag.moved, v = drag.v;
    drag = null;
    row.removeAttribute("data-dragging");
    if (moved) {
      /* a throw carries on a frame; otherwise land on the nearest */
      var i = current();
      if (v < -0.6) i += 1; else if (v > 0.6) i -= 1;
      go(i);
      var swallow = function (ev) { ev.stopPropagation(); ev.preventDefault(); row.removeEventListener("click", swallow, true); };
      row.addEventListener("click", swallow, true);
      window.setTimeout(function () { row.removeEventListener("click", swallow, true); }, 0);
    }
  }
  row.addEventListener("pointerup", release);
  row.addEventListener("pointercancel", release);
  row.addEventListener("dragstart", function (e) { e.preventDefault(); });

  /* Keyboard on the rail */
  film.addEventListener("keydown", function (e) {
    if (box && box.open) return;
    if (e.key === "ArrowRight") { if (mode === "spin" && turn) turn(1); else go(current() + 1); e.preventDefault(); }
    else if (e.key === "ArrowLeft") { if (mode === "spin" && turn) turn(-1); else go(current() - 1); e.preventDefault(); }
  });

  /* --- 360° — the spin ----------------------------------------------------
     Twenty-four frames of the dealer's turntable. A drag turns the car
     (one width of the stage is one full turn), a throw keeps it turning
     and slows; the arrows step it a frame; it turns once by itself on
     opening. Frames are fetched when the view is first opened. */
  var spinFrames = [];
  try { spinFrames = JSON.parse(film.getAttribute("data-spin") || "[]"); } catch (e) { spinFrames = []; }
  var spin = film.querySelector(".spin");
  var modes = Array.prototype.slice.call(film.querySelectorAll(".film__mode-button"));
  var note = film.querySelector(".film__note");

  if (spin && spinFrames.length > 1) {
    var stage = spin.querySelector(".spin__stage");
    var picture = spin.querySelector(".spin__image");
    var loading = spin.querySelector(".spin__loading");
    var loadBar = loading ? loading.querySelector("span") : null;
    var n = spinFrames.length;
    var angle = 0;                      /* in frames, fractional */
    var loaded = 0, ready = false, cache = [];
    var velocity = 0, raf = 0, auto = false;

    function paintFrame() {
      var i = ((Math.round(angle) % n) + n) % n;
      var src = spinFrames[i];
      if (picture.getAttribute("src") !== src) picture.src = src;
    }
    function fetchAll(done) {
      if (ready) { done(); return; }
      if (loading) loading.hidden = false;
      spinFrames.forEach(function (src, i) {
        var im = new Image();
        im.onload = im.onerror = function () {
          loaded += 1;
          if (loadBar) loadBar.style.width = (loaded / n * 100) + "%";
          if (loaded === n) { ready = true; if (loading) loading.hidden = true; done(); }
        };
        im.src = src; cache[i] = im;
      });
    }
    function tick() {
      raf = 0;
      if (auto) { angle += 0.05; paintFrame(); raf = window.requestAnimationFrame(tick); return; }
      if (Math.abs(velocity) > 0.002) {
        angle += velocity; velocity *= 0.94; paintFrame();
        raf = window.requestAnimationFrame(tick);
      } else velocity = 0;
    }
    function stopAuto() { auto = false; stage.setAttribute("data-touched", ""); }
    function start() {
      fetchAll(function () {
        if (!reduced.matches && !stage.hasAttribute("data-touched")) { auto = true; if (!raf) raf = window.requestAnimationFrame(tick); window.setTimeout(function () { auto = false; }, 9000); }
      });
    }

    /* drag */
    var hold = null;
    stage.addEventListener("pointerdown", function (e) {
      if (e.button !== 0) return;
      stopAuto(); velocity = 0;
      hold = { x: e.clientX, a: angle, t: performance.now(), v: 0, id: e.pointerId };
      stage.setAttribute("data-dragging", "");
      stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener("pointermove", function (e) {
      if (!hold) return;
      var per = stage.clientWidth / n;                 /* one stage width is one turn */
      var next = hold.a - (e.clientX - hold.x) / per;
      var now = performance.now();
      hold.v = (next - angle) / Math.max(1, now - hold.t) * 16;   /* frames per tick */
      hold.t = now; angle = next; paintFrame();
    });
    function letGo() {
      if (!hold) return;
      velocity = Math.max(-1.2, Math.min(1.2, hold.v));
      hold = null;
      stage.removeAttribute("data-dragging");
      if (!raf && !reduced.matches) raf = window.requestAnimationFrame(tick);
    }
    stage.addEventListener("pointerup", letGo);
    stage.addEventListener("pointercancel", letGo);
    stage.addEventListener("wheel", function (e) {
      if (Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;   /* sideways only */
      stopAuto(); angle += e.deltaX / 40; paintFrame(); e.preventDefault();
    }, { passive: false });

    /* the switch */
    function setMode(next) {
      mode = next;
      var spinning = mode === "spin";
      row.hidden = spinning; spin.hidden = !spinning;
      modes.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.mode === mode ? "true" : "false"); });
      var track = film.querySelector(".film__track");
      if (track) track.style.visibility = spinning ? "hidden" : "";
      if (counter) counter.parentNode.style.visibility = spinning ? "hidden" : "";
      if (note) note.style.visibility = spinning ? "hidden" : "";
      arrows.forEach(function (a) { a.disabled = false; });
      if (spinning) start(); else { auto = false; velocity = 0; settle(); }
    }
    modes.forEach(function (b) { b.addEventListener("click", function () { setMode(b.dataset.mode); }); });
    var launch = film.querySelector(".film__launch");
    if (launch) launch.addEventListener("click", function () { setMode("spin"); });
    turn = function (dir) { stopAuto(); velocity = 0; angle = Math.round(angle) + dir; paintFrame(); };
  }

  /* the arrows and the keyboard serve whichever view is up */
  arrows.forEach(function (a) {
    a.addEventListener("click", function () { if (mode === "spin" && turn) turn(+a.dataset.dir); }, true);
  });

  /* --- Full-screen ------------------------------------------------------- */
  var box = document.querySelector(".lightbox");
  var index = 0;
  if (box && typeof box.showModal === "function" && photos.length) {
    var image = box.querySelector(".lightbox__image");
    var count = box.querySelector("[data-index]");
    var boxArrows = Array.prototype.slice.call(box.querySelectorAll(".lightbox__arrow"));
    var show = function (i) {
      index = (i + photos.length) % photos.length;
      image.src = photos[index];
      image.alt = opens[index] ? opens[index].querySelector("img").alt : "";
      if (count) count.textContent = index + 1;
      var warm = new Image(); warm.src = photos[(index + 1) % photos.length];
    };
    opens.forEach(function (b) {
      b.addEventListener("click", function () { show(+b.dataset.index); box.showModal(); });
    });
    boxArrows.forEach(function (a) {
      a.addEventListener("click", function () { show(index + (+a.dataset.dir)); });
      if (photos.length < 2) a.hidden = true;
    });
    box.querySelector(".lightbox__close").addEventListener("click", function () { box.close(); });
    box.addEventListener("click", function (e) { if (e.target === box) box.close(); });
    box.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { show(index + 1); e.preventDefault(); e.stopPropagation(); }
      else if (e.key === "ArrowLeft") { show(index - 1); e.preventDefault(); e.stopPropagation(); }
    });
    box.addEventListener("close", function () {
      go(index);                                   /* the rail follows the viewer */
      if (opens[index]) opens[index].focus({ preventScroll: true });
    });
    var startX = null;
    box.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") startX = e.clientX; });
    box.addEventListener("pointerup", function (e) {
      if (startX === null) return;
      var dx = e.clientX - startX; startX = null;
      if (Math.abs(dx) > 40) show(index + (dx < 0 ? 1 : -1));
    });
  }

  /* --- Save, and the drawer for Call · Text · Share ---------------------
     Save keeps the car in the visitor's own browser (My Garage, when there
     is one, will take it from there). The other three slide the drawer in
     from the right and light the group asked for. */
  var tools = document.querySelector(".tools");
  var drawer = document.getElementById("contact");
  if (tools) {
    var stock = tools.getAttribute("data-stock"), carName = tools.getAttribute("data-name");
    var save = tools.querySelector('[data-tool="save"]');
    var KEY = "rr-garage";
    var garage = function () { try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return []; } };
    if (save) {
      var saved = garage().indexOf(stock) !== -1;
      save.setAttribute("aria-pressed", saved ? "true" : "false");
      save.querySelector("span").textContent = saved ? "Saved" : "Save";
      save.addEventListener("click", function () {
        var list = garage(), i = list.indexOf(stock);
        if (i === -1) list.push(stock); else list.splice(i, 1);
        try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {}
        var on = i === -1;
        save.setAttribute("aria-pressed", on ? "true" : "false");
        save.querySelector("span").textContent = on ? "Saved" : "Save";
      });
    }
  }
  if (drawer && tools) {
    var panel = drawer.querySelector(".drawer__panel");
    var opener = null;
    var line = carName + " at Rolls-Royce Motor Cars Palm Beach — " + location.href;
    var subject = carName + " — Rolls-Royce Motor Cars Palm Beach";

    /* Email: a mail to whoever they name, with the car and the link */
    var emailForm = drawer.querySelector('[data-form="email"]');
    if (emailForm) {
      emailForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var to = emailForm.elements.to.value.trim();
        var from = emailForm.elements.from.value.trim();
        var msg = emailForm.elements.message.value.trim();
        var body = (from ? from + " sent you this: " : "") + msg + "\n\n" + line;
        location.href = "mailto:" + encodeURIComponent(to) + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      });
    }
    /* Text: Messages to the number they type, or to themselves */
    var textForm = drawer.querySelector('[data-form="text"]');
    if (textForm) {
      textForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var to = textForm.elements.to.value.replace(/[^\d+]/g, "");
        location.href = "sms:" + to + "?&body=" + encodeURIComponent(line);
      });
    }
    var smsSelf = drawer.querySelector('[data-sms="self"]');
    if (smsSelf) smsSelf.href = "sms:?&body=" + encodeURIComponent(line);

    /* Share: the networks, the link, the device's own sheet */
    var url = encodeURIComponent(location.href), text = encodeURIComponent(carName + " at Rolls-Royce Motor Cars Palm Beach");
    var image = document.querySelector(".film__open img");
    var targets = {
      facebook: "https://www.facebook.com/sharer/sharer.php?u=" + url,
      x: "https://twitter.com/intent/tweet?text=" + text + "&url=" + url,
      whatsapp: "https://wa.me/?text=" + text + "%20" + url,
      telegram: "https://t.me/share/url?url=" + url + "&text=" + text,
      linkedin: "https://www.linkedin.com/sharing/share-offsite/?url=" + url,
      pinterest: "https://pinterest.com/pin/create/button/?url=" + url + "&description=" + text + (image ? "&media=" + encodeURIComponent(image.src) : "")
    };
    Object.keys(targets).forEach(function (k) { var a = drawer.querySelector('[data-share="' + k + '"]'); if (a) a.href = targets[k]; });
    var copy = drawer.querySelector('[data-share="copy"]');
    var sheet = drawer.querySelector('[data-share="sheet"]');
    if (copy) {
      copy.addEventListener("click", function () {
        var word = copy.querySelector("[data-word]");
        var done = function (t) { word.textContent = t; window.setTimeout(function () { word.textContent = "Copy"; }, 1800); };
        if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { done("Copied"); }, function () { done("Failed"); });
        else done("Failed");
      });
    }
    if (sheet && navigator.share) {
      sheet.hidden = false;
      sheet.addEventListener("click", function () { navigator.share({ title: carName, url: location.href }).catch(function () {}); });
    }

    function openDrawer(group, from) {
      opener = from || null;
      drawer.hidden = false;
      Array.prototype.forEach.call(drawer.querySelectorAll(".drawer__group"), function (g) {
        if (g.dataset.group === group) g.setAttribute("data-lit", ""); else g.removeAttribute("data-lit");
      });
      document.body.setAttribute("data-drawer", "");
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          drawer.setAttribute("data-open", "");
          var target = drawer.querySelector('.drawer__group[data-group="' + group + '"]');
          if (target) target.scrollIntoView({ block: "nearest" });
          var first = target ? target.querySelector("input, a, button") : null;
          (first || panel).focus({ preventScroll: true });
        });
      });
    }
    function closeDrawer() {
      drawer.removeAttribute("data-open");
      document.body.removeAttribute("data-drawer");
      window.setTimeout(function () { drawer.hidden = true; }, 500);
      if (opener) opener.focus({ preventScroll: true });
    }
    Array.prototype.forEach.call(tools.querySelectorAll("[data-open]"), function (b) {
      b.addEventListener("click", function () { openDrawer(b.dataset.open, b); });
    });
    Array.prototype.forEach.call(drawer.querySelectorAll("[data-close]"), function (b) {
      b.addEventListener("click", closeDrawer);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !drawer.hidden) { closeDrawer(); e.preventDefault(); }
      /* the focus stays inside the drawer while it is open */
      if (e.key === "Tab" && !drawer.hidden) {
        var focusables = panel.querySelectorAll('a[href], button:not([hidden]), input, textarea, [tabindex="-1"]');
        var first = focusables[0], last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
        else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
      }
    });
  }

  /* --- The bar ------------------------------------------------------------- */
  var bar = document.querySelector(".vdp__bar");
  var figure = document.querySelector(".vdp__figure");
  var offer = document.querySelector(".offer");
  var enquire = document.getElementById("enquire");
  if (bar && figure && offer) {
    bar.hidden = false;
    var ticking = false;
    var paint = function () {
      ticking = false;
      var vh = window.innerHeight;
      var gone = figure.getBoundingClientRect().bottom < 0;
      var o = offer.getBoundingClientRect();
      var offerHere = o.top < vh * 0.9 && o.bottom > vh * 0.2;
      var formHere = enquire ? enquire.getBoundingClientRect().top < vh * 0.8 : false;
      if (gone && !offerHere && !formHere) bar.setAttribute("data-shown", ""); else bar.removeAttribute("data-shown");
    };
    var onScroll = function () { if (!ticking) { ticking = true; window.requestAnimationFrame(paint); } };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    paint();
  }
})();
