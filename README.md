# Rolls-Royce Motor Cars Palm Beach — home page

Static page. Open `index.html`; no build step, no dependencies.

```
RR/
├── index.html         the home page
├── inventory.html     the SRP — the four picks, the cards
├── vehicles/          one page per car (generated — do not edit)
├── css/tokens.css     palette, type, grid, motion
├── css/main.css       composition, sections, the card, motion (shared chrome)
├── css/inventory.css  the SRP: head, picks, grid
├── css/vehicle.css    the vehicle page: head, gallery, specifications
├── js/main.js         header bar, menu, reveals, films, section stepping, the home rail
├── js/inventory.js    the four picks and the sort over the cards in the page
├── js/vehicle.js      the gallery
├── data/inventory.json  the cars — every figure, photo and where it came from
├── tools/build.py     rebuilds the cards, the option lists and vehicles/ from the data
├── assets/fonts/      Riviera Nights Light + Regular, woff
├── assets/img/        photographs (webp) and the two film posters
├── assets/video/      the two films, 1080p and 720p, no audio track
├── VIDEOS/            the masters, as supplied (not used by the page)
└── DO NOTO GIT /      brand guidelines (confidential — see .gitignore)
```

Preview over a server that supports range requests — Safari will not play the
films from `python3 -m http.server`, which sends no `Accept-Ranges`.

## Source

Figma **Braman BRANDS** → page *UPD #2 Braman RR* → frame **“1920 version #2”**
(`193:2952`). That is the frame the shared prototype runs, and it is newer than
the frame named “1920”. Two differences worth knowing: version #2 has **no
Inventory section**, and it carries the header with seven routes.

Geometry is the file's: 12 columns, 30 gutter, 1320 measure, 300 margins at
1920; the chrome runs on its own 75px margin. At 1920 every element sits within
10px of the file — that difference is the scrollbar.

**Sections fill the screen at any size.** Heights are `100svh` rather than the
file's fixed 960/1080, and the vertical positions inside each section stay the
file's proportions of the section. A section whose copy needs more room grows
instead of clipping it.

## Colour

The palette is the brand's own (BRAND GUIDELINES → COLOUR VALUES); the Figma
fills already were these values: Purple Spirit `#281432`, Pearl `#E7D2C3`,
Sky `#B4C7CB`, Ultraviolet `#6D30A7`. Type is Frost or Noir, and the quieter
registers are tints of Frost rather than separate greys. The secondary control
is Steel `#676776` — the file drew it as `#5c5c6a`, which is not a brand colour
and gave a 2.8:1 edge on the dark ground; Steel gives 3.3:1.

Ultraviolet is the single highlight on the page (the Sell rules, and links on
light grounds). Aqua — the guidelines' link colour on dark grounds — is
deliberately unused, because the book allows one highlight per screen.

The one value outside the palette is the cinematic ground `#151515`, which is
the file's own and one step off Noir.

## Motion

The prototype looks scroll-driven but is not: each section is a component with
a `Default` and a `Variant2`, and the transition fires on **Mouse enter** —
scrolling past a resting pointer is what plays it. Here the same pairs fire when
a section reaches the middle of the viewport, once, and never reverse.

| Section | What moves | Clock |
|---|---|---|
| Hero | headline and button rise and fade in; the model name settles down | 1.0s, ease-out |
| Ghost | photograph rises inside its half; copy arrives from the right; buttons lift | 2.68s, spring |
| Spectre | mirrored, and the type turns from white to ink as it lands | 1.92s, spring |
| Cullinan | field settles upward as it lights; title and copy close; buttons close to centre | 1.92s, spring |
| About · Service | the photograph arrives from the side the section faces | 2.04s / 1.92s, spring |
| Black Badge | the frame opens from 991 × 557 to full screen; the mark, the line and the button climb in from below as a staircase | 1.1s frame · 0.9s copy, 140ms per tread |
| Sell | the three columns step in from the left, one after another, then the two calls rise | 0.9s, 140ms per tread |

Leaving is the same staircase, run upward: shorter (0.48s), quieter, and eased
in rather than out, so an exit never competes with an arrival.

