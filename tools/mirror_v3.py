"""Version 3 (from version 2, on the client's note of 2026-10-04 — the same
note as the Bentley site's direction 7: an older clientele, desktop and
phone). Version 2 stays exactly as the client saw it (live at da79c55); every
version-3 page is written here from its version-2 source:
   - index_v3.html      from index_v2.html,
   - inventory_v3.html  from inventory.html,
   - vehicles_v3/<car>  from vehicles/<car>,
re-pointed to the version-3 set, with css/v3.css loaded last on each.
   - a normal, static page: no motion class, no section stepping
   - Inventory (marked), Specials, Finance and Contact Us always on screen:
     in the bar's routes on a wide screen, a bar at the foot below 1024
   - under the hero's title, static: New and Pre-Owned Inventory side by
     side, Special Offers beneath (the client's sketch)
Edit version 3 here and in css/v3.css, never in the pages it writes.
Run: python3 tools/mirror_v3.py"""
import os, re, hashlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
def read(p):  return open(ROOT + p, encoding='utf-8').read()
def write(p, s): open(ROOT + p, 'w', encoding='utf-8', newline='\n').write(s)

DEALER = 'https://www.bramanrolls-roycepalmbeach.com'
SPECIALS = DEALER + '/incentives/'            # "Finance Offers and Lease Specials"
FINANCE = DEALER + '/finance-department/'
CONTACT = DEALER + '/contact-us/'

# --- the version-3 set: every route home, to the inventory and to a car's
#     page leads inside it (version 2's SRP and car pages sent Models, Sell,
#     Service and About to the first home page, index.html)
def relink(s):
    s = s.replace('index_v2.html', 'index_v3.html')
    s = re.sub(r'((?:href|src)="(?:\.\./)?)index\.html', r'\1index_v3.html', s)
    s = s.replace('inventory.html', 'inventory_v3.html')
    s = s.replace('vehicles/', 'vehicles_v3/')
    return s

# --- static: the page opens without the motion class (every sheet then takes
#     its finished composition) and without section stepping
MOTION = re.compile(r'<script>(?:(?!</script>).)*classList\.add\("motion"\)(?:(?!</script>).)*</script>\n', re.S)
def calm(s):
    s = MOTION.sub('', s)
    return s.replace('<body data-scroll="sections">', '<body>', 1)

# --- the bar's routes: Inventory marked, Specials and Finance to the dealer's
#     own pages (version 2 left them at "#"); Contact Us joins the services' row
def routes(s, pre, home):
    here = '' if home else pre + 'index_v3.html'
    items = [
        (f'{here}#models', 'Models', ''),
        (f'{pre}inventory_v3.html', 'Inventory', ' class="header__nav-inventory"'),
        (SPECIALS, 'Specials', ''),
        (f'{here}#sell', 'Sell Your Car', ''),
        (f'{here}#service', 'Parts / Service', ''),
        (FINANCE, 'Finance', ''),
        ('#', 'Blog', ''),
        (f'{here}#about', 'About', ''),
    ]
    ul = '<ul>\n' + '\n'.join(f'        <li{c}><a href="{h}">{t}</a></li>' for h, t, c in items) + '\n      </ul>'
    s = re.sub(r'(<nav class="header__nav"[^>]*>\s*)<ul>.*?</ul>', lambda m: m.group(1) + ul, s, count=1, flags=re.S)
    # Contact Us beside the telephone, in the services' row: the routes' line
    # has no room for a ninth at 1024
    if 'header__contact' not in s:
        s = s.replace('<ul class="header__utility">', f'<ul class="header__utility">\n      <li class="header__contact"><a href="{CONTACT}">Contact Us</a></li>', 1)
    return s

# --- the foot bar, below 1024: the four the client named, each a word
def dock(s, pre):
    if 'class="dock"' in s: return s
    bar = (f'\n<nav class="dock" aria-label="Shop">\n'
           f'  <a class="dock__main" href="{pre}inventory_v3.html">Inventory</a>\n'
           f'  <a href="{SPECIALS}">Special Offers</a>\n'
           f'  <a href="{FINANCE}">Financing</a>\n'
           f'  <a href="{CONTACT}">Contact Us</a>\n'
           f'</nav>\n')
    return s.replace('</header>\n', '</header>\n' + bar, 1)

