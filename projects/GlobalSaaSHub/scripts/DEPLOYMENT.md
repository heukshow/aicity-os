# COSHUMA production deployment

`coshuma.com` is served from the repository's `gh-pages` branch.

The production branch must contain the **complete output of `npm run build`**, not a hand-edited `index.html` paired with an older hashed JS/CSS bundle.

Source of truth:
- UI source: `projects/GlobalSaaSHub/src/`
- Static/SEO source: `projects/GlobalSaaSHub/public/` and `projects/GlobalSaaSHub/index.html`
- Production artifact: `projects/GlobalSaaSHub/dist/`
- Production branch: `gh-pages`
- Custom domain: `projects/GlobalSaaSHub/public/CNAME` = `coshuma.com`

`.github/workflows/coshuma-site-deploy.yml` rebuilds and publishes the complete Vite `dist` when site source changes. Do not manually sync only individual `gh-pages` HTML files after React/UI changes; doing so can leave `index.html` pointing at a stale hashed application bundle.


## Public-copy protection invariant

The public production artifact is intentionally crawlable for buyer-search discovery, but every built HTML page must pass the COSHUMA brand-protection step before publication.

- `scripts/apply_brand_protection.py dist` injects a canonical-origin and anti-embedding guard into every built HTML page.
- `scripts/tests/test_brand_protection.py dist` fails the build if any HTML page is unprotected or if the public brand/terms notices are missing.
- The guard allows the canonical COSHUMA hosts, the owner's GitHub Pages host, and local/private-network development hosts. A copied bundle served from an unrelated public host is replaced with a link back to the canonical COSHUMA URL.
- This is a deterrent and origin signal, not a claim that browser-delivered HTML can be made impossible to copy.

The source repository must **not** be switched from public to private until the replacement publishing path is proven to keep `coshuma.com` online. A visibility change is a separate infrastructure migration and requires a successful production health check before and after cutover.
