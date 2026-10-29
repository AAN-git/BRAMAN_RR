# Rolls-Royce Motor Cars Palm Beach — project notes

See README.md for the build. The Bentley site (../BRAMAN_BENTLEY, its
CLAUDE.md) gets the same client notes.

## Feedback log

- **Client baseline:** v2 (`index_v2.html`, `inventory.html`, `vehicles/`, and
  `catalog.html`) as live at da79c55. Never edit it. Version 3 (`index_v3.html`,
  `inventory_v3.html`, `vehicles_v3/`) is written by `tools/mirror_v3.py` from
  v2, with `css/v3.css` last — edit only those two, then run the script.
  Pushed 2026-10-05 (788d42a).
- **Client note 2026-10-04 (both sites):** older clientele; a static page (no
  scroll stepping, no pinned sections, no video); Inventory, Specials,
  Financing, Contact Us always on screen (bar routes on desktop, foot bar below
  1024); under the hero, New | Pre-Owned Inventory with Special Offers beneath.
- **Phone (Alex, 2026-10-05, repeated):** no holes between or inside
  sections; copy in the regular cut at 18px, never light and small, never long
  text in capitals, never words over a busy photograph; what is boxed on
  desktop is boxed on the phone; buttons full width. Measure section gaps at
  390, ~470 and ~660 before reporting.
- **Don't touch what already works:** change only what was asked.
- **Black Badge image:** `black badge/blackbadge.png` (Spectre Black Badge);
  on desktop its words stand on the floor beneath the car.
- **Hero (v3):** the three buttons replace the commission button; the lockup
  sits on the road below the car — raised as far as it goes without touching it.
- **Inner pages (Kirsten via Alex, 2026-10-28):** every page made for the
  Bentley site comes to this one — the Bentley inner pages' layout in the
  Rolls-Royce colours, light: Frost ground, Noir ink, the dark plate Noir,
  Riviera Nights, titles in capitals, the pill button in Ultraviolet, the bar
  solid Purple Spirit as on the listing and car pages. The page list is the
  dealer's demo menu; words, staff, direct lines and forms from the demo
  (bramanrolls-roycepalmbeach.aandemo.com), verbatim. Built by tools/sub_v4.py
  (README). SRP and VDP stay as they are.
- **Rolls-Royce photographs (Alex, 2026-10-28):** every car shown is a 2026
  model (Phantom, Ghost / Ghost Extended Series II, Cullinan Series II, Spectre
  Series II, Black Badge); from rolls-roycemotorcars.com and Braman's own
  pictures — never the PressClub (editorial use only). Words never on a whole
  car; on a large detail they may lie ("главное какое фото"). Specials: the
  whole car zoomed out, or a zoomed-in detail.
- **The bar's menu is the dealer's (Alex, 2026-10-28, "where is the demo's
  drop-down?"):** the demo's groups and lists in its words and order (New,
  Pre-Owned, Bespoke Projects, Specials, Service, Parts, Finance, About Us),
  behind the Inventory pill (2026-10-28: Inventory carries the demo's New
  shopping tools, New lists the 2026–27 models); lists drop on a Purple Spirit plate on hover /
  focus / first tap, open by caret in the phone panel (tools/mirror_v4.py
  MENU, css/menu_v4.css, js/menu_v4.js). A route without a git page goes to
  the dealer's own. The demo is the real site, unfinished: git builds the
  pages it lacks and hands them to development.
- **Model pages (Alex, 2026-10-28):** chapter for chapter the Bentley site's
  model page (BRAMAN_BENTLEY pages7/bentayga-speed.main.html: hero, statement,
  exterior + details, interior, the drive WITH FIGURES, Bespoke as
  personalisation, in stock, enquiry). Words verbatim from
  rolls-roycemotorcars.com (US) — check every page against it, words and
  photographs of that model only. Figures: the US site states none, so they
  come from Rolls-Royce's own press releases (PressClub text only, never its
  photographs). Hero tagline two lines at most.
  The hero's words lie over the frame as on Spectre: pick a frame where they
  clear the car (car at the right) or lie on a large detail — never invent a
  layout for it (a words-under-the-frame band was rejected: "откуда это
  взялось? у Bentley такого не помню"). Parts pictures are car parts, never
  accessories (umbrella, bag rejected).