“Spring” is Figma's **Gentle** (mass 1, stiffness 100, damping 15, 2.8%
overshoot), sampled into a CSS `linear()` easing in `tokens.css`.

**Cullinan and Black Badge are sticky sections**, in three beats. The field
(photograph, film) rises into its frame while the copy keeps its place; the
moment the composition matches the file, the field **pins** to the top of the
viewport; the copy then leaves upward over a standing picture, and the next
section arrives over it. Each section is the frame plus a hold of half a screen
and a tail of 0.6 — `--hold` and `--tail` in `main.css`. On mobile both are
dropped and the copy sits under the image.

## The header

Two states.

**At rest** (the first screen): no ground under it at all — the film, the mark
and the seven routes on the file's own lines, 139px tall.

**On scroll** it condenses to 112px and freezes over: the content behind it
blurs and a tint comes up with it. Everything stays in view — the seven routes
on their line, Roadside Assistance, My Garage and a telephone on theirs — just
drawn in tighter. There is no menu button on a desktop. Under 1024 the routes
cannot fit beside the mark, so there the bar is 84px with a menu button that
opens one full-screen panel: the routes stacked, the two services at its foot.

One ink throughout, and no ground switching: measured over every section, the
worst text contrast on the frozen bar is 6.4:1.

Two engineering notes. **The footer carries `position: relative; z-index: 1`**
because the listing and the vehicle page paint their pool of light as a
`position: fixed` pseudo-element inside `<main>`: a positioned `<main>` paints
above a static footer whatever the DOM order, and the pool covered the footer
whole — the footer was there, and invisible. And, from an afternoon lost
earlier: **do not soften the header's layer with `mask-image`.** A masked layer inside an element carrying `backdrop-filter`
stalls Chromium's compositor — the page stops painting new frames, silently.

## What is not the file, and why

- **14px floor.** The file sets MORE links, the utility row and the footer links
  at 12px. Functional text is held at 14px.
- **Legal line** lifted from `#5d5d5d` (2.5:1 on Purple Spirit) to a Frost tint
  at 5.4:1.
- **No scrim on the hero** — Alex's call, after the constructed pool read as a
  smudge on the pale dune frames. The consequence, measured on the delivered
  render: on the two palest shots the headline is about 2.3:1 and the navigation
  about 1.6:1, both under AA. Three ways to fix it without a visible wash:
  a light overall grade on the film (≈25%), a bottom vignette with the copy
  moved down into it, or re-cutting the film so the type never lands on a pale
  frame. `.hero__scrim` is still in the markup as the one place to put a ground
  back.
- **A pool of shadow behind the Black Badge copy**, which otherwise lands on the
  lit grille and headlamps: worst frame 4.6:1.
- **Typos fixed**: INVENOTRY → Inventory; the doubled copyright line; the double
  space in “Request Consultation”.
- **A pause control** on each film, and no film starts under `prefers-reduced-motion`.

## Scrolling

One gesture, one section. A wheel or trackpad gesture moves to the next stop and
never into the middle of a section; the stops are the section tops, the beat
inside a locked section where its copy has left, and the foot of any section
taller than the screen. Pointer devices only — on touch the long sections have
to stay reachable by ordinary scrolling — and PageUp / PageDown do the same on
every device.

## Inventory (SRP)

`inventory.html`. The card is the file's inventory card from the older frame
("1920" → inventory, `192:1231`): the 4:3 photograph, STOCK · MILEAGE, the
title, the price, the Provenance mark, hairlines between. Departures from
the file, all Alex's calls (2026-09-17):

