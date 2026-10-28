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
    # no "Private submission" over the form: the form starts level with the
    # first point (Alex, 2026-10-07)
    s = s.replace('<form class="sell__form" data-inbox novalidate>', '<form class="sell__form" data-inbox novalidate aria-label="Private submission">')
    s = re.sub(r'\s*<p class="sell__form-label">Private submission</p>', '', s)
    # the title on two lines (Alex, 2026-10-07)
    s = s.replace('id="sell-title">White Glove Acquisition &amp; Concierge<', 'id="sell-title">White Glove Acquisition<br> &amp; Concierge<')
    return s.replace('<img src="assets/img/sell.webp" width="2560" height="1707" loading="lazy"',
                     '<img src="assets/img/sell-coast-1920.webp" srcset="assets/img/sell-coast-1200.webp 1200w, assets/img/sell-coast-1920.webp 1920w" sizes="100vw" width="1920" height="1080" loading="lazy"')

# the routes land on version 4's own inner pages (tools/sub_v4.py, on the
# dealer's menu: Alex, 2026-10-28 "the menu as on the demo"): every route the
# bar, the dock, the footer and the home page's calls send to the dealer's
# site, or to nowhere ("#"), goes to the page built for it
ROUTES = {
    'Contact Us': 'contact_v4.html', 'Specials': 'specials_v4.html', 'Special Offers': 'specials_v4.html',
    'Sell Your Car': 'sell_v4.html', 'Parts / Service': 'service_v4.html', 'Finance': 'finance_v4.html',
    'Financing': 'finance_v4.html', 'About': 'about_v4.html', 'About Us': 'about_v4.html',
    'Value Your Trade': 'value-trade_v4.html', 'Quick Quote': 'quote-new_v4.html', 'Start Your Search': 'find-my-car_v4.html',
    'Rolls-Royce Lease Specials': 'specials_v4.html', 'Finance Center': 'finance_v4.html',
    'Apply for Financing': 'finance-application_v4.html', 'Make an Appointment': 'service-appointment_v4.html',
    'Schedule Appointment': 'service-appointment_v4.html', 'Schedule Service': 'service-appointment_v4.html',
    'Order Parts': 'order-parts_v4.html', 'Hours &amp; Directions': 'contact_v4.html#hours-h',
    'Meet Our Team': 'about_v4.html#team', 'Speak With a Specialist': 'contact_v4.html',
    'new specials': 'specials-new_v4.html', 'used specials': 'specials-used_v4.html',
}
def routes(s, up, home):
    for label, href in ROUTES.items():
        s = re.sub(rf'(<a(?: class="[^"]*")?) href="(?:#[a-z]*|https://www\.bramanrolls-roycepalmbeach\.com/[^"]*)"((?: [^>]*)?>){re.escape(label)}</a>',
                   lambda m: f'{m.group(1)} href="{up}{href}"{m.group(2)}{label}</a>', s)
    # the home page's chapter anchors from every other page
    if not home: s = s.replace('<a href="#models">Models</a>', f'<a href="{up}index_v4.html#models">Models</a>')
    return s

