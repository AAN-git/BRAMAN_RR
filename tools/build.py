"""Build everything that comes from data/inventory.json:
   - the cards in inventory.html (and its year / model option lists),
   - the twelve cards on the home page's inventory rail,
   - one vehicle page per car in vehicles/, from the SRP's own chrome.
Run from anywhere: python3 tools/build.py"""
import json, re, html, os
from collections import Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
d = json.load(open(ROOT + 'data/inventory.json'))

# The preview server sends every file with cache-control: max-age of a year,
# so a browser that saw an earlier build keeps its stylesheet and script
# until told otherwise. Every build stamps the css and js links with the
# build time; a new address is a new file to the cache.
import datetime
STAMP = datetime.datetime.now().strftime('%Y%m%d%H%M')
def stamp(html):
    html = re.sub(r'((?:href|src)="(?:\.\./)?(?:css|js)/[^"?]+)(?:\?v=[^"]*)?"', lambda m: m.group(1) + '?v=' + STAMP + '"', html)
    return html
V = d['vehicles']
e = html.escape

def money(n): return '${:,}'.format(n)

# --- Featured order — rows of three: a row of pre-owned, then two rows of new,
#     and again, each group in the dealer's own order. Pre-owned leads so the
#     Provenance cars are the first thing on the page, and the two stocks stay
#     mixed all the way down rather than one stacked under the other.
new_cars = [v for v in V if v['condition'] == 'new']
used_cars = [v for v in V if v['condition'] != 'new']
featured = []
while new_cars or used_cars:
    featured += used_cars[:3]; del used_cars[:3]
    featured += new_cars[:6]; del new_cars[:6]

# --- The mark: the client's Provenance lockup, inlined so it needs no mask
#     and no second request; its ink is currentColor, set in the stylesheet.
MARK = open(ROOT + 'assets/icons/provenance.svg').read().strip()
MARK = MARK.replace('<svg ', '<svg class="cpo" role="img" aria-label="Provenance, certified pre-owned" focusable="false" ', 1)
CHEVRON = '<path d="M1.414 0L9.07 7.79778L7.656 9.23796L0 1.44019L1.414 0ZM14.3614 0L15.7754 1.44019L11.5573 5.58656L10.1433 4.14536L14.3614 0Z"/>'

def name_of(v):
    return f"{v['year']} Rolls-Royce {v['model']}" + (f" {v['trim']}" if v['trim'] else '')

def lease_text(v, short=True):
    if not v['lease_month']: return ''
    tax = ' + tax' if v['lease_plus_tax'] else ''
    return f"Lease {money(v['lease_month'])}{tax} / mo" if short else f"{money(v['lease_month'])}{tax} / month"

# --- One card. `p` is the path prefix to the site root ('' or '../').
def card(v, p='', eager=False):
    flag = f'<span class="card__flag">{lease_text(v)}</span>' if v['lease_month'] else ''
    alt = f'{v["exterior"]} {v["year"]} Rolls-Royce {v["model"]}' + (' — manufacturer image; the dealer has no photograph of this car' if v['stock_image'] else '')
    mark = ('\n              ' + MARK) if v['condition'] == 'used' else ''
    label = 'MSRP' if v['condition'] == 'new' else 'Price'
    return f'''        <li class="card" data-condition="{v['condition']}" data-year="{v['year']}" data-price="{v['price']}" data-mileage="{v['mileage']}" data-model="{e(v['model'])}" data-trim="{e(v['trim'])}" data-stock="{e(v['stock'])}" data-vin="{e(v['vin'])}">
          <a class="card__link" href="{p}{v['page']}" aria-label="{e(v['title'])}, {label} {money(v['price'])}">
            <span class="card__media">{flag}<img src="{p}{v['image']}" width="840" height="630" loading="{'eager' if eager else 'lazy'}" decoding="async" alt="{e(alt)}"></span>
            <dl class="card__facts">
              <div><dt>Stock:</dt> <dd>{e(v['stock'])}</dd></div>
              <div><dt>Mileage</dt> <dd>{'{:,}'.format(v['mileage'])}</dd></div>
            </dl>
            <h2 class="card__title">{e(v['title'])} <span class="card__place">in West Palm Beach, FL</span></h2>
            <div class="card__row">
              <p class="card__price"><span class="card__price-label">{label}</span> <span class="card__price-value">{money(v['price'])}</span><span class="asterisk" aria-hidden="true">*</span></p>{mark}
            </div>
            <dl class="card__spec">
              <div><dt>Exterior</dt> <dd>{e(v['exterior'])}</dd></div>
              <div><dt>Interior</dt> <dd>{e(v['interior'])}</dd></div>
            </dl>
          </a>
        </li>'''