- **The price is a tag** — a hairline pill on the same line as the mark —
  so it reads as a figure, not as another line of copy. On a new car the tag
  says `MSRP $539,725`, because that is the figure the dealer shows; on a
  pre-owned car it says `PRICE $427,900` (the dealer's "Braman Price").
- **The lease is the flag on the photograph** (`LEASE $6,486 / MO`, Purple
  Spirit, on the five cars where the dealer offers one) and nowhere else.
  The file's "Lease for" line is gone: on every car without a lease it had to
  say "On request", which is not a thing.
- The title is the car's name; "in West Palm Beach, FL" is its own small,
  quiet line under it. The foot is the colour, exterior over interior. Every
  card carries it, so every card ends on the same line.
- Every card links to the car's own page in `vehicles/`.

Above the grid: eyebrow, title, count, then **four picks on one line — Year,
Make, Model, Sort by** — each a label over a rule with the choice on it.
That is the whole search: the stock is thirty cars of one make and four
models, and Alex cut a five-group facet panel and a free-text field back to
this ("not a wildly detailed search — our inventory is very focused").
Three cards to a row from 1200 up, two under it, one on a phone.

**The ground is lit**: a wide pool of the brand's two purples — Ultraviolet
at the core, Purple Spirit around it — falling from above the head, and a
dimmer pool low on the right, on the cinematic ground. The layer is fixed,
so the cards scroll through the light. Worst text contrast on the lit
ground: 10.6:1 (the eyebrow at the top centre). The older Figma frame's
inventory section has the same pool above its cards.

**A model strip was built and cut** (2026-09-17): the Rolls-Royce pre-owned
locator's row of tiles, its photographs and taglines, as a sideways rail of
filters. It is recoverable — styles under "Model strip" in `inventory.css`,
photographs in `assets/img/models/`. The markup to put back, inside
`<main>` before `.wrap` (the filter logic would need restoring in
`inventory.js`):

```html
<section class="models" aria-label="Search by model">
  <ul class="models__row" id="models">
    <li class="tile"><button class="tile__button" type="button" data-model="" aria-pressed="true">
      <img class="tile__image" src="assets/img/models/all.webp" width="600" height="1160" alt="">
      <span class="tile__body"><span class="tile__name">All models</span><span class="tile__tag">Provenance certified pre-owned</span><span class="tile__cta">Search all models</span></span>
    </button></li>
    <!-- …and one <li class="tile"> per model: spectre, ghost, cullinan, phantom, wraith, dawn,
         with data-model="Spectre" etc. and aria-pressed="false" -->
  </ul>
</section>
```

**The cars are the dealer's real inventory** — thirty Rolls-Royce, 21 new
and 9 pre-owned, as listed at bramanrolls-roycepalmbeach.com on 2026-09-17
(`/search/new-rolls-royce/`, two pages, and `/search/used-rolls-royce/`),
captured to `data/inventory.json` with the source URLs and date. Each record
carries the headline figure the dealer shows (`price`, labelled by
`price_label`: MSRP on a new car, Braman Price on a used one), the sale
price with the two dealer charges, the MSRP and the lease where the dealer
shows them, the dealer's "Internet Special" flag, the spec fields from the
listing's JSON-LD, the dealer's "popular features", its description, and
its first six photographs (`assets/img/vdp/<stock>/`, 1400 wide, with a
420 thumbnail, and the source URL of each). The card photograph is the
dealer's first listing photo, cut to 4:3 at 840 wide. One car — the 2014
Phantom Drophead Coupé — has no photograph on the dealer's site and shows
the manufacturer render the dealer uses; its alt text says so.

**Everything the data touches is generated**: `python3 tools/build.py`
rewrites the cards and the option lists in `inventory.html`, the twelve
cards on the home rail, and every page in `vehicles/`. Edit the JSON, run
it, and the markup follows; do not edit those parts by hand.

- **Featured** is the page order: a row of pre-owned, two rows of new, and
  so on, each in the dealer's order — so the Provenance cars lead and the
  two stocks stay mixed. **Sort**: featured, price both ways, year, model.
  All of it is client-side over the cards already in the page; a feed can
  replace the markup and `inventory.js` will not need to know.
- **The Provenance mark** is the client's own lockup — monogram, name,
  "certified pre-owned" — supplied as a vector on 2026-09-17 and kept at the
  file's 107 × 49, on the pre-owned cards only. The builder inlines
  `assets/icons/provenance.svg` into each card with its paths on
  `currentColor`, so it draws in every browser with no mask and no second
  request, and takes its ink from the stylesheet; the sub-line is part of
  the artwork and is below reading size, so that meaning also sits in the
  page eyebrow.
- Cards climb in as a quiet staircase (60ms per card) on load and after every
  pick; the listing scrolls freely — section stepping is the home page's only.
- The Black Badge section's class is `.badge`; the card mark is `.cpo` for
  that reason — the stylesheet is shared.

## Inventory on the home page

Between Service and Sell, the older frame's inventory section is back (Alex,
2026-09-17): a rail of twelve cards — four screens of three — with an arrow
in each margin, and the file's Sky pill, VIEW ALL. The rail snaps a card at
a time; an arrow moves it a screen and goes quiet at its end. Under 1200 it
is two to a screen; under 1024 the arrows go and the rail bleeds to the
viewport edges for a swipe. A mostly sideways wheel gesture is left to the
rail; the section stepper only takes a vertical one. The three cards step in
from below and the call rises after them, on the Sell clock.

