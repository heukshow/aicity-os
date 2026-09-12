# COSHUMA Google analytics live-connection evidence — 2026-09-12

## Verified execution

- GitHub Actions workflow: `COSHUMA Analytics Snapshot`
- Run number: `35`
- Run ID: `34673576871`
- Head SHA: `c1672f642cdd91f1a306187784c01afbcb032af4`
- Result: `success`
- Collection timestamp: 2026-09-12T04:39:31Z–2026-09-12T04:39:32Z
- Job log emitted: `dashboard snapshot written: live_google_connected`
- Job log then emitted: `Validated analytics snapshot stored behind owner authentication.`

## What `live_google_connected` proves

`projects/GlobalSaaSHub/scripts/generate_live_dashboard_data.mjs` only writes `status: "live_google_connected"` after it obtains a Google OAuth access token and completes the required Google Analytics Data API and Search Console API requests used for the aggregate KPI ranges, traffic sources/pages, affiliate-click reports, search totals, search queries, and search pages. The resulting connection fields are set to GA4 connected and Search Console connected. Optional time-series requests have their own separate status checks and do not authorize inventing missing rows.

Therefore this run is evidence that COSHUMA's core GA4 and Search Console read path was live again at the execution time. It does **not** prove any particular click count, signup, commission, payout, or revenue amount.

## Revenue-truth treatment

- GA4 connection: verified live for this run.
- Search Console connection: verified live for this run.
- Affiliate click counts: do not copy or estimate from this evidence file; use the owner-authenticated private snapshot when an exact number is needed.
- Partner revenue: still requires partner-side or payment-side evidence. Do not infer revenue from GA4 events or search traffic.
- No secrets, private snapshot payload, service-account credentials, or raw owner-only metrics are recorded here.