# --- under the hero's title: the client's three, static, in the place of
#     the commission button (the client's sketch boxes that place; the
#     commission keeps its own chapter, Bespoke, further down)
HERO_CTA = '<a class="btn btn--slate hero__cta" href="#bespoke" data-bespoke>Start a Bespoke Commission</a>'
def deck(s):
    if 'hero__deck' in s: return s
    new = ('<nav class="hero__deck" aria-label="Shop the inventory">\n'
           '        <a class="btn btn--white" href="inventory_v3.html?condition=new">New Inventory</a>\n'
           '        <a class="btn btn--white" href="inventory_v3.html?condition=used">Pre-Owned Inventory</a>\n'
           f'        <a class="btn btn--white hero__deck-offers" href="{SPECIALS}">Special Offers</a>\n'
           '      </nav>')
    assert HERO_CTA in s, 'the hero CTA moved in index_v2.html'
    return s.replace(HERO_CTA, new, 1)

# --- Black Badge: a photograph, not a still from the film (Alex,
#     2026-10-05: the Spectre Black Badge, black badge/blackbadge.png)
BADGE_OLD = '<img class="badge__film" src="assets/img/black-badge-poster.webp" alt="" width="1920" height="1080" loading="lazy" decoding="async">'
BADGE_NEW = ('<img class="badge__film" src="assets/img/black-badge-spectre.webp" '
             'srcset="assets/img/black-badge-spectre-1200.webp 1200w, assets/img/black-badge-spectre.webp 1920w" sizes="100vw" '
             'alt="" width="1920" height="1176" loading="lazy" decoding="async">')
def badge(s):
    if 'black-badge-spectre' in s: return s
    assert BADGE_OLD in s, 'the Black Badge frame moved in index_v2.html'
    return s.replace(BADGE_OLD, BADGE_NEW, 1)

# --- css/v3.css last on every page, stamped with its content
SHEET = re.compile(r'(<link rel="stylesheet" href="((?:\.\./)?)css/[^"]+">\n)(?!<link rel="stylesheet")')
def sheet(s):
    h = hashlib.md5(open(ROOT + 'css/v3.css', 'rb').read()).hexdigest()[:10]
    s = re.sub(r'<link rel="stylesheet" href="(?:\.\./)?css/v3\.css[^"]*">\n', '', s)
    m = list(SHEET.finditer(s))[-1]
    return s[:m.end()] + f'<link rel="stylesheet" href="{m.group(2)}css/v3.css?v={h}">\n' + s[m.end():]

# The client, 2026-10-05: the site terms in the first screen on a phone too.
# The bar's own terms link lives in the aside (moved by a transform), so the
# phone gets a line of its own, a direct child of the header.
TERMS = DEALER + '/terms-and-conditions/'
def terms_line(s):
    if 'header__terms-line' in s:
        return s
    line = f'\n  <a class="header__terms-line" href="{TERMS}">Site Terms &amp; Conditions</a>'
    return re.sub(r'(<header class="header"[^>]*>)', lambda m: m.group(1) + line, s, count=1)

def page(s, pre='', home=False):
    s = calm(relink(s))
    s = routes(s, pre, home)
    s = dock(s, pre)
    s = terms_line(s)
    if home: s = badge(deck(s))
    return sheet(s)

write('index_v3.html', page(read('index_v2.html'), home=True))
write('inventory_v3.html', page(read('inventory.html')))
os.makedirs(ROOT + 'vehicles_v3', exist_ok=True)
cars = sorted(f for f in os.listdir(ROOT + 'vehicles') if f.endswith('.html'))
for f in os.listdir(ROOT + 'vehicles_v3'):
    if f.endswith('.html') and f not in cars: os.remove(ROOT + 'vehicles_v3/' + f)
for f in cars:
    write('vehicles_v3/' + f, page(read('vehicles/' + f), pre='../'))
print('index_v3.html, inventory_v3.html,', len(cars), 'car pages in vehicles_v3/')
