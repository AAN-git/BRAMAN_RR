"""Version 4's inner pages: the Bentley site's inner-page template (direction 7,
../BRAMAN_BENTLEY) in the Rolls-Royce site's own colours and face (Kirsten,
2026-10-28: "follow the layout of those internal pages, just match the
colours"; Alex: light, black and white).

  - css/sub_v4.css is WRITTEN here: the Bentley inner pages' sheets, every rule
    held to the inner page's <main class="sub"> so the Rolls-Royce header, menu
    and footer keep their own sheets; then css/sub_v4.skin.css (written by
    hand), the Rolls-Royce face, ground, ink and controls over them. A fix to
    the Bentley template comes over at the next run.
  - js/sub_v4.js is WRITTEN here from the Bentley inner pages' scripts (the form
    labels, the dropdown's open list, the calculator, the films).
  - every pages_v4/<name>.main.html (written by hand) is wrapped in
    index_v4.html's head, header and footer as <name>_v4.html.

Never edit css/sub_v4.css, js/sub_v4.js or the pages it writes.
Run (Windows: PYTHONUTF8=1): python3 tools/sub_v4.py"""
import os, re, hashlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
BM = ROOT + '../BRAMAN_BENTLEY/'
def read(p, base=ROOT): return open(base + p, encoding='utf-8').read()
def write(p, s): open(ROOT + p, 'w', encoding='utf-8', newline='\n').write(s)
def stamp(p): return hashlib.md5(open(ROOT + p, 'rb').read()).hexdigest()[:10]

# --- the sheet ---------------------------------------------------------------
# the Bentley inner page's stack, in its own order (cards.css stays behind: the
# Rolls-Royce cards keep their own sheet)
SHEETS = ['system', 'index7', 'inventory7', 'vehicle7', 'day7', 'static7', 'subpages7']
SCOPE = 'main.sub'

def blocks(css):
    """Split a sheet into (prelude, body) pairs; body is None for a statement."""
    out, i, n = [], 0, len(css)
    while i < n:
        while i < n and css[i] in ' \t\r\n': i += 1
        if i >= n: break
        j = i
        while j < n and css[j] not in '{;': j += 1
        if j >= n: break
        if css[j] == ';':
            out.append((css[i:j].strip(), None)); i = j + 1; continue
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == '{': depth += 1
            elif css[k] == '}': depth -= 1
            k += 1
        out.append((css[i:j].strip(), css[j + 1:k - 1]))
        i = k
    return out

def split_top(s, sep=','):
    parts, depth, cur = [], 0, ''
    for ch in s:
        if ch in '([': depth += 1
        elif ch in ')]': depth -= 1
        if ch == sep and depth == 0: parts.append(cur); cur = ''
        else: cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]

def first_compound(sel):
    depth = 0
    for i, ch in enumerate(sel):
        if ch in '([': depth += 1
        elif ch in ')]': depth -= 1
        elif depth == 0 and ch in ' >+~': return sel[:i], sel[i:]
    return sel, ''

LOOK = re.compile(r':not\(\[data-look="\d"\]\)')
def scope(sel):
    """One selector held to the inner page's <main>, or None to drop it."""
    if re.search(r'(?<![\w-])\.card(?![\w-])|\.card__|(?<![\w-])\.grid(?![\w-])', sel):
        return None                      # the Rolls-Royce card and grid keep theirs
    head, rest = first_compound(sel)
    pre = ''
    if re.match(r'(html|:root)\b', head):
        if re.search(r'\[data-look="\d"\]', LOOK.sub('', head)): return None   # another look's
        head = LOOK.sub('', head)
        if head in ('html', ':root') and not rest.strip(): return SCOPE
        if head not in ('html', ':root'): pre = head + ' '
        rest = rest.lstrip(' >')
        if not rest: return None
        head, rest = first_compound(rest)
    if re.match(r'body\b', head):
        if head != 'body': return None
        rest = rest.lstrip(' >')
        if not rest: return pre + SCOPE
        head, rest = first_compound(rest)
    if re.match(r'(main\b|#main\b|\.(sub|srp)(?![\w-]))', head) or re.search(r'\.(sub|srp)(?![\w-])', head.split(':')[0]):
        return pre + SCOPE + re.sub(r'^main', '', head) + rest
    return pre + SCOPE + ' ' + head + rest

