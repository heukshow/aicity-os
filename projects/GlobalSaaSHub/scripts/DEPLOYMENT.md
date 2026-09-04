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