## Vehicle page (VDP)

`vehicles/<stock>.html`, one per car, generated. Not in the file — composed
in the listing's own registers on the same lit ground, and rebuilt on
2026-09-17 after a first version (a gallery beside a spec column) and a
second (a photo strip over three equal columns of hairline rows) were both
rejected — the second by Alex outright: everything in it had the same
weight, so nothing led. The page now has a dominant and a rank:

- **the photographs are the dominant** — a rail of the six frames, each
  at its own proportion and one height (62vh, capped), nothing cropped and
  nothing letterboxed, the first on the measure and the rest running off
  the right edge. It scrolls, snaps and **drags** with a throw (Alex asked
  for drag, and called a stage-with-thumbnails gallery "a very old way");
  under it, on the measure, a line that says where the rail is, the view
  switch, the count, and the two arrows. A mark in each frame's
  corner says it opens large; any frame opens full-screen in a `<dialog>`
  with arrows, keyboard and swipe, and the rail follows the viewer when it
  closes;
- **the 360° view** — the dealer's listing carries a turntable spin
  (DealerMade Next HD viewer: ~54 positions × three cameras). The widget
  itself cannot be embedded here: it looks its configuration up by the
  page's own host (`dealerWebsite` comes back null for any host but the
  dealer's), so on the dealer's domain it is their one script tag, and on
  this preview the spin is ours, built from their frames. Every car has
  one, so every page has one: **the second frame of the rail is the way
  in** — the first spin frame dimmed under a ring that says 360° and a
  label (a small pill on the first frame went unnoticed) — and the
  "360° view" switch in the foot is the second way in. Twenty-four frames
  of the middle camera, evenly picked, 1000 wide (`assets/img/spin/<stock>/`,
  16MB in all; the picks and the source are recorded in `spin_source`).
  They fetch when the view is first opened, with a thin line for progress;
  the car turns once by itself, then a drag turns it (one stage width is
  one turn), a throw keeps it turning and slows, the arrows and the
  keyboard step it a frame, a sideways wheel turns it too. The one car the
  dealer has no photographs of — the 2014 Phantom Drophead Coupé — shows a
  real frame from its spin instead of the manufacturer render, on its card
  and its page;
- **Save · Email · Text · Share** on the crumbs line, at the right. Save
  keeps the car in the visitor's browser (`localStorage`, key `rr-garage`,
  for a My Garage to pick up). The other three slide a **drawer** in from
  the right — "Pass it on" — and light the group asked for. Alex's brief:
  Text is for the visitor to text the car to someone or to themselves;
  Call goes, replaced by an email form to someone; Share is plain links to
  the networks. So: **Email** — To, your name, a message, "Send by email"
  opens the mail app with the subject, message and link ready; **Text** —
  a mobile number, "Send by text" opens Messages to that number with the
  link, or a line to your own phone; **Share** — Facebook, X, WhatsApp,
  Telegram, LinkedIn, Pinterest (with the first photograph), Copy the link
  (says "Copied"), and the device's own sheet where there is one. Nothing
  is sent from the page itself — every action hands off to the visitor's
  own app, so there is no backend to build. Escape, the scrim and the
  close button shut it; focus stays inside while it is open and returns to
  the tool that opened it. The drawer lives outside `<main>`, whose
  stacking context would keep it under the header;
