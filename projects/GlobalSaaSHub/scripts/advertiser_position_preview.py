"""Read-only house-ad previews for the advertiser page, from existing manifests.

A preview is not an editorial page, a paid advertisement or a booking control.
"""
from html import escape
from pathlib import Path
import json
from house_ad_identity import identity_html


def preview_sections(root: Path, data: dict) -> str:
    primary = json.loads((root / 'data/coshuma-promotions.json').read_text(encoding='utf-8'))['promotions']
    assets = {c['id']: c for c in data['creatives']}
    slots = []
    for n, c in enumerate(primary, 1):
        slots.append((c['slot'], f'F{n}', c['page'], 'coshuma-promotion', 'Fixed', [c]))
    codes = {'buyer-hub-fixed':'F4','comparison-hub-fixed':'F5','tool-rotation':'R1','guide-rotation':'R2','compare-rotation':'R3'}
    for row in sorted(data['slots'], key=lambda r: codes[r['id']]):
        slots.append((row['id'], codes[row['id']], row['page'], row['id'], row['mode'].title(), [assets[k] for k in row['creative_ids']]))
    output = []
    for sid, code, page, anchor, mode, creatives in slots:
        slides = []
        for i, c in enumerate(creatives):
            e = lambda k: escape(str(c[k]), quote=True)
            slides.append(f'''<article class="ad-context-creative" data-preview-slide{'' if i == 0 else ' hidden'}>
<div class="ad-context-label">Advertisement &middot; COSHUMA &middot; Display preview</div>{identity_html()}
<div class="ad-context-layout"><img class="ad-context-image" src="{e('image')}?v=logo-20261006" width="{e('width')}" height="{e('height')}" alt="{e('alt')}" loading="lazy" decoding="async"/><div><h3>{e('title')}</h3><p>{e('description')}</p><span class="ad-context-cta">{e('button')}</span></div></div></article>''')
        controls = ''
        if len(creatives) > 1:
            controls = f'''<div class="ad-context-controls" data-preview-controls hidden><button type="button" data-preview-prev>Previous example</button><span data-preview-count aria-live="polite">1 / {len(creatives)}</span><button type="button" data-preview-next>Next example</button></div><p class="fine">Preview controls are manual. On-page rotation uses up to three creatives, one at a time, with an eight-second interval when active.</p>'''
        output.append(f'''<details id="ad-preview-{sid}" class="ad-context-preview" data-position-preview="{sid}">
<summary>{code} &middot; {mode} &middot; Preview advertisement</summary>
<div class="ad-context-body"><p class="ad-context-disclosure"><strong>Example advertiser: COSHUMA.</strong> The product named in the position list is the topic of the surrounding article, not the advertiser. This preview uses COSHUMA's existing house-ad assets; it is not a client campaign or a screenshot.</p>
<div data-preview-slides>{''.join(slides)}</div>{controls}
<p class="fine">The product button above is shown for layout only. It does not open a product site or place an order.</p>
<a class="ad-context-page" data-live-example data-context-link="{sid}" href="{page}#{anchor}" target="_blank" rel="noopener noreferrer">View the position within the full article &rarr;</a>
<p class="fine">Opens a separate tab. The article may contain product comparisons, recommendations and affiliate links. Those are separate from this COSHUMA advertisement.</p></div></details>''')
    return '<div class="ad-context-previews" aria-label="Advertisement previews without product recommendations">'+''.join(output)+'</div>'


def position_text(row: dict) -> str:
    return row['position'].replace('Pipedrive / HighLevel comparison', 'product-comparison section')
