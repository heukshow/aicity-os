#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARKER = 'data-coshuma-origin-guard="1"'

PROTECTION_BLOCK = r'''<meta name="copyright" content="© 2026 COSHUMA. All rights reserved.">
<meta name="author" content="COSHUMA">
<script data-coshuma-origin-guard="1">
(function () {
  var host = (window.location.hostname || '').toLowerCase();
  var canonicalHosts = new Set(['coshuma.com', 'www.coshuma.com', 'heukshow.github.io']);
  var localHost =
    !host ||
    host === 'localhost' ||
    host === '127.0.0.1' ||
    host === '[::1]' ||
    /^10\./.test(host) ||
    /^192\.168\./.test(host) ||
    /^172\.(1[6-9]|2\d|3[01])\./.test(host);

  var webProtocol = window.location.protocol === 'http:' || window.location.protocol === 'https:';
  var foreignHost = webProtocol && !canonicalHosts.has(host) && !localHost;
  var framed = window.top !== window.self;
  if (!foreignHost && !framed) return;

  var canonicalUrl = 'https://coshuma.com' + window.location.pathname + window.location.search + window.location.hash;

  function showCanonicalNotice() {
    document.documentElement.innerHTML =
      '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
      '<title>COSHUMA — Canonical Site</title></head>' +
      '<body style="margin:0;background:#07080c;color:#e2e8f0;font:16px/1.6 system-ui,sans-serif;display:grid;min-height:100vh;place-items:center">' +
      '<main style="max-width:680px;padding:32px"><h1 style="color:white">COSHUMA</h1>' +
      '<p id="coshuma-origin-message"></p><p><a id="coshuma-canonical-link" target="_top" rel="noopener" style="color:#93c5fd">Open the official COSHUMA page</a></p>' +
      '</main></body>';
    var message = document.getElementById('coshuma-origin-message');
    var link = document.getElementById('coshuma-canonical-link');
    if (message) {
      message.textContent = foreignHost
        ? 'This copy is not being served from COSHUMA\'s canonical public domain.'
        : 'COSHUMA pages are not intended to be embedded inside another site.';
    }
    if (link) link.href = canonicalUrl;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showCanonicalNotice, { once: true });
  } else {
    showCanonicalNotice();
  }

  if (framed && !foreignHost) {
    try { window.top.location.replace(canonicalUrl); } catch (_) {}
  }
})();
</script>'''

def protect_html(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    expected_google_verification = f'google-site-verification: {path.name}'
    if path.name.startswith('google') and path.name.endswith('.html') and text.strip() == expected_google_verification:
        return False
    if text.count(MARKER) > 1:
        raise SystemExit(f'{path}: duplicate COSHUMA origin guard')
    if MARKER in text:
        return False
    if not re.search(r'</head\s*>', text, flags=re.I):
        raise SystemExit(f'{path}: missing </head> for origin guard injection')
    updated = re.sub(r'</head\s*>', lambda _: PROTECTION_BLOCK + '\n</head>', text, count=1, flags=re.I)
    path.write_text(updated, encoding='utf-8')
    return True

def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'dist')
    if not root.is_dir():
        raise SystemExit(f'brand protection target does not exist: {root}')
    pages = sorted(root.rglob('*.html'))
    if not pages:
        raise SystemExit(f'no HTML pages found under {root}')
    changed = sum(1 for page in pages if protect_html(page))
    print(f'COSHUMA BRAND PROTECTION: PASS ({len(pages)} HTML pages checked, {changed} updated)')

if __name__ == '__main__':
    main()
