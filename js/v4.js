/* Version 4 — Black Badge: the car is never under the words (Alex, 2026-10-07).
   The film's still is cut by its width (cover), so on a short, wide screen the
   car grew down into the mark and the line. From 768px the still is placed
   here instead: the car — roof to the shadow under the wheels — stands whole
   between the bar and the mark, and where the still no longer reaches the
   frame's edges its floor fades into Noir. On a phone the still is the band
   above the words, and stays. */
(() => {
  const frame = document.querySelector('.badge__frame');
  const img = frame && frame.querySelector('.badge__film');
  const mark = document.querySelector('.badge__mark');
  if (!img || !mark) return;
  const R = 1176 / 1920;          /* the still's height to its width */
  const ROOF = 0.33, FLOOR = 0.70; /* the car in the still, top to bottom */
  const BAR = 128, AIR = 32;       /* the bar once scrolled, and the step to the mark */
  const wide = matchMedia('(min-width: 768px)');
  const PROPS = ['position', 'left', 'top', 'width', 'height', 'max-width', 'object-fit', '-webkit-mask-image', 'mask-image', '-webkit-mask-composite', 'mask-composite'];
  function place() {
    if (!wide.matches) { PROPS.forEach((k) => img.style.removeProperty(k)); return; }
    const W = frame.clientWidth, H = frame.clientHeight;
    const words = mark.getBoundingClientRect().top - frame.getBoundingClientRect().top;
    const room = words - AIR - BAR;
    if (room <= 0) return;
    const h = Math.min(Math.max(W * R, H), room / (FLOOR - ROOF));
    const w = h / R;
    const top = Math.min(0, words - AIR - FLOOR * h);
    const fade = [];
    if (top + h < H + 1) fade.push('linear-gradient(to bottom, #000 0 78%, transparent)');
    if (w < W) fade.push('linear-gradient(to right, transparent, #000 10%, #000 90%, transparent)');
    const mask = fade.length ? fade.join(', ') : 'none';
    /* set one by one, never cssText: the scroll (js/v4-motion.js) owns the
       still's transform */
    const set = { position: 'absolute', left: `${(W - w) / 2}px`, top: `${top}px`, width: `${w}px`, height: `${h}px`,
      'max-width': 'none', 'object-fit': 'fill', '-webkit-mask-image': mask, 'mask-image': mask,
      '-webkit-mask-composite': fade.length > 1 ? 'source-in' : '', 'mask-composite': fade.length > 1 ? 'intersect' : '' };
    for (const k in set) set[k] ? img.style.setProperty(k, set[k]) : img.style.removeProperty(k);
  }
  window.__placeBadge = place;
  place();
  addEventListener('resize', place, { passive: true });
  addEventListener('load', place);
  if (document.fonts) document.fonts.ready.then(place);
  /* the points step in from the left when the chapter is reached: measure
     again once they have landed */
  sell.addEventListener('reveal', () => setTimeout(place, 1800));
})();

/* The hero: the same rule. The still (16:9) is cut by its width on a short,
   wide screen and the car came down onto "Phantom Regatta". From 768px the
   still rises — no further than its own edge — until the shadow under the
   wheels clears the words; whatever the rise cannot give, the words give,
   stepping down towards the foot of the screen. */
