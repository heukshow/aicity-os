#!/usr/bin/env python3
from pathlib import Path
import sys

MARKER = 'data-coshuma-origin-guard="1"'
REQUIRED_TERMS = [
    'mirror or systematically republish',
    'impersonate COSHUMA',
    'brand-usage.html',
]

def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'dist')
    if not root.is_dir():
        raise SystemExit(f'brand protection target does not exist: {root}')

    project_root = Path(__file__).resolve().parents[2]
    license_path = project_root / 'LICENSE-COSHUMA.txt'
    if not license_path.exists():
        raise SystemExit('LICENSE-COSHUMA.txt is missing')
    license_text = license_path.read_text(encoding='utf-8')
    if 'Copyright © 2026 COSHUMA. All rights reserved.' not in license_text:
        raise SystemExit('COSHUMA proprietary notice is incomplete')

    brand_usage = root / 'brand-usage.html'
    terms = root / 'terms.html'
    if not brand_usage.exists():
        raise SystemExit('brand-usage.html is missing from the public bundle')
    if not terms.exists():
        raise SystemExit('terms.html is missing from the public bundle')

    terms_text = terms.read_text(encoding='utf-8')
    for phrase in REQUIRED_TERMS:
        if phrase not in terms_text:
            raise SystemExit(f'terms.html missing protection phrase: {phrase}')

    pages = sorted(root.rglob('*.html'))
    if not pages:
        raise SystemExit('no HTML pages found in public bundle')

    missing = []
    duplicates = []
    for page in pages:
        count = page.read_text(encoding='utf-8').count(MARKER)
        if count == 0:
            missing.append(page.relative_to(root).as_posix())
        elif count != 1:
            duplicates.append(page.relative_to(root).as_posix())

    if missing:
        raise SystemExit('origin guard missing from: ' + ', '.join(missing[:20]))
    if duplicates:
        raise SystemExit('duplicate origin guard in: ' + ', '.join(duplicates[:20]))

    print(f'COSHUMA BRAND PROTECTION TEST: PASS ({len(pages)} HTML pages protected)')

if __name__ == '__main__':
    main()