def scoped(css, hoist):
    out = []
    for pre, body in blocks(css):
        if body is None: continue                         # @import, @charset
        if pre.startswith('@font-face'): continue          # the Rolls-Royce face
        if pre.startswith('@keyframes'): hoist.append(f'{pre} {{{body}}}'); continue
        if pre.startswith('@'):
            inner = scoped(body, hoist)
            if inner.strip(): out.append(f'{pre} {{\n{inner}}}')
            continue
        sels = [s for s in (scope(x) for x in split_top(pre)) if s]
        if sels: out.append(f'{", ".join(sels)} {{{body.strip()} }}')
    return '\n'.join(out) + '\n'

def sheet():
    hoist, parts = [], []
    for name in SHEETS:
        css = re.sub(r'/\*.*?\*/', '', read(f'css/{name}.css', BM), flags=re.S)
        parts.append(f'/* --- {name}.css (Bentley) --- */\n' + scoped(css, hoist))
    skin = read('css/sub_v4.skin.css')
    head = ('/* WRITTEN by tools/sub_v4.py — do not edit. The Bentley inner pages\' sheets\n'
            '   (../BRAMAN_BENTLEY/css), held to main.sub, then css/sub_v4.skin.css. */\n')
    write('css/sub_v4.css', head + '\n'.join(hoist) + '\n' + '\n'.join(parts) + '\n/* --- the Rolls-Royce skin --- */\n' + skin)

# --- the script --------------------------------------------------------------
# from the Bentley page script only what an inner page uses: the layout width,
# the form labels, the dropdown's open list; the inner pages' script whole
KEEP = ('/* the layout width', '/* Form labels', '/* The open list of a dropdown')
def script():
    page = read('js/page7.js', BM)
    chunks = re.split(r'\n(?=/\*)', page)
    keep = [c for c in chunks if c.startswith(KEEP)]
    out = ('/* WRITTEN by tools/sub_v4.py from ../BRAMAN_BENTLEY/js/page7.js and sub7.js — do not edit. */\n'
           + '\n'.join(keep) + '\n' + read('js/sub7.js', BM))
    write('js/sub_v4.js', out)

# --- the pages ---------------------------------------------------------------
RR = ' | Rolls-Royce Motor Cars Palm Beach'
WPB = 'Rolls-Royce Motor Cars Palm Beach, West Palm Beach'
PAGES = {
    'contact': ('Contact Us' + RR,
                'Contact Rolls-Royce Motor Cars Palm Beach, 2801 Okeechobee Boulevard, West Palm Beach: sales 561-203-8780, service 561-277-3624, parts 561-203-8383, opening hours and directions.'),
    'about': ('About Us' + RR, f'About {WPB}: our sales, service and parts staff, opening hours and location.'),
    'finance': ('Finance Department' + RR, f'{WPB} finance department: apply for financing, value your trade, estimate a payment, or speak with the finance team.'),
    'finance-application': ('Finance Application' + RR, f'Apply for financing at {WPB}: the personal finance application. Sales 561-203-8780.'),
    'business-finance': ('Business Finance Application' + RR, f'Apply for business financing at {WPB}: the business finance application. Sales 561-203-8780.'),
    'calculator': ('Payment Calculator' + RR, f'Estimate a monthly payment at {WPB}: price, down payment, trade-in, rate and term.'),
    'service': ('Service Department' + RR, f'{WPB} service department: schedule service, service specials, ask a tech, safety recalls and our service staff. Service 561-277-3624.'),
    'service-appointment': ('Schedule Vehicle Service Appointment' + RR, f'Schedule a service appointment at {WPB}. Service 561-277-3624.'),
    'ask-a-tech': ('Ask a Tech' + RR, f'Ask a technician at {WPB}: describe the problem and a technician will contact you. Service 561-277-3624.'),
    'recall': ('Vehicle Recall Information Request' + RR, f'Check your vehicle for safety notices and recalls at {WPB}: a service representative will run a report. Service 561-277-3624.'),
    'parts': ('Parts Department' + RR, f'{WPB} parts department: order genuine parts, parts specials and service appointments. Parts 561-203-8383.'),
    'order-parts': ('Order Parts' + RR, f'Order genuine Rolls-Royce parts from {WPB}. Parts 561-203-8383.'),
    'test-drive-new': ('Schedule a New Vehicle Test Drive' + RR, f'Schedule a new vehicle test drive at {WPB}: choose a date and time to come in. Sales 561-203-8780.'),
    'test-drive-used': ('Schedule a Used Vehicle Test Drive' + RR, f'Schedule a pre-owned vehicle test drive at {WPB}: choose a date and time to come in. Sales 561-203-8780.'),
    'quote-new': ('Get a New Vehicle Quote' + RR, f'Get a sales quote on a new vehicle from {WPB}. Sales 561-203-8780.'),
    'quote-used': ('Get a Used Vehicle Quote' + RR, f'Get a sales quote on a pre-owned vehicle from {WPB}. Sales 561-203-8780.'),
    'value-trade': ('Vehicle Trade-In Value' + RR, f'Find out what your vehicle may be worth at {WPB}: tell us about it and our team will contact you. Sales 561-203-8780.'),
    'sell': ('Sell Your Vehicle' + RR, f'Sell your vehicle to {WPB}: tell us about it and our team will contact you shortly. Sales 561-203-8780.'),
    'find-my-car': ('Find My Car' + RR, f'{WPB} can find nearly any vehicle you are looking for: tell us what you want and we will begin a search. Sales 561-203-8780.'),
    'specials': ('All Inventory Specials' + RR, f'All inventory specials at {WPB}: new and pre-owned motor cars on special.'),
    'specials-new': ('New Inventory Specials' + RR, f'New inventory specials at {WPB}.'),
    'specials-used': ('Used Inventory Specials' + RR, f'Pre-owned inventory specials at {WPB}.'),
    'testimonials': ('Testimonials' + RR, f'Customer testimonials for {WPB}, from DealerRater.'),
    'privacy': ('Privacy Policy' + RR, 'The privacy policy of Rolls-Royce Motor Cars Palm Beach.'),
    'difference': ('Reasons to Choose Braman' + RR, 'Reasons to choose Braman Motorcars: PermaPlate protection, Nitro-filled tires, our service departments, parts and boutiques.'),
}

