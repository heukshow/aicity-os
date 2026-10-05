"""Publish approved COSHUMA house promotions, without touching paid-ad truth.

The three exact source pages are the only permitted surfaces. The house card
follows the existing paid container at the same boundary. CSS and the runtime
hide it whenever the independently verified paid container is visible.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import argparse
import json
import re
import struct
from house_ad_identity import identity_html

ROOT = Path(__file__).resolve().parents[1]
PAIRS = {
    '/tool/pipedrive.html': ('tool-primary', 'square', 600, 600),
    '/best/claap-sales-follow-up-ai.html': ('buyer-intent-top', 'landscape', 1200, 675),
    '/compare/semrush-vs-frase.html': ('compare-decision-premium', 'wide', 1200, 400),
}
START = '<!-- COSHUMA_PROMOTION_START -->'
END = '<!-- COSHUMA_PROMOTION_END -->'
BLOCK = re.compile(r'\s*<!-- COSHUMA_PROMOTION_START -->.*?<!-- COSHUMA_PROMOTION_END -->', re.S)
CSS = '<link rel="stylesheet" href="/coshuma-promotions.css?v=logo-20261006" />'
JS = '<script defer src="/coshuma-promotions.js"></script>'

class SectionParser(HTMLParser):
    def __init__(self, text, slot):
        super().__init__(convert_charrefs=True)
        self.text, self.slot = text, slot
        self.depth = 0
        self.active = None
        self.boundaries = []
        self.lines = [0]
        for match in re.finditer('\n', text): self.lines.append(match.end())
    def absolute_offset(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col
    def handle_starttag(self, tag, attrs):
        if tag != 'section': return
        self.depth += 1
        if dict(attrs).get('data-sponsored-slot') == self.slot:
            if self.active is not None: raise ValueError('Nested paid slot')
            self.active = self.depth
    def handle_endtag(self, tag):
        if tag != 'section': return
        if self.active == self.depth:
            self.boundaries.append(self.absolute_offset() + len('</section>'))
            self.active = None
        self.depth -= 1

def image_size(path):
    data = path.read_bytes()
    if data[:8] == b'\x89PNG\r\n\x1a\n': return struct.unpack('>II', data[16:24])
    if data[:4] != b'RIFF' or data[8:12] != b'WEBP': raise ValueError('Unsupported image signature')
    kind = data[12:16]
    if kind == b'VP8 ':
        if data[23:26] != b'\x9d\x01\x2a': raise ValueError('Malformed WebP')
        w, h = struct.unpack('<HH', data[26:30])
        return w & 0x3fff, h & 0x3fff
    if kind == b'VP8L':
        if data[20] != 47: raise ValueError('Malformed WebP')
        n = int.from_bytes(data[21:25], 'little')
        return (n & 0x3fff) + 1, ((n >> 14) & 0x3fff) + 1
    if kind == b'VP8X':
        if data[20] & 2: raise ValueError('Animated images are not allowed')
        return int.from_bytes(data[24:27], 'little') + 1, int.from_bytes(data[27:30], 'little') + 1
    raise ValueError('Unrecognized WebP header')

def load_manifest():
    data = json.loads((ROOT / 'data/coshuma-promotions.json').read_text(encoding='utf-8'))
    rows = data.get('promotions', [])
    if data.get('schema_version') != 1 or not isinstance(data.get('enabled'), bool): raise ValueError('Invalid configuration')
    if len(rows) != 3 or {r.get('page') for r in rows} != set(PAIRS): raise ValueError('Exact three pages required')
    for row in rows:
        expected = PAIRS[row['page']]
        if (row['slot'], row['format'], row['width'], row['height']) != expected: raise ValueError('Unapproved format')
        for key, minimum, maximum in [('title', 5, 80), ('description', 20, 240), ('button', 2, 30), ('alt', 10, 160)]:
            v = row[key]
            if not isinstance(v, str) or not minimum <= len(v) <= maximum or any(c in v for c in '<>\n\r'): raise ValueError('Invalid plain-text copy')
        if not re.fullmatch(r'coshuma-[a-z0-9-]+', row['id']): raise ValueError('Invalid house ID')
        if row['destination'] not in ['/best/index.html', '/compare/', '/best/claap-sales-follow-up-ai.html#claap-3-call-checklist']: raise ValueError('Unapproved destination')
        if not re.fullmatch(r'/promotions/coshuma-(tool|guide|comparison)\.(webp|png)', row['image']): raise ValueError('Unapproved image')
        file = ROOT / 'public' / row['image'].lstrip('/')
        if file.stat().st_size > row['max_bytes'] or image_size(file) != (row['width'], row['height']): raise ValueError('Image dimensions or file size do not match')
    return data

def card(row):
    e = lambda k: escape(str(row[k]), quote=True)
    return f'''\n{START}
<aside id="coshuma-promotion" class="coshuma-promotion coshuma-promotion--{e('format')}" data-coshuma-promotion="{e('id')}" data-promotion-page="{e('page')}" data-promotion-slot="{e('slot')}" aria-label="COSHUMA self-promotion">
  <div class="coshuma-promotion__label">Advertisement <span aria-hidden="true">&middot;</span> COSHUMA</div>
  {identity_html()}
  <div class="coshuma-promotion__layout">
    <img class="coshuma-promotion__image" src="{e('image')}?v=logo-20261006" width="{e('width')}" height="{e('height')}" alt="{e('alt')}" loading="lazy" decoding="async" />
    <div class="coshuma-promotion__copy">
      <h2>{e('title')}</h2>
      <p>{e('description')}</p>
      <a class="coshuma-promotion__button" data-promotion-link href="{e('destination')}">{e('button')}</a>
    </div>
  </div>
  <div class="coshuma-promotion__advertiser"><span>Build software? Your product could be here.</span><a data-advertiser-interest href="/advertise.html?placement={e('slot')}#inquire">Explore this placement &rarr;</a></div>
</aside>
{END}'''

def prepare(text, row, enabled=True):
    clean = BLOCK.sub('', text)
    for tag in (CSS, JS): clean = clean.replace(tag, '')
    clean=clean.replace('<link rel="stylesheet" href="/coshuma-promotions.css" />','')
    if not enabled: return clean
    parser = SectionParser(clean, row['slot']); parser.feed(clean)
    if len(parser.boundaries) != 1: raise ValueError('Expected one existing paid slot: ' + row['page'])
    at = parser.boundaries[0]
    if row['next_heading'] not in clean[at:at+2500]: raise ValueError('Position context changed')
    updated = clean[:at] + card(row) + clean[at:]
    if updated.count('</head>') != 1 or updated.count('</body>') != 1: raise ValueError('Malformed page')
    updated = updated.replace('</head>', CSS + '</head>', 1)
    return updated.replace('</body>', JS + '</body>', 1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    config = load_manifest()
    folder = args.verify or ROOT / 'public'
    changed = 0
    for row in config['promotions']:
        file = folder / row['page'].lstrip('/')
        source = file.read_text(encoding='utf-8')
        if args.verify:
            # Final output may be minified; verify concrete content instead of raw formatting.
            if config['enabled']:
                for expected in ['data-coshuma-promotion="' + row['id'] + '"', row['image'], 'coshuma-promotions.css', 'coshuma-promotions.js', 'COSHUMA self-promotion', 'data-advertiser-logo']:
                    if expected not in source: raise ValueError(f'{file}: lost {expected}')
        else:
            updated = prepare(source, row, config['enabled'])
            if updated != source:
                file.write_text(updated, encoding='utf-8'); changed += 1
    print(f'COSHUMA promotions: 3 exact pages verified; changed={changed}. No paid records or payment state changed.')

if __name__ == '__main__': main()