- **the band above it** — crumbs, eyebrow (New · In stock, or Pre-owned ·
  Provenance certified), the name at one size under the file's H1 so it
  holds one line, and the figure beside it: the price tag and the lease flag;
- **the plate** — the four facts a buyer asks first, large: exterior,
  interior, mileage, engine;
- **the offer**, sticky at the right on a plate of its own (a hairline
  all round and a breath of ground, like the enquiry, so the right side
  stands apart from the copy) — the dealer's "Internet Special"
  flag where it shows one, the price at H1, the lease, MSRP and "you save"
  where the dealer shows them, the two dealer charges and the sale price,
  Request a Quote (to the enquiry) and Connect with a Specialist (dials
  sales), a route to financing, then the record in small rows: stock, VIN,
  transmission, drivetrain, fuel economy, doors. **The dealer's five
  actions are spread over the page, not stacked** (Alex: "I showed you
  what options they have so you'd distribute them"): Confirm Availability
  sits in the band beside the price; Get pre-approved under the pricing;
  Value your trade-in in the enquiry's lede;
- **Description**, beside the offer, as an accordion (Alex: "a separate
  section for the description, all the options, as an accordion"): the
  dealer's prose with its notes (CARFAX one-owner, clean CARFAX, priced
  below KBB, odometer below market — where the dealer says them);
  **Equipment & options**, the dealer's popular features merged with the
  equipment list in its description where there is one (up to 30 items,
  two columns of rows on rules); and the Provenance terms with the mark on
  a pre-owned car, folded by default. Where the dealer wrote no prose, the
  description group is one sentence assembled from the record and nothing
  else;
- **Enquire** — one band: the lede with the telephone and the trade-in
  route at the left; at the right the form as an object of its own — a
  plate on a hairline with boxed fields (name, email, telephone on a line,
  the message), Send at its foot. A first version drew the fields as bare
  rules and Alex could not tell it was a form. It submits nowhere yet;
- **More from the collection** — three cards, the same model first — and
  VIEW ALL.

On a small screen the offer bar (price, Enquire) follows the page once the
figure at the top has scrolled off, and steps aside while the offer or the
form is in view; on a desktop the sticky offer is the bar, so there is none.
The name steps in from the left, the figure lands, then the stage and the
strip rise, on the page's clock.

## For the server

`dist/` is the site and nothing else: the two pages, `vehicles/`, `css/`,
`js/`, `assets/`, `data/`. It is a copy, so re-copy it after any edit:

```
rm -rf dist && mkdir dist && cp index.html inventory.html dist/ && cp -R vehicles css js assets data dist/
```

**The preview server sends every file with `cache-control: max-age=31536000`
— a year.** A browser that has seen an earlier build keeps its stylesheet and
script and shows the new markup half-styled (2026-09-18: cards a screen
tall, the lease flag a plain underlined link, the vehicle page's "More"
cards the same). So `tools/build.py` stamps every css and js link with the
build time (`css/main.css?v=202609181317`): a new address is a new file to
the cache. Run the build before every hand-over, and reload the page once
after uploading — the HTML itself carries the same header, and a plain
reload is what fetches it fresh. Better still, in Plesk → Apache & nginx
settings → additional nginx directives:
`location ~* \.html$ { add_header Cache-Control "no-cache"; }`.

Upload its *contents* into `httpdocs/previews/BRAMAN_RR/`. About 80MB, of
which 47MB is the two films at two sizes, 14MB the vehicle photographs and
16MB the 360° frames.

## Fonts

**Cleared.** The client confirmed the fonts for this build (via Alex,
2026-09-16), so Riviera Nights Light and Regular are self-hosted from
`assets/fonts/`. The files themselves carry a retail licence covering preview
and print embedding; the client's confirmation is what this build stands on.

## Open

- **Links** are placeholders (`#`) except Inventory, the cards, the vehicle
  pages and the telephone numbers; the routing of the other buttons and the
  enquiry form is still to come.
- **Film weight** — 9.1MB at 1080p, 4.3MB at 720p, chosen by width, loaded only
  when its section is reached. The page before the film is 200KB.
