"""Shared official identity for COSHUMA-owned advertisements only."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = '/brand/coshuma-lockup-light.svg'

def identity_html():
    if not (ROOT / 'public' / LOGO_PATH.lstrip('/')).is_file():
        raise ValueError('Official COSHUMA logo is missing')
    return ('<div class="house-ad-identity" aria-label="Advertiser: COSHUMA">'
            '<img data-advertiser-logo src="' + LOGO_PATH + '" width="520" height="96" '
            'alt="COSHUMA" decoding="async" /></div>')
