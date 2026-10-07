"""Version 4 (from version 3, on the client's note of 2026-10-07: "brighten up
the Rolls site a bit with some more coastal background colors rather than
black"). Version 3 stays exactly as the client saw it; every version-4 page is
written here from its version-3 source:
   - index_v4.html      from index_v3.html,
   - inventory_v4.html  from inventory_v3.html,
   - vehicles_v4/<car>  from vehicles_v3/<car>,
re-pointed to the version-4 set, with css/v4.css loaded last on each.
The colours are the brand's own supporting backgrounds (BRAND GUIDELINES →
COLOUR USE): Frost, Pearl and Sky in place of black on the home page's
Inventory, Sell and Bespoke, and on the listing and the car pages. Black
stays where the guidelines keep it — Black Badge — and Purple Spirit closes
the page.
Edit version 4 here and in css/v4.css, never in the pages it writes.
Run: python3 tools/mirror_v3.py && python3 tools/mirror_v4.py"""
import os, re, hashlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
def read(p):  return open(ROOT + p, encoding='utf-8').read()
def write(p, s): open(ROOT + p, 'w', encoding='utf-8', newline='\n').write(s)

def relink(s):
    s = s.replace('index_v3.html', 'index_v4.html')
    s = s.replace('inventory_v3.html', 'inventory_v4.html')
    s = s.replace('vehicles_v3/', 'vehicles_v4/')
    return s

# the chapters that turn light say so, so the focus ring and anything else
# keyed to the ground follow them
LIGHT = [('stock', 'inventory'), ('sell', 'sell'), ('bespoke', 'bespoke')]
def grounds(s):
    for cls, id_ in LIGHT:
        s = re.sub(rf'(<section class="{cls}" id="{id_}") data-ground="dark"', rf'\1 data-ground="light" data-coast="{cls}"', s, count=1)
    s = re.sub(r'(<main id="main" class="(srp|vdp)") data-ground="dark"', r'\1 data-ground="light" data-coast="\2"', s, count=1)
    return s

SHEET = re.compile(r'(<link rel="stylesheet" href="((?:\.\./)?)css/v3\.css[^"]*">\n)')
def sheet(s):
    h = hashlib.md5(open(ROOT + 'css/v4.css', 'rb').read()).hexdigest()[:10]
    s = re.sub(r'<link rel="stylesheet" href="(?:\.\./)?css/v4\.css[^"]*">\n', '', s)
    m = SHEET.search(s)
    return s[:m.end()] + f'<link rel="stylesheet" href="{m.group(2)}css/v4.css?v={h}">\n' + s[m.end():]

# the hero's line and Black Badge's, shortened (Alex, 2026-10-07)
def hero(s):
    s = s.replace('An Elegant Story in Paint,<br> Leather, Wood and Metal', 'An Elegant Story in Paint')
    return s.replace('Black Badge is a formidable alter ego. Boldly crafted and designed with enhanced power, torque, and control.', 'Black Badge is a formidable alter ego.')

# the home page's Black Badge still is placed by js/v4.js
def script(s):
    if 'class="badge__film"' not in s: return s
    h = hashlib.md5(open(ROOT + 'js/v4.js', 'rb').read()).hexdigest()[:10]
    s = re.sub(r'<script src="js/v4\.js[^"]*"></script>\n', '', s)
    return s.replace('</body>', f'<script src="js/v4.js?v={h}"></script>\n</body>', 1)

# the scroll: Lenis on every version-4 page; GSAP for the home page's pins
CDN = ['https://unpkg.com/gsap@3.15.0/dist/gsap.min.js',
       'https://unpkg.com/gsap@3.15.0/dist/ScrollTrigger.min.js',
       'https://unpkg.com/gsap@3.15.0/dist/SplitText.min.js',
       'https://unpkg.com/lenis@1.3.26/dist/lenis.min.js']
def motion(s, up):
    s = re.sub(r'<script src="(?:https://unpkg\.com/(?:gsap|lenis)[^"]*|(?:\.\./)?js/v4-motion\.js[^"]*)"></script>\n', '', s)
    h = hashlib.md5(open(ROOT + 'js/v4-motion.js', 'rb').read()).hexdigest()[:10]
    tags = ''.join(f'<script src="{u}"></script>\n' for u in CDN) + f'<script src="{up}js/v4-motion.js?v={h}"></script>\n'
    return s.replace('</body>', tags + '</body>', 1)

# the old copy exit on the locked sections gives way to the pins
def pins(s):
    return s.replace(' data-reveal data-exit aria-labelledby="cullinan-title"', ' data-reveal aria-labelledby="cullinan-title"') \
            .replace(' data-reveal data-exit aria-labelledby="badge-title"', ' data-reveal aria-labelledby="badge-title"')

# Sell's ground: Alex's photograph of the paint and the badge (2026-10-07)
def sell(s):
    return s.replace('<img src="assets/img/sell.webp" width="2560" height="1707" loading="lazy"',
                     '<img src="assets/img/sell-coast-1920.webp" srcset="assets/img/sell-coast-1200.webp 1200w, assets/img/sell-coast-1920.webp 1920w" sizes="100vw" width="1920" height="1080" loading="lazy"')

def page(s, up=''):
    return motion(script(sheet(grounds(relink(sell(pins(hero(s))))))), up)

write('index_v4.html', page(read('index_v3.html')))
write('inventory_v4.html', page(read('inventory_v3.html')))
os.makedirs(ROOT + 'vehicles_v4', exist_ok=True)
cars = sorted(f for f in os.listdir(ROOT + 'vehicles_v3') if f.endswith('.html'))
for f in os.listdir(ROOT + 'vehicles_v4'):
    if f.endswith('.html') and f not in cars: os.remove(ROOT + 'vehicles_v4/' + f)
for f in cars:
    write('vehicles_v4/' + f, page(read('vehicles_v3/' + f), '../'))
print('index_v4.html, inventory_v4.html,', len(cars), 'car pages in vehicles_v4/')