# a specials page's cars: <!-- STOCKS ids="R65004,R65386" --> is filled with the
# listing's own cards for those stock numbers, in that order (a sold car drops
# out), and {{N}} with their count; the cards keep the listing's own sheet, on
# the light ground the listing gives them (data-coast)
CARDS = re.findall(r'\n(\s*<li class="card"[^>]*>.*?\n\s*</li>)', read('inventory_v4.html'), re.S)
def stocks(body):
    m = re.search(r'<!-- STOCKS ids="([^"]+)" -->', body)
    if not m: return body
    pick = [c for i in m.group(1).split(',') for c in CARDS if f'data-stock="{i}"' in c]
    grid = '<div class="sub__cards" data-coast="sub"><ul class="sub__cards-grid">\n' + '\n'.join(pick) + '\n      </ul></div>'
    n = len(pick)
    return body.replace(m.group(0), grid).replace('{{N}}', f'{n} Motor Car{"s" if n != 1 else ""}')

def pages():
    home = read('index_v4.html')
    head, rest = home.split('<main id="main">', 1)
    foot = rest.split('</main>', 1)[1]
    head = re.sub(r'<link rel="preload" href="assets/img/[^>]*>\n', '', head)
    head = head.replace('</head>', f'<link rel="stylesheet" href="css/sub_v4.css?v={stamp("css/sub_v4.css")}">\n</head>', 1)
    # the home page's pinned chapters have nothing to pin here: GSAP stays home
    foot = re.sub(r'<script src="https://unpkg\.com/gsap[^"]*"></script>\n', '', foot)
    foot = re.sub(r'<script src="js/v4\.js[^"]*"></script>\n', '', foot)
    foot = foot.replace('</body>', f'<script src="js/sub_v4.js?v={stamp("js/sub_v4.js")}" defer></script>\n</body>', 1)
    for name, (title, desc) in PAGES.items():
        h = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', head, count=1, flags=re.S)
        h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h, count=1)
        out = h + stocks(read(f'pages_v4/{name}.main.html')).rstrip() + '\n' + foot
        out = re.sub(rf'(<a href="{name}_v4\.html")(>)', r'\1 aria-current="page"\2', out)
        write(f'{name}_v4.html', out)
        print(f'{name}_v4.html')

if __name__ == '__main__':
    sheet(); script(); pages()
