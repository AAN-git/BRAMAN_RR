"""Writes css/v4.css: css/v4.src.css (by hand), then, for the chapters marked
data-coast, every rule of the version-3 sheets that draws a Frost hairline,
tint or type (rgba(255, 255, 255, a)) restated in Noir at the same weight —
so a light chapter has no white line left on it. Rules about what stands on
photographs or films (the hero, the films, the flags, the drawer, the bar,
the dock, the footer, Black Badge) are left alone.
Run: python3 tools/coast_v4.py && python3 tools/mirror_v4.py"""
import os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
SHEETS = ['css/main.css', 'css/home-v2.css', 'css/cards.css', 'css/inventory.css', 'css/vehicle.css', 'css/v3.css']
SKIP = re.compile(r'hero|film|spin|lightbox|drawer|flag|header|dock|footer|badge|cullinan|split|news|about|service|tile|poster|toggle|\.cpo|sell__field')
WHITE = re.compile(r'rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*([0-9.]+)\s*\)')

def strip_comments(s): return re.sub(r'/\*.*?\*/', '', s, flags=re.S)

def blocks(css):
    """yield (prelude, body) at the top level; @media bodies are recursed"""
    i, n = 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0: return
        pre = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == '{': depth += 1
            elif css[k] == '}': depth -= 1
            k += 1
        yield pre, css[j + 1:k - 1]
        i = k

def darken(decls):
    out = []
    for d in decls.split(';'):
        if 'rgba' in d and WHITE.search(d) and ':' in d:
            prop = d.split(':', 1)[0].strip()
            if prop.startswith('--'): continue
            val = WHITE.sub(lambda m: f'rgba(0, 0, 0, {min(1, float(m.group(1)) * 1.0):g})', d.split(':', 1)[1])
            # a border shorthand is restated as its colour only, so a rule that
            # set the width to 0 elsewhere keeps winning on the width
            if prop in ('border', 'border-top', 'border-bottom', 'border-left', 'border-right'):
                m = re.search(r'rgba\([^)]*\)', val)
                prop, val = prop + '-color', m.group(0)
            # a tint used as a ground stays a whisper on the light ground
            if prop in ('background', 'background-color'):
                val = WHITE.sub(lambda m: f'rgba(0, 0, 0, {min(0.06, float(m.group(1))):g})', d.split(':', 1)[1])
            out.append(f'{prop}:{val.strip()}')
    return out

def scope(sel):
    sel = sel.strip()
    return f':is([data-coast], [data-coast] *):is({sel})'

def walk(css, media=None):
    rules = []
    for pre, body in blocks(css):
        if pre.startswith('@media'):
            rules += walk(body, pre)
        elif pre.startswith('@'):
            continue
        else:
            if SKIP.search(pre): continue
            ds = darken(body)
            if not ds: continue
            sels = ', '.join(scope(s) for s in pre.split(',') if s.strip())
            rules.append((media, sels + ' { ' + '; '.join(ds) + '; }'))
    return rules

out = [open(ROOT + 'css/v4.src.css', encoding='utf-8').read().split('/* AFTER */', 1)[0].rstrip() + '\n']
count = 0
for sheet in SHEETS:
    if not os.path.exists(ROOT + sheet): continue
    css = strip_comments(open(ROOT + sheet, encoding='utf-8').read())
    rules = walk(css)
    if not rules: continue
    out.append(f'\n/* from {sheet} */\n')
    for media, r in rules:
        out.append(f'{media} {{ {r} }}\n' if media else r + '\n')
        count += 1
# the hand-written exceptions must win over the generated restatements
# the hand-written exceptions must win over the generated restatements
src = open(ROOT + 'css/v4.src.css', encoding='utf-8').read()
tail = src.split('/* AFTER */', 1)[1] if '/* AFTER */' in src else ''
out.append('\n/* exceptions, restated after the generated rules (css/v4.src.css, AFTER) */\n' + tail.strip() + '\n')
open(ROOT + 'css/v4.css', 'w', encoding='utf-8', newline='\n').write(''.join(out))
print('css/v4.css:', count, 'generated rules')