# the bar's routes are the dealer's menu (Alex, 2026-10-28: "where is the demo's
# drop-down?"): its groups and their lists, in its words and order, behind the
# Inventory pill the client keeps in view; a route lands on version 4's page
# where there is one, on the dealer's own page where there is not yet.
# A line without an address is the demo's own heading inside a list.
LIVE = 'https://www.bramanrolls-roycepalmbeach.com/'
MENU = [
    ('New', 'inventory_v4.html?condition=new', [
        ('Shopping Tools', None),
        ('View All New Inventory', 'inventory_v4.html?condition=new'),
        ('Schedule Test Drive', 'test-drive-new_v4.html'),
        ('Get a Quote', 'quote-new_v4.html'),
        ('Value Your Trade', 'value-trade_v4.html'),
        ('Rolls-Royce Spectre', LIVE + 'the-rolls-royce-spectre/'),
        ('Rolls-Royce Black Badge Ghost', LIVE + 'black-badge-ghost/'),
        ('Reasons to Choose Braman', 'difference_v4.html')]),
    ('Pre-Owned', 'inventory_v4.html?condition=used', [
        ('Pre-Owned Inventory', None),
        ('All Pre-Owned Vehicles', 'inventory_v4.html?condition=used'),
        ('One-Owner Vehicles', 'inventory_v4.html?condition=used'),
        ('Shopping Tools', None),
        ('Sell Us Your Vehicle', 'sell_v4.html'),
        ('Find My Car', 'find-my-car_v4.html'),
        ('Schedule Test Drive', 'test-drive-used_v4.html'),
        ('Value Your Trade', 'value-trade_v4.html'),
        ('Get a Quote', 'quote-used_v4.html')]),
    ('Bespoke Projects', None, [
        ('Available', 'inventory_v4.html?condition=new'),
        ('Future', LIVE + 'moonstone-pearl-rr-ghost/')]),
    ('Specials', 'specials_v4.html', [
        ('New Vehicle Specials', 'specials-new_v4.html'),
        ('Pre-Owned Vehicle Specials', 'specials-used_v4.html')]),
    ('Service', 'service_v4.html', [
        ('Service Department', 'service_v4.html'),
        ('Schedule Appointment', 'service-appointment_v4.html'),
        ('Ask a Tech', 'ask-a-tech_v4.html'),
        ('Vehicle Recall Request', 'recall_v4.html')]),
    ('Parts', 'parts_v4.html', [
        ('Parts Department', 'parts_v4.html'),
        ('Order Parts', 'order-parts_v4.html')]),
    ('Finance', 'finance_v4.html', [
        ('Personal Finance Application', 'finance-application_v4.html'),
        ('Business Finance Application', 'business-finance_v4.html'),
        ('Payment Calculator', 'calculator_v4.html')]),
    ('About Us', 'about_v4.html', [
        ('Learn More About Our Dealership', None),
        ('About Us', 'about_v4.html'),
        ('Directions', LIVE + 'directions/'),
        ('Hours', 'contact_v4.html#hours-h'),
        ('Privacy Policy', 'privacy_v4.html'),
        ('Testimonials', 'testimonials_v4.html'),
        ('Join Our Team', 'https://www.bramanmotorcars.com/current-job-opportunities/'),
        ('Rolls-Royce Blog', LIVE + 'blog/'),
        ('Contact', None),
        ('Contact Us', 'contact_v4.html'),
        ('Meet the Staff', 'about_v4.html#team')]),
]
CARET = '<svg viewBox="0 0 10 6" width="10" height="6" aria-hidden="true" focusable="false"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>'
def menu(up):
    url = lambda h: h if h.startswith('http') else up + h
    out = ['      <ul>', f'        <li class="header__nav-inventory"><a href="{up}inventory_v4.html">Inventory</a></li>']
    for i, (name, href, items) in enumerate(MENU):
        sid = 'nav-' + re.sub(r'[^a-z]+', '-', name.lower()).strip('-')
        head = f'<a href="{url(href)}">{name}</a>' if href else f'<span class="header__group-name">{name}</span>'
        rows = ''.join(f'\n            <li><a href="{url(h)}">{t}</a></li>' if h else f'\n            <li class="header__drop-label">{t}</li>' for t, h in items)
        out.append(f'''        <li class="header__group">
          <div class="header__group-head">{head}<button class="header__more" type="button" aria-expanded="false" aria-controls="{sid}" aria-label="{name}: more">{CARET}</button></div>
          <ul class="header__drop" id="{sid}">{rows}
          </ul>
        </li>''')
    out.append('      </ul>')
    return '\n'.join(out)

NAV = re.compile(r'(<nav class="header__nav" aria-label="Primary">\n)\s*<ul>.*?</ul>\n', re.S)
def dropdown(s, up):
    s = NAV.sub(lambda m: m.group(1) + menu(up) + '\n', s, count=1)
    hc = hashlib.md5(open(ROOT + 'css/menu_v4.css', 'rb').read()).hexdigest()[:10]
    hj = hashlib.md5(open(ROOT + 'js/menu_v4.js', 'rb').read()).hexdigest()[:10]
    s = re.sub(r'<link rel="stylesheet" href="(?:\.\./)?css/menu_v4\.css[^"]*">\n', '', s)
    s = re.sub(r'(<link rel="stylesheet" href="(?:\.\./)?css/v4\.css[^"]*">\n)', lambda m: m.group(1) + f'<link rel="stylesheet" href="{up}css/menu_v4.css?v={hc}">\n', s, count=1)
    s = re.sub(r'<script src="(?:\.\./)?js/menu_v4\.js[^"]*"></script>\n', '', s)
    return s.replace('</body>', f'<script src="{up}js/menu_v4.js?v={hj}"></script>\n</body>', 1)

def page(s, up='', home=False):
    return dropdown(routes(motion(script(sheet(grounds(relink(sell(pins(hero(s))))))), up), up, home), up)

write('index_v4.html', page(read('index_v3.html'), home=True))
write('inventory_v4.html', page(read('inventory_v3.html')))
os.makedirs(ROOT + 'vehicles_v4', exist_ok=True)
cars = sorted(f for f in os.listdir(ROOT + 'vehicles_v3') if f.endswith('.html'))
for f in os.listdir(ROOT + 'vehicles_v4'):
    if f.endswith('.html') and f not in cars: os.remove(ROOT + 'vehicles_v4/' + f)
for f in cars:
    write('vehicles_v4/' + f, page(read('vehicles_v3/' + f), '../'))
print('index_v4.html, inventory_v4.html,', len(cars), 'car pages in vehicles_v4/')
