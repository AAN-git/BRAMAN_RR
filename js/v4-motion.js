/* Version 4 — the scroll (Alex, 2026-10-07).
   Lenis is the page's scroll layer on every version-4 page (his standing
   rule): on the GSAP ticker, never under prefers-reduced-motion, menus and
   dialogs left to scroll natively and the page held while they are open.

   On the home page, Cullinan and Black Badge take the pinned exit with stops
   from Czinger and Pagani: the section docks full-screen, the words hold to
   be read, then — scrubbed to the scroll, reversible — the title's lines rise
   out of their masks, the line follows, the calls lift and fade; the picture
   holds its size (Alex: no shrink before it leaves) and only darkens. Once the words are gone the pin lets go.
   When the scroll comes to rest just before a pin (moving down) or inside
   one (moving up), the page glides the rest of the way and docks; any input
   cancels the glide. From 768px only — a phone keeps the plain page.

   Ownership: version 3's reveals own the titles', lines' and calls' transform
   and opacity, so the exit never touches those properties on those elements.
   It moves the lines SplitText cuts inside them, and the calls through
   `translate` and `filter: opacity()` (css/v4.css, data-pinx). */
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!window.Lenis || !window.gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);
  if (window.SplitText) gsap.registerPlugin(SplitText);

  document.querySelectorAll('.header__menu, .drawer__panel, .lightbox, dialog')
    .forEach((el) => el.setAttribute('data-lenis-prevent', ''));
  const lenis = new Lenis({ autoRaf: false, anchors: true, lerp: 0.1 });
  window.__lenis = lenis;
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((t) => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);

  /* the menu locks the body; a modal dialog holds the page */
  const hold = () => {
    const held = document.body.style.overflow === 'hidden' || document.querySelector('dialog[open]');
    held ? lenis.stop() : lenis.start();
  };
  new MutationObserver(hold).observe(document.body, { attributes: true, attributeFilter: ['style'] });
  document.querySelectorAll('dialog').forEach((d) => new MutationObserver(hold).observe(d, { attributes: true, attributeFilter: ['open'] }));

  const PINS = [
    { el: '.cullinan', len: 80, body: '.cullinan__body', title: '.cullinan__title', lines: '.cullinan__copy .line',
      lead: null, calls: '.cullinan .actions, .cullinan .doors', media: '.cullinan__image', field: '.cullinan__field' },
    { el: '.badge', len: 70, body: '.badge__body', title: null, lines: '.badge__copy',
      lead: '.badge__mark svg', calls: '.badge__cta, .badge .doors', media: '.badge__film', field: '.badge__frame' },
  ].filter((p) => document.querySelector(p.el));
  if (!PINS.length) return;

  const mm = gsap.matchMedia();
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => mm.add('(min-width: 768px)', () => {
    const made = PINS.map((p) => {
      const el = document.querySelector(p.el);
      el.setAttribute('data-pinx', '');
      const field = el.querySelector(p.field), media = el.querySelector(p.media);
      const dim = document.createElement('div');
      dim.className = 'pinx__dim'; dim.setAttribute('aria-hidden', 'true');
      field.appendChild(dim);
      const splits = [];
      const cut = (node) => {
        if (!node || !window.SplitText) return [];
        const sp = SplitText.create(node, { type: 'lines', mask: 'lines', linesClass: 'pinx__line' });
        splits.push(sp); return sp.lines;
      };
      const head = p.title ? cut(el.querySelector(p.title)) : [];
      const lines = [...el.querySelectorAll(p.lines)].flatMap(cut);
      const lead = p.lead ? [...el.querySelectorAll(p.lead)] : [];   /* a mark in place of a title */
      const calls = [...el.querySelectorAll(p.calls)];
      const tl = gsap.timeline({
        defaults: { ease: 'power1.in' },
        scrollTrigger: { trigger: el, start: 'top top', end: () => `+=${(p.len / 100) * innerHeight}`,
          pin: true, pinSpacing: true, scrub: true, anticipatePin: 1, invalidateOnRefresh: true },
      });
      tl.to({}, { duration: 1 }, 0);                                                   /* 0 → 1; hold to 0.3 */
      if (head.length) tl.to(head, { yPercent: -110, duration: 0.26, stagger: 0.07 }, 0.3);
      if (lines.length) tl.to(lines, { yPercent: -110, duration: 0.22, stagger: 0.05 }, 0.42);
      /* the calls: a number per call, written to its two variables */
      const lift = (node, at) => {
        const v = { t: 0 };
        const paint = () => { node.style.setProperty('--pinx-y', `${-20 * v.t}px`); node.style.setProperty('--pinx-a', `${(1 - v.t) * 100}%`); };
        tl.to(v, { t: 1, duration: 0.2, onUpdate: paint }, at);
      };
      lead.forEach((node) => lift(node, 0.3));
      calls.forEach((node, i) => lift(node, 0.5 + i * 0.04));
      tl.to(dim, { opacity: 0.35, duration: 0.7, ease: 'none' }, 0.3);
      return { st: tl.scrollTrigger, undo: () => {
        tl.scrollTrigger && tl.scrollTrigger.kill(); tl.kill();
        splits.forEach((sp) => sp.revert());
        [...lead, ...calls].forEach((n) => { n.style.removeProperty('--pinx-y'); n.style.removeProperty('--pinx-a'); });
        dim.remove(); el.removeAttribute('data-pinx');
      } };
    });
    ScrollTrigger.sort(); ScrollTrigger.refresh();
    if (window.__placeBadge) window.__placeBadge();

    /* --- the stops: each pin's start, where the section is docked and read */
    const stops = () => made.map((m) => m.st.start);
    window.__stops = () => stops().map(Math.round);
    const IDLE = 150, APPROACH = 0.35;
    let dir = 1, gliding = false, armed = false, lastY = lenis.scroll, lastMove = 0;
    const ease = (t) => 1 - Math.pow(1 - t, 3);
    const blocked = () => document.body.style.overflow === 'hidden' || document.querySelector('dialog[open]');
    const target = (y, d) => {
      const vh = innerHeight;
      for (const m of made) {
        const s = m.st.start, e = m.st.end;
        if (d > 0 && y > s - APPROACH * vh && y < s - 1) return s;   /* just before a pin, moving down */
        if (d < 0 && y > s + 1 && y < e) return s;                    /* inside one, moving up */
      }
      return null;
    };
    const glide = (t) => {
      gliding = true; armed = false;
      const dur = Math.min(0.9, Math.max(0.6, 0.55 + (Math.abs(t - lenis.scroll) / innerHeight) * 0.3));
      lenis.scrollTo(t, { duration: dur, easing: ease, onComplete: () => { gliding = false; armed = false; lastY = lenis.scroll; } });
    };
    const poll = () => {
      const y = lenis.scroll, now = performance.now();
      if (Math.abs(y - lastY) > 0.5) { lastY = y; lastMove = now; if (!gliding) armed = true; return; }
      if (!armed || gliding || now - lastMove < IDLE) return;
      armed = false;
      if (blocked() || Math.abs(lenis.velocity) > 0.4) return;
      const t = target(y, dir);
      if (t != null) glide(t);
    };
    const onScroll = () => { if (lenis.direction) dir = lenis.direction; };
    /* the wheel feeds Lenis's own target and overrides a glide by itself;
       a pointer or a key stops it where it is */
    const cancelWheel = () => { gliding = false; };
    const cancel = () => { if (gliding) { gliding = false; lenis.scrollTo(lenis.scroll, { immediate: true, force: true }); } };
    gsap.ticker.add(poll);
    lenis.on('scroll', onScroll);
    addEventListener('wheel', cancelWheel, { passive: true });
    addEventListener('pointerdown', cancel, { passive: true });
    addEventListener('keydown', cancel);
    return () => {
      made.forEach((m) => m.undo());
      gsap.ticker.remove(poll); lenis.off('scroll', onScroll);
      removeEventListener('wheel', cancelWheel); removeEventListener('pointerdown', cancel); removeEventListener('keydown', cancel);
      if (window.__placeBadge) window.__placeBadge();
    };
  }));
})();