# =========================================================================
# 1. The SRP: the grid and the option lists
# =========================================================================
cards = [card(v, '', eager=i < 3) for i, v in enumerate(featured)]
grid = '<ul class="grid" id="grid">\n' + '\n'.join(cards) + '\n    </ul>'
years = sorted(Counter(v['year'] for v in V), reverse=True)
order = ['Cullinan', 'Ghost', 'Phantom', 'Spectre', 'Wraith', 'Dawn']
models = [m for m in order if any(v['model'] == m for v in V)] + sorted({v['model'] for v in V} - set(order))
def options(first, values):
    return '\n'.join([f'          <option value="">{first}</option>'] + [f'          <option value="{v}">{v}</option>' for v in values])

path = ROOT + 'inventory.html'
srp = open(path).read()
srp = re.sub(r'<ul class="grid" id="grid">.*?</ul>', lambda m: grid, srp, count=1, flags=re.S)
srp = re.sub(r'(<select class="pick__select" name="year" data-pick="year">\n).*?(\n        </select>)', lambda m: m.group(1) + options('All years', years) + m.group(2), srp, count=1, flags=re.S)
srp = re.sub(r'(<select class="pick__select" name="model" data-pick="model">\n).*?(\n        </select>)', lambda m: m.group(1) + options('All models', models) + m.group(2), srp, count=1, flags=re.S)
srp = re.sub(r'<span data-count>\d+</span>', f'<span data-count>{len(V)}</span>', srp)
# the footnote under the listing: the dealer's disclosure, verbatim
legal = d.get('price_disclaimer') or ''
srp = re.sub(r'<p class="srp__legal" id="legal">.*?</p>', lambda m: f'<p class="srp__legal" id="legal">{e(legal)}</p>', srp, count=1, flags=re.S)
srp = stamp(srp)
open(path, 'w').write(srp)
print(len(cards), 'cards in inventory.html;', len(years), 'years,', len(models), 'models')

# =========================================================================
# 2. The home page: the first twelve of the featured order on the rail
# =========================================================================
home = '<ul class="stock__row">\n' + '\n'.join(cards[:12]) + '\n        </ul>'
path = ROOT + 'index.html'
idx = open(path).read()
if '<ul class="stock__row">' in idx:
    idx = re.sub(r'<ul class="stock__row">.*?</ul>', lambda m: home, idx, count=1, flags=re.S)
    first_two = ' '.join(re.split(r'(?<=\.)\s+', (d.get('price_disclaimer') or ''))[:2])
    idx = re.sub(r'<p class="stock__legal">.*?</p>', lambda m: f'<p class="stock__legal">{e(first_two)} <a href="inventory.html#legal">Full pricing details</a>.</p>', idx, count=1, flags=re.S)
    idx = stamp(idx)
    open(path, 'w').write(idx)
    print('12 cards in index.html')

# =========================================================================
# 3. The vehicle pages — the SRP's head, header and footer, paths lifted a
#    level, and the car between them.
# =========================================================================
head = re.search(r'<head>.*?</head>', srp, re.S).group(0)
header = re.search(r'<a class="skip".*?</header>', srp, re.S).group(0)
footer = re.search(r'<!-- LAST MASS.*?</footer>', srp, re.S).group(0)
def lift(s):
    s = re.sub(r'(href|src)="(assets/|css/|js/|index\.html|inventory\.html)', r'\1="../\2', s)
    s = s.replace('href="./"', 'href="../"')
    return s
