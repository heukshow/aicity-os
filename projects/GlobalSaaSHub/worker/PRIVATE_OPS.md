# Private operations dashboard

Owner entry: `https://globalsaashub-payments.qmfforfhem.workers.dev/ops/traffic-revenue.html`.

`ops-dashboard-view.js` updates the private HTML rendering against the real snapshot schema. Connection badges, opportunity rows and search-query lists reflect received data rather than static disconnected placeholders. `/ops/partnerstack-summary.json` reuses the existing PartnerStack secret after owner authentication, exposing only connection status and first-page record counts (up to 250 per endpoint), not credentials or customer records. A successful PartnerStack query is partial network coverage, not a verified all-network revenue total.

The `/ops` route authenticates `support@coshuma.com` against the `OPS_PASSWORD_SHA256` Worker secret. The existing admin credentials and payment routes are independent. Neither passwords nor secret values belong in Git. Login forms use a signed ten-minute CSRF cookie plus a matching hidden nonce; this supports the existing Work browser without trusting a mismatched Origin. Login attempts are limited to ten per client IP per ten-minute bucket; client IPs are stored only as hashes. Sessions expire on the server after eight hours and use Secure, HttpOnly, SameSite=Strict cookies. Basic authentication and unverified Access identity headers cannot bypass this route.

HTML and internal JSON live in the existing ORDERS D1 binding's `private_ops_documents` table, outside both GitHub Pages and repository source. Every read requires authentication, including HEAD and direct JSON requests. Responses use no-store/private. Apply `migrations/0002_private_ops.sql` before first deployment; importing documents requires existing authorized Cloudflare administration access. Do not commit document contents or upload them as public Actions artifacts.

The analytics workflow generates into runner temporary storage and uploads through `/internal/analytics-snapshot`. The Worker verifies the GitHub OIDC RS256 signature, issuer, dedicated audience, repository and owner IDs, exact main-branch workflow, event type and time limits before accepting a write. This identity grants write-only snapshot ingestion, never dashboard reads. No new long-lived GitHub secret is required. Failed generation preserves the previous private snapshot. HTML changes must be uploaded separately through authorized Cloudflare D1 administration.

Vite excludes all `ops/` files and `admin-affiliate-audit.json` from production output, even if an old process regenerates them. The affiliate audit generator writes only to ignored `.private-ops/`. Public `/ops` source files must remain absent. Both main and gh-pages need removal during migration; removing only a custom-domain link leaves raw GitHub and Pages origins exposed.

Cloudflare Access was not enabled: the existing OAuth identity has Workers/D1 permission but Access API access returns 403. The existing free Worker and D1 provide the actual server authentication boundary. No DNS, MX, plan or payment changes are needed.

Previously published Git history, cached copies, and third-party copies are outside this forward-looking access boundary. Do not claim historical data has been recalled. History rewriting is a separate destructive operation.

Validation: `node --test test/*.test.js` in worker; `node --test scripts/tests/private-ops-build.test.mjs` and `npx vite build` in GlobalSaaSHub. Test anonymous HTML/JSON, forged/expired cookies, wrong account, allowed account, rejected publishers, exact OIDC claims, and absence of public output. Recheck `/health` without creating payment transactions.
