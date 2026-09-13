# beehiiv partner-program registration evidence — 2026-09-14

## Duplicate-state check
- Repository search for `beehiiv`: no existing COSHUMA tool or affiliate record before this cycle.
- Company Gmail `support@coshuma.com` search `in:anywhere beehiiv`: no matching received, sent, spam, or trash messages before this cycle.

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
- `affiliate_status`: `application_available_account_required`
- `affiliate_url`: null
- Exact account-specific customer tracking URL: **not issued / not verified**.
- Application submission: **not claimed**. The public apply route is a JavaScript app and requires an authenticated beehiiv account/partner session.
- Customer signups, paid customers, commission and revenue: **unknown / not verified**.
- Browser/application blocker is tracked in GitHub issue #465.

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
Until beehiiv itself issues an account-specific customer tracking link, COSHUMA must use only official non-affiliate beehiiv customer URLs and must not invent referral parameters. Do not claim signup, conversion, commission, or revenue from deployment or link issuance alone.
