# beehiiv partner-program registration evidence — 2026-09-14

## Duplicate-state check
- Repository search for `beehiiv`: no existing COSHUMA tool or affiliate record before this cycle.
- Company Gmail `support@coshuma.com` search `in:anywhere beehiiv`: no matching received, sent, spam, or trash messages before this cycle.
- After the signup attempt, Gmail received a beehiiv email-verification message addressed to `support@coshuma.com`. This proves the signup flow reached email verification, but does **not** prove account creation, partner-program enrollment, tracking-link issuance, approval, referral, paid conversion, commission, or revenue.

## Official product evidence
- Pricing: https://www.beehiiv.com/pricing
- Current Launch plan: $0/month, up to 2,500 subscribers, unlimited email sends.
- beehiiv states the Launch plan is free forever and no credit card is required to get started.
- Paid Scale/Max pricing varies by subscriber tier and billing cadence; COSHUMA does not hard-code a single paid-plan price as universally applicable.

## Official partner evidence
- Partner program: https://www.beehiiv.com/partners
- Apply route: https://app.beehiiv.com/partner_program
- Official page states partners can earn up to 60% of referred paying-customer revenue for one year.
- Official page states a beehiiv account is created/used to unlock the partner dashboard and custom tracking link.
- Current public partner page states referred users receive a 14-day trial plus 20% off their first 3 months when they come through an eligible partner route; COSHUMA must not advertise that benefit on a generic non-affiliate CTA before its own issued partner route is verified.
- Official page states partner payouts are made through PayPal.
- Self-referrals and branded Google/Bing search ads are prohibited by the public partner FAQ.

## COSHUMA state
- `affiliate_status`: `browser_required_legal_program_consent`
- Existing signup/account path: **confirmed by support Gmail messages `1a09ba80f91097c0` and `1a09bd155da3084f`; do not create a duplicate account**.
- Partner enrollment: **not submitted / not verified**. The current join form requires reviewing and accepting the Partner Program Terms.
- `affiliate_url`: null
- Exact account-specific customer tracking URL: **not issued / not verified**.
- Application submission: **not claimed**. No authenticated evidence yet shows that the partner enrollment itself was submitted.
- Customer signups, paid customers, commission and revenue: **unknown / not verified**.
- Legal-consent blocker and exact-link recovery remain tracked in GitHub issue #465.

## 2026-10-11 evidence reconciliation
- Official beehiiv help, updated 2026-05-05: https://www.beehiiv.com/support/article/13091611134103
- It states that active-plan users, including free-trial users, can enter the Partner Dashboard; first-time enrollment presents a join form that requires reviewing and accepting the Partner Program Terms.
- A private custom partner link becomes available only after joining. No COSHUMA-specific beehiiv customer link is currently verified.
- Personal Gmail message `1a0268a7b8777e9e` proves that a Dub Partner Network marketplace application was submitted on 2026-08-21; message `1a0515e930b9704b` proves that marketplace application was rejected on 2026-08-30.
- Dub's rejection explicitly says it does not affect existing direct program partnerships or payouts. It therefore neither approves nor rejects beehiiv enrollment and must not be used as beehiiv approval, link, conversion, commission, payout or revenue evidence.
- Safe next action: reuse the existing beehiiv account, stop at the Partner Program Terms acceptance gate until legal consent is explicitly authorized, then verify the issued customer-facing link after enrollment.

## Live deployment verification
Verified after the merged deployment on 2026-09-14 KST from an external client:
- `https://coshuma.com/tool/beehiiv.html` → HTTP 200; canonical present; SoftwareApplication JSON-LD present; no `noindex`; link to beehiiv-vs-Kit comparison present.
- `https://coshuma.com/best/beehiiv-free-plan-pricing.html` → HTTP 200; canonical present; WebPage/FAQ structured data present; no `noindex`; tool-page internal link present.
- `https://coshuma.com/compare/beehiiv-vs-kit.html` → HTTP 200; canonical present; structured data present; no `noindex`; beehiiv tool-page internal link present.
- `https://coshuma.com/category/sales-crm.html` → HTTP 200 and links to `/tool/beehiiv.html` through the email/outreach category grouping.
- `https://coshuma.com/best/index.html` → HTTP 200 and links to `/best/beehiiv-free-plan-pricing.html`.
- `https://coshuma.com/tool/kit.html` → HTTP 200 and links to `/compare/beehiiv-vs-kit.html`.
- `https://coshuma.com/sitemap.xml` → HTTP 200 and includes all three beehiiv URLs.
- `https://coshuma.com/llms.txt` → HTTP 200 and includes the beehiiv tool/best/compare routes.
- `https://coshuma.com/robots.txt` → HTTP 200; `Allow: /`; sitemap declared; no beehiiv path block.

## Publishing guard
Until beehiiv itself issues an account-specific customer tracking link, COSHUMA must use only official non-affiliate beehiiv customer URLs and must not invent referral parameters. Do not claim signup, conversion, commission, or revenue from deployment, an email-verification message, or link issuance alone.
