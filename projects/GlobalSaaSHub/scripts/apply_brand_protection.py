#!/usr/bin/env python3
from pathlib import Path
import html
import re
import sys

MARKER = 'data-coshuma-origin-guard="1"'

# Search Console still reports these former canonical paths as indexed. GitHub
# Pages cannot emit per-path HTTP redirects, so publish small 200 responses that
# immediately hand visitors and crawlers to the current canonical pages. Keep
# aliases out of sitemaps and mark them noindex to avoid duplicate results.
LEGACY_SEARCH_ALIASES = {
    "tool/jasper-ai.html": "tool/jasper.html",
    "tool/make.html": "tool/make-com.html",
    "tool/synthflow.html": "tool/synthflow-ai.html",
    "compare/notion-ai-vs-boldsign.html": "compare/boldsign-vs-notion-ai.html",
}

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
    if (!document.body) return;
    document.title = 'COSHUMA — Canonical Site';

    while (document.body.firstChild) {
      document.body.removeChild(document.body.firstChild);
    }
    document.body.setAttribute(
      'style',
      'margin:0;background:#07080c;color:#e2e8f0;font:16px/1.6 system-ui,sans-serif;display:grid;min-height:100vh;place-items:center'
    );

    var main = document.createElement('main');
    main.setAttribute('style', 'max-width:680px;padding:32px');

    var heading = document.createElement('h1');
    heading.setAttribute('style', 'color:white');
    heading.textContent = 'COSHUMA';

    var message = document.createElement('p');
    message.textContent = foreignHost
      ? 'This copy is not being served from COSHUMA\'s canonical public domain.'
      : 'COSHUMA pages are not intended to be embedded inside another site.';

    var linkRow = document.createElement('p');
    var link = document.createElement('a');
    link.href = canonicalUrl;
    link.target = '_top';
    link.rel = 'noopener';
    link.setAttribute('style', 'color:#93c5fd');
    link.textContent = 'Open the official COSHUMA page';

    linkRow.appendChild(link);
    main.appendChild(heading);
    main.appendChild(message);
    main.appendChild(linkRow);
    document.body.appendChild(main);
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


def write_legacy_search_aliases(root: Path) -> int:
    written = 0
    for legacy_path, canonical_path in LEGACY_SEARCH_ALIASES.items():
        target = root / canonical_path
        if not target.is_file():
            raise SystemExit(f'legacy alias target does not exist: {canonical_path}')

        canonical_url = f'https://coshuma.com/{canonical_path}'
        canonical_url_attr = html.escape(canonical_url, quote=True)
        alias = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="noindex,follow" />
    <meta http-equiv="refresh" content="0;url={canonical_url_attr}" />
    <link rel="canonical" href="{canonical_url_attr}" />
    <title>Page moved | COSHUMA</title>
    <script>window.location.replace({canonical_url!r} + window.location.search + window.location.hash);</script>
  </head>
  <body>
    <main>
      <h1>This COSHUMA page has moved</h1>
      <p><a href="{canonical_url_attr}">Continue to the current page</a>.</p>
    </main>
  </body>
</html>
'''
        destination = root / legacy_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(alias, encoding='utf-8')
        written += 1
    return written


def protect_html(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    expected_google_verification = f'google-site-verification: {path.name}'
    if path.name.startswith('google') and path.name.endswith('.html') and text.strip() == expected_google_verification:
        return False
    expected_naver_verification = f'naver-site-verification: {path.name}'
    if path.name.startswith('naver') and path.name.endswith('.html') and text.strip() == expected_naver_verification:
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
    aliases_written = write_legacy_search_aliases(root)
    pages = sorted(root.rglob('*.html'))
    if not pages:
        raise SystemExit(f'no HTML pages found under {root}')
    changed = sum(1 for page in pages if protect_html(page))
    print(
        f'COSHUMA BRAND PROTECTION: PASS '
        f'({len(pages)} HTML pages checked, {changed} updated, {aliases_written} legacy aliases written)'
    )


if __name__ == '__main__':
    main()