head = re.sub(r'href="\.\./css/inventory\.css[^"]*"', 'href="../css/vehicle.css"', lift(head))   # the vehicle page has its own sheet
header = lift(header); footer = lift(footer)

def strip_spec_sentence(t):
    # the new copy opens with a spec line: "Arctic White 2027 Rolls-Royce Cullinan Black Badge AWD ZF 8-Speed Automatic V12. We are…"
    return re.sub(r'^[^.]*?(V12|Automatic|AWD|RWD)\.?\s*', '', t).strip()

DRIVE = {'AWD': 'all-wheel drive', 'RWD': 'rear-wheel drive'}
def overview(v):
    """The dealer's prose where there is some; otherwise one factual sentence
    assembled from the record — nothing in it that is not in the data."""
    prose = strip_spec_sentence(v['description'])
    if len(prose) > 60: return prose
    engine = 'V12' if (v['engine'] or '').startswith('V12') or '6.75L' in (v['engine'] or '') else (v['engine'] or '')
    parts = [f"A {'new' if v['condition']=='new' else 'pre-owned'} {v['year']} Rolls-Royce {v['model']}{' ' + v['trim'] if v['trim'] else ''} in {v['exterior']} over {v['interior']}, with {'{:,}'.format(v['mileage'])} miles."]
    drive = [x for x in [engine, (v['transmission'] or '').replace('ZF 8-Speed Automatic', 'ZF eight-speed automatic'), DRIVE.get(v['drivetrain'] or '', '')] if x]
    if drive: parts.append(', '.join(drive) + '.')
    parts.append('Available now at Rolls-Royce Motor Cars Palm Beach.')
    return ' '.join(parts)

def rows(pairs):
    return '\n'.join(f'              <div><dt>{e(k)}</dt><dd>{val}</dd></div>' for k, val in pairs if val)