(() => {
  const hero = document.querySelector('.hero');
  const img = hero && hero.querySelector('.hero__film');
  const body = hero && hero.querySelector('.hero__body');
  const model = hero && hero.querySelector('.hero__model');
  if (!img || !body || !model) return;
  const R = 1080 / 1920, FLOOR = 0.60, AIR = 28, FOOT = 24;
  const wide = matchMedia('(min-width: 768px)');
  function place() {
    img.style.objectPosition = ''; body.style.transform = '';
    if (!wide.matches) return;
    const box = hero.getBoundingClientRect(), W = box.width, H = box.height;
    const s = Math.max(W * R, H);                 /* the still's drawn height */
    const words = model.getBoundingClientRect().top - box.top;
    const slack = H - s;                          /* 0 or less */
    const want = words - AIR - FLOOR * s;         /* where the still's top must be */
    const top = Math.max(slack, Math.min(slack / 2, want));
    if (slack < 0) img.style.objectPosition = `50% ${(top / slack * 100).toFixed(1)}%`;
    const short = top + FLOOR * s + AIR - words;  /* what the rise could not give */
    if (short > 0) {
      const room = box.bottom - body.getBoundingClientRect().bottom - FOOT;
      body.style.transform = `translateY(${Math.max(0, Math.min(short, room))}px)`;
    }
  }
  place();
  addEventListener('resize', place, { passive: true });
  if (document.fonts) document.fonts.ready.then(place);
})();

/* Sell: the RR badge on Alex's photograph never sits under the words. From
   768px the photograph is placed so the badge stands in the open ground
   between the first point and the form, the photograph still covering the
   chapter; the veil's opening (css/v4.css) follows it. */
(() => {
  const sell = document.querySelector('[data-coast="sell"]');
  const field = sell && sell.querySelector('.sell__field');
  const img = field && field.querySelector('img');
  const first = sell && sell.querySelector('.sell__points li');
  const form = sell && sell.querySelector('.sell__form');
  const head = sell && sell.querySelector('.sell__head');
  if (!img || !first || !form || !head) return;
  const R = 1080 / 1920, BX = 0.405, BY = 0.455;   /* the badge in the photograph */
  const wide = matchMedia('(min-width: 768px)');
  const PROPS = ['left', 'width', 'height', 'top', 'object-fit', 'max-width'];
  function place() {
    if (!wide.matches) { PROPS.forEach((k) => img.style.removeProperty(k)); field.style.removeProperty('--bx'); field.style.removeProperty('--by'); return; }
    const box = field.getBoundingClientRect(), W = box.width, H = box.height;
    /* the open ground: right of the first point's longest line, left of the form,
       below the lede */
    let right = 0;
    first.querySelectorAll('h3, p').forEach((n) => {
      const r = document.createRange(); r.selectNodeContents(n);
      [...r.getClientRects()].forEach((q) => { right = Math.max(right, q.right); });
    });
    const fb = form.getBoundingClientRect(), fr = first.getBoundingClientRect();
    const hb = head.getBoundingClientRect().bottom;
    /* one column (the form below the points): the open ground is to the right */
    const fx = fb.top > fr.bottom ? box.right : fb.left;
    const tx = (right + fx) / 2 - box.left;
    const ty = Math.max(hb - box.top + 130, (fr.top + fr.bottom) / 2 - box.top);
    /* the smallest photograph that covers the chapter and can put the badge there */
    let w = Math.max(W, H / R);
    for (let i = 0; i < 40; i++) {
      const h = w * R;
      const l = tx - BX * w, t = ty - BY * h;
      if (l <= 0 && l + w >= W && t <= 0 && t + h >= H) break;
      w *= 1.03;
    }
    const h = w * R;
    const l = Math.min(0, Math.max(W - w, tx - BX * w)), t = Math.min(0, Math.max(H - h, ty - BY * h));
    const set = { left: `${l}px`, top: `${t}px`, width: `${w}px`, height: `${h}px`, 'object-fit': 'fill', 'max-width': 'none' };
    for (const k in set) img.style.setProperty(k, set[k]);
    field.style.setProperty('--bx', `${l + BX * w}px`);
    field.style.setProperty('--by', `${t + BY * h}px`);
  }
  place();
  addEventListener('resize', place, { passive: true });
  addEventListener('load', place);
  if (document.fonts) document.fonts.ready.then(place);
  /* the points step in from the left when the chapter is reached: measure
     again once they have landed */
  sell.addEventListener('reveal', () => setTimeout(place, 1800));
})();
