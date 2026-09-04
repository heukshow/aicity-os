from pathlib import Path
import re

project = Path(__file__).resolve().parents[1]
dist = project / 'dist'
index = dist / 'index.html'

if not index.exists():
    raise SystemExit('dist/index.html missing')

html = index.read_text(encoding='utf-8')
if 'COSHUMA' not in html:
    raise SystemExit('COSHUMA brand marker missing from dist/index.html')
if 'GlobalSaaSHub - Premier AI' in html:
    raise SystemExit('stale GlobalSaaSHub fallback detected')

asset_refs = re.findall(r'(?:src|href)="(/assets/[^"]+)"', html)
if not asset_refs:
    raise SystemExit('No hashed Vite assets referenced by dist/index.html')

for ref in asset_refs:
    if not (dist / ref.lstrip('/')).exists():
        raise SystemExit(f'Missing referenced asset: {ref}')

cname = dist / 'CNAME'
if not cname.exists() or cname.read_text(encoding='utf-8').strip() != 'coshuma.com':
    raise SystemExit('dist/CNAME missing or incorrect')

print('OK: COSHUMA dist bundle is internally consistent and targets coshuma.com')