def vehicle_page(v):
    p = '../'
    name = name_of(v)
    used = v['condition'] == 'used'
    eyebrow = 'Pre-owned · Provenance certified' if used else 'New · In stock'
    label = 'MSRP' if v['condition'] == 'new' else 'Price'
    photos = v['photos'] or [{'src': v['image'], 'thumb': v['image'], 'w': 840, 'h': 630}]
    stock_note = ' (manufacturer image — the dealer has no photograph of this car)' if v['stock_image'] else ''
    spin = json.dumps([f"{p}{f}" for f in v['spin']])
    spin_tile = ''
    if v['spin']:
        spin_tile = f'''
      <li class="film__frame film__frame--spin"><button class="film__launch" type="button" aria-label="View the motor car in 360°"><img src="{p}{v['spin'][0]}" width="1000" height="667" loading="lazy" decoding="async" alt=""><span class="film__launch-mark"><span class="film__launch-ring"><svg viewBox="0 0 96 96" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" focusable="false"><path d="M12 48a36 36 0 1 0 6-20"/><path d="M14 20l4 9 9-4"/></svg><span>360°</span></span><span class="film__launch-label">View in 360°</span></span></button></li>'''
    frames = '\n'.join(
        f'''      <li class="film__frame"><button class="film__open" type="button" data-index="{i}" aria-label="Photograph {i + 1} of {len(photos)} — open full-screen"><img src="{p}{ph['src']}" width="{ph['w']}" height="{ph['h']}" loading="{'eager' if i < 2 else 'lazy'}" decoding="async" alt="{e(v['exterior'])} {e(name)}{stock_note if i == 0 else ''}"><span class="film__expand" aria-hidden="true"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" focusable="false"><path d="M1 6V1h5M10 1h5v5M15 10v5h-5M6 15H1v-5"/></svg></span></button></li>''' + (spin_tile if i == 0 else '')
        for i, ph in enumerate(photos))
    sources = json.dumps([f"{p}{ph['src']}" for ph in photos])
    features = '\n'.join(f'              <li>{e(f)}</li>' for f in v['features'])
    engine_short = 'Electric' if 'Electric' in (v['engine'] or '') else ('V12' if 'V12' in (v['engine'] or '') else (v['engine'] or ''))
    lease_row = f"{money(v['lease_month'])}{' + tax' if v['lease_plus_tax'] else ''} / month" if v['lease_month'] else ''

    # the buy box: the price large, then what the dealer shows around it
    around = []
    if used and v['msrp']:
        around += [('MSRP', money(v['msrp'])), ('You save', f"− {money(v['msrp'] - v['price'])}")]
    if v['sale_price_with_fees']:
        around += [('Dealer service charge', '$1,189'), ('Electronic filing charge', '$514'), ('Sale price', money(v['sale_price_with_fees']))]
    facts = [
        ('Stock', e(v['stock'])), ('VIN', f'<span class="vdp__vin">{e(v["vin"])}</span>'),
        ('Transmission', e(v['transmission'] or '')), ('Drivetrain', e(v['drivetrain'] or '')),
        ('Fuel economy', f"{v['mpg']} mpg" if v['mpg'] else ''), ('Doors', e(str(v['doors'] or ''))),
    ]

    prose = strip_spec_sentence(v['description'])
    notes = ''.join(f'<li>{e(n)}</li>' for n in v['notes'])
    equipment = '\n'.join(f'              <li>{e(x)}</li>' for x in v['equipment'])
    def fold(key, title, body, open_=True):
        return f'''
          <details class="fold" {'open' if open_ else ''}>
            <summary class="fold__head"><span>{title}</span><svg class="fold__chevron" viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></summary>
            <div class="fold__body">
{body}
            </div>
          </details>'''
    description = ''
    if prose or notes:
        description = fold('description', 'Vehicle description', (f'              <p class="vdp__copy">{e(prose)}</p>' if prose else '') + (f'\n              <ul class="vdp__notes">{notes}</ul>' if notes else ''))
    options = fold('equipment', 'Equipment &amp; options', f'              <ul class="vdp__features">\n{equipment}\n              </ul>') if v['equipment'] else ''
    provenance = ''
    if used:
        provenance = fold('provenance', 'Provenance certified pre-owned', f'''              <div class="vdp__provenance-body">
                {MARK}
                <p class="vdp__copy">A transferable warranty with a $0 deductible, limited warranty for up to 24 months with unlimited mileage, a multipoint inspection, the vehicle's history, and roadside assistance.</p>
              </div>''', open_=False)
    gallery_note = f'{v["photo_count_at_dealer"]} photographs at <a href="{e(v["dealer_url"])}">the dealer\'s listing</a>' if v['photo_count_at_dealer'] > len(photos) else ('Manufacturer image; the dealer has no photograph of this car' if v['stock_image'] else '')

    # the disclosure: the dealer's own text, and the lease terms as the dealer states them
    disclaimer = d.get('price_disclaimer') or ''
    lt = v.get('lease_terms') if v['lease_month'] else None
    lease_rows = ''
    if lt:
        def m_(n): return money(n) if isinstance(n, int) else ''
        pay = (lt.get('payment') or '').replace('+tax', ' + tax')
        if pay and '.' in pay: pay = '$' + '{:,}'.format(int(float(pay.split(' ')[0]))) + pay[pay.index(' '):] if ' ' in pay else '$' + '{:,}'.format(int(float(pay)))
        mileage = f"{'{:,}'.format(lt['miles_per_year'])} miles a year" + (f", ${lt['overage_per_mile']} a mile over" if lt.get('overage_per_mile') else '') if lt.get('miles_per_year') else ''
        lease_rows = rows([
            ('Lease sale price', m_(lt.get('sales_price'))),
            ('Term', f"{lt['term_months']} months" if lt.get('term_months') else ''),
            ('Due at signing', m_(lt.get('due_at_signing'))),
            ('Monthly payment', (pay + ' a month') if pay else ''),
            ('Residual at lease end', m_(lt.get('residual'))),
            ('Purchase option fee', m_(lt.get('purchase_option_fee'))),
            ('Mileage', mileage),
            ('Disposition fee', m_(lt.get('disposition_fee'))),
            ('Credit', 'Tier 1, Rolls-Royce Financial Services' if lt.get('credit') else ''),
            ('Deal number', e(lt.get('deal_number') or '')),
            ('Take delivery by', e(lt.get('offer_ends') or '')),
        ])
    # the dealer's own disclaimer sentence for the lease, verbatim
    raw = v.get('lease_terms_raw') or ''
    lease_fine = raw.split('Disclaimer:', 1)[1].strip() if 'Disclaimer:' in raw else raw
    lease_fine = re.sub(r'\s+', ' ', lease_fine).replace(' ,', ',').replace(' .', '.')
    lease_block = f'''
      <div class="pricing__lease">
        <h3 class="vdp__h" id="lease-terms">Lease terms<span class="pricing__mark" aria-hidden="true">*</span></h3>
        <dl class="offer__rows pricing__rows">
{lease_rows}
        </dl>
        <p class="pricing__fine">{e(lease_fine)}</p>
      </div>''' if lt else ''
    pricing = f'''
    <!-- The disclosure: what the dealer says beside every price, and the
         lease as the dealer states it, on the page rather than behind a
         click. The asterisks by the price and the lease lead here. -->
    <section class="pricing" id="pricing" aria-labelledby="pricing-title" tabindex="-1">
      <h2 class="vdp__h" id="pricing-title">Pricing details</h2>
      <div class="pricing__body">{lease_block}
        <div class="pricing__legal">
          <h3 class="vdp__h" id="price-terms">Disclaimer<span class="pricing__mark" aria-hidden="true">*</span></h3>
          <p class="pricing__text">{e(disclaimer.lstrip('* ').strip())}</p>
        </div>
      </div>
    </section>'''

    others = [o for o in featured if o['stock'] != v['stock']]
    more = sorted(others, key=lambda o: (o['model'] != v['model'], o['condition'] != v['condition']))[:3]
    more_cards = '\n'.join(card(o, p) for o in more)

    spin_block = ''
    mode_block = ''
    if v['spin']:
        spin_block = f'''<div class="spin" hidden>
      <div class="wrap">
        <div class="spin__stage">
          <img class="spin__image" src="{p}{v['spin'][0]}" width="1000" height="667" alt="{e(v['exterior'])} {e(name)}, turning" draggable="false">
          <p class="spin__hint"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" focusable="false"><path d="M3 12a9 4 0 1 0 18 0"/><path d="M21 12a9 4 0 0 0-18 0"/><path d="M18 8l3 4-4 1"/></svg>Drag to rotate</p>
          <div class="spin__loading" hidden><span></span></div>
        </div>
      </div>
    </div>'''
        mode_block = '''<div class="film__mode" role="group" aria-label="View">
        <button class="film__mode-button" type="button" data-mode="photos" aria-pressed="true">Photographs</button>
        <button class="film__mode-button" type="button" data-mode="spin" aria-pressed="false">360° view</button>
      </div>'''
    title = f"{v['title']} | Rolls-Royce Motor Cars Palm Beach"
    desc_meta = f"{v['title']}, {v['exterior']} over {v['interior']}, {'{:,}'.format(v['mileage'])} miles, {label} {money(v['price'])} at Rolls-Royce Motor Cars Palm Beach, West Palm Beach, Florida."
    h = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', head)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc_meta)}">', h)
    h1 = e(name).replace('Rolls-Royce', '<span class="nowrap">Rolls-Royce</span>')

    return f'''<!doctype html>
<html lang="en">
{h}
<body>
{header}

<main id="main" class="vdp" data-ground="dark">
  <div class="wrap">

    <div class="vdp__top">
      <nav class="vdp__crumbs" aria-label="Breadcrumb">
        <a href="../index.html">Home</a><span aria-hidden="true">/</span><a href="../inventory.html">Inventory</a><span aria-hidden="true">/</span><span aria-current="page">{e(name)}</span>
      </nav>
      <!-- Save · Email · Text · Share — Save keeps the car; the other three open the drawer -->
      <ul class="tools" data-stock="{e(v['stock'])}" data-name="{e(name)}">
        <li><button class="tool" type="button" data-tool="save" aria-pressed="false"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" focusable="false"><path d="M10 17s-7-4.4-7-9.2A3.8 3.8 0 0 1 10 6a3.8 3.8 0 0 1 7 1.8C17 12.6 10 17 10 17z"/></svg><span>Save</span></button></li>
        <li><button class="tool" type="button" data-tool="email" data-open="email"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" focusable="false"><rect x="2.5" y="4.5" width="15" height="11"/><path d="M2.5 5l7.5 6 7.5-6"/></svg><span>Email</span></button></li>
        <li><button class="tool" type="button" data-tool="text" data-open="text"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" focusable="false"><path d="M3 4h14v9H8l-4 3v-3H3z"/></svg><span>Text</span></button></li>
        <li><button class="tool" type="button" data-tool="share" data-open="share"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" focusable="false"><path d="M10 12V3M6.5 6.5L10 3l3.5 3.5"/><path d="M4 10v6h12v-6"/></svg><span>Share</span></button></li>
      </ul>
    </div>

    <!-- The name, and the figure beside it. -->
    <header class="vdp__head" data-reveal>
      <div class="vdp__name">
        <p class="vdp__eyebrow">{eyebrow}</p>
        <h1 class="vdp__title">{h1}</h1>
      </div>
      <div class="vdp__figure">
        <p class="card__price vdp__price"><span class="card__price-label">{label}</span> <span class="card__price-value">{money(v['price'])}</span><a class="asterisk" href="#pricing" aria-label="Pricing details">*</a></p>
        {f'<p class="vdp__lease">{lease_text(v)}<a class="asterisk" href="#pricing" aria-label="Lease terms">*</a></p>' if v['lease_month'] else ''}
        <a class="btn btn--ghost vdp__confirm" href="#enquire">Confirm Availability</a>
      </div>
    </header>

  </div>

  <!-- The photographs: a rail of frames, each at its own proportion and one
       height, the first on the measure and the rest running off the right
       edge. It drags, scrolls and snaps; the line beneath says where it is;
       any frame opens full-screen. -->
  <section class="film" aria-label="Photographs" data-photos='{sources}' data-spin='{spin}'>
    <ul class="film__row">
{frames}
    </ul>
    {spin_block}
    <div class="wrap film__foot">
      <div class="film__track" aria-hidden="true"><span class="film__thumb"></span></div>
      {mode_block}
      <p class="film__count"><span data-index>1</span><span class="film__total"> / {len(photos)}</span></p>
      <div class="film__nav">
        <button class="film__arrow film__arrow--prev" type="button" data-dir="-1" aria-label="Previous photograph" disabled><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></button>
        <button class="film__arrow film__arrow--next" type="button" data-dir="1" aria-label="Next photograph"><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></button>
      </div>
    </div>
  </section>

  <div class="wrap">
    <!-- The plate: the four facts a buyer asks first, large. -->
    <dl class="plate">
      <div><dt>Exterior</dt><dd>{e(v['exterior'])}</dd></div>
      <div><dt>Interior</dt><dd>{e(v['interior'])}</dd></div>
      <div><dt>Mileage</dt><dd>{'{:,}'.format(v['mileage'])} <span class="plate__unit">miles</span></dd></div>
      <div><dt>Engine</dt><dd>{e(engine_short)}</dd></div>
    </dl>

    <div class="vdp__body">
      <div class="vdp__main">
        <section class="vdp__section" aria-labelledby="desc-title">
          <h2 class="sr-only" id="desc-title">Description</h2>{description}{options}{provenance}
        </section>
      </div>

      <!-- The offer: the price, what sits around it, the two calls, the record. -->
      <aside class="offer" aria-label="The offer">
        {'<p class="offer__flag">Internet Special</p>' if v['special'] else ''}
        <p class="offer__label">{label}<a class="asterisk" href="#pricing" aria-label="Pricing details">*</a></p>
        <p class="offer__price">{money(v['price'])}</p>
        {f'<p class="offer__lease"><span>Lease<a class="asterisk" href="#pricing" aria-label="Lease terms">*</a></span><span>{lease_row}</span></p>' if lease_row else ''}
        {f'<dl class="offer__rows">{chr(10)}{rows(around)}{chr(10)}        </dl>' if around else ''}
        <div class="offer__actions">
          <a class="btn btn--white" href="#enquire">Request a Quote</a>
          <a class="btn btn--slate" href="tel:+15612038780">Connect with a Specialist</a>
        </div>
        <p class="offer__route"><a class="route" href="#">Get pre-approved for financing<svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></p>
        <p class="offer__route offer__route--quiet"><a class="route" href="#pricing">Pricing details<svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></p>
        <dl class="offer__rows offer__facts">
{rows(facts)}
        </dl>
      </aside>
    </div>

{pricing}

    <!-- Enquire -->
    <section class="vdp__enquire" id="enquire" aria-labelledby="enq-title">
      <div class="vdp__enquire-lede">
        <h2 class="vdp__h" id="enq-title">Enquire</h2>
        <p class="vdp__copy">A specialist will confirm availability and arrange a private viewing at 2801 Okeechobee Boulevard, West Palm Beach — or call <a href="tel:+15612038780">561-203-8780</a>.</p>
        <p class="vdp__copy vdp__trade">Have a motor car to part with? <a class="route" href="#">Value your trade-in<svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></p>
      </div>
      <form class="enquire" onsubmit="return false" aria-labelledby="enq-form-title">
        <p class="enquire__title" id="enq-form-title">Send an enquiry</p>
        <label class="field"><span class="field__label">Name</span><input class="field__input" type="text" name="name" autocomplete="name" placeholder="Your name"></label>
        <label class="field"><span class="field__label">Email</span><input class="field__input" type="email" name="email" autocomplete="email" placeholder="name@example.com"></label>
        <label class="field"><span class="field__label">Telephone</span><input class="field__input" type="tel" name="tel" autocomplete="tel" placeholder="+1"></label>
        <label class="field field--wide"><span class="field__label">Message</span><textarea class="field__input field__area" name="message" rows="3">I am interested in the {e(name)}, stock {e(v['stock'])}.</textarea></label>
        <div class="enquire__send"><button class="btn btn--white" type="submit">Send Enquiry</button></div>
      </form>
    </section>
  </div>

  <!-- More from the collection: the same model first. -->
  <section class="stock stock--more" data-reveal aria-labelledby="more-title">
    <div class="wrap">
      <h2 class="stock__title" id="more-title">More from the collection</h2>
      <div class="stock__rail">
        <ul class="stock__row">
{more_cards}
        </ul>
      </div>
      <div class="actions">
        <a class="btn btn--sky" href="../inventory.html">View All<span class="sr-only"> inventory</span></a>
      </div>
    </div>
  </section>

  <!-- On a small screen the offer follows the page once it has scrolled off. -->
  <div class="vdp__bar" hidden>
    <div class="wrap vdp__bar-wrap">
      <p class="vdp__bar-price"><span>{label}</span> {money(v['price'])}</p>
      <a class="btn btn--white btn--compact" href="#enquire">Enquire</a>
    </div>
  </div>

  <!-- Full-screen photograph -->
  <dialog class="lightbox" aria-label="Photograph">
    <button class="lightbox__close" type="button" aria-label="Close"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" focusable="false"><path d="M2 2l12 12M14 2L2 14"/></svg></button>
    <button class="film__arrow lightbox__arrow lightbox__arrow--prev" type="button" data-dir="-1" aria-label="Previous photograph"><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></button>
    <img class="lightbox__image" src="" alt="">
    <button class="film__arrow lightbox__arrow lightbox__arrow--next" type="button" data-dir="1" aria-label="Next photograph"><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></button>
    <p class="lightbox__count"><span data-index>1</span> / {len(photos)}</p>
  </dialog>
</main>

  <!-- The drawer: Email, Text, Share — slides in from the right. Outside <main>,
       whose stacking context would keep it under the header. -->
  <div class="drawer" id="contact" hidden>
    <div class="drawer__scrim" data-close></div>
    <aside class="drawer__panel" role="dialog" aria-modal="true" aria-labelledby="drawer-title" tabindex="-1">
      <div class="drawer__head">
        <p class="drawer__eyebrow">{e(name)}</p>
        <h2 class="drawer__title" id="drawer-title">Pass it on</h2>
        <button class="drawer__close" type="button" data-close aria-label="Close"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" focusable="false"><path d="M2 2l12 12M14 2L2 14"/></svg></button>
      </div>

      <section class="drawer__group" data-group="email" aria-labelledby="dg-email">
        <h3 class="vdp__h" id="dg-email">Email this motor car</h3>
        <form class="drawer__form" data-form="email">
          <label class="field"><span class="field__label">To</span><input class="field__input" type="email" name="to" required placeholder="name@example.com" autocomplete="email"></label>
          <label class="field"><span class="field__label">Your name</span><input class="field__input" type="text" name="from" placeholder="So they know who sent it" autocomplete="name"></label>
          <label class="field"><span class="field__label">Message</span><textarea class="field__input field__area" name="message" rows="3">I thought you might like this {e(name)} at Rolls-Royce Motor Cars Palm Beach.</textarea></label>
          <button class="btn btn--white" type="submit">Send by email</button>
          <p class="drawer__fine">Opens your mail app with the message and the link ready.</p>
        </form>
      </section>

      <section class="drawer__group" data-group="text" aria-labelledby="dg-text">
        <h3 class="vdp__h" id="dg-text">Text this motor car</h3>
        <form class="drawer__form" data-form="text">
          <label class="field"><span class="field__label">Mobile number</span><input class="field__input" type="tel" name="to" required placeholder="+1 561 000 0000" autocomplete="tel"></label>
          <button class="btn btn--white" type="submit">Send by text</button>
          <p class="drawer__fine">Opens Messages with the link ready — to a friend, or <a data-sms="self" href="sms:">to your own phone</a>.</p>
        </form>
      </section>

      <section class="drawer__group" data-group="share" aria-labelledby="dg-share">
        <h3 class="vdp__h" id="dg-share">Share</h3>
        <ul class="drawer__list">
          <li><a class="drawer__line" data-share="facebook" href="#" target="_blank" rel="noopener"><span>Facebook</span><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></li>
          <li><a class="drawer__line" data-share="x" href="#" target="_blank" rel="noopener"><span>X</span><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></li>
          <li><a class="drawer__line" data-share="whatsapp" href="#" target="_blank" rel="noopener"><span>WhatsApp</span><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></li>
          <li><a class="drawer__line" data-share="telegram" href="#" target="_blank" rel="noopener"><span>Telegram</span><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></li>
          <li><a class="drawer__line" data-share="linkedin" href="#" target="_blank" rel="noopener"><span>LinkedIn</span><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></li>
          <li><a class="drawer__line" data-share="pinterest" href="#" target="_blank" rel="noopener"><span>Pinterest</span><svg viewBox="0 0 16 10" fill="currentColor" aria-hidden="true" focusable="false">{CHEVRON}</svg></a></li>
          <li><button class="drawer__line" type="button" data-share="copy"><span>Copy the link</span><strong data-word>Copy</strong></button></li>
          <li><button class="drawer__line" type="button" data-share="sheet" hidden><span>More</span><strong>Share…</strong></button></li>
        </ul>
      </section>
    </aside>
  </div>

{footer}

<script src="../js/main.js"></script>
<script src="../js/vehicle.js"></script>
</body>
</html>
'''

os.makedirs(ROOT + 'vehicles', exist_ok=True)
for f in os.listdir(ROOT + 'vehicles'):
    if f.endswith('.html'): os.remove(ROOT + 'vehicles/' + f)
for v in V:
    open(ROOT + v['page'], 'w').write(stamp(vehicle_page(v)))
print(len(V), 'vehicle pages in vehicles/')
