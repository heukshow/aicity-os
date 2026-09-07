# ActiveCampaign affiliate route verification — 2026-09-08

## Current evidence

- Tool: `activecampaign`
- COSHUMA page: `https://coshuma.com/tool/activecampaign.html`
- Company mailbox checked: `support@coshuma.com`
- Gmail search for ActiveCampaign in the prior year returned no application, approval, rejection, or outreach messages.
- Official affiliate page: `https://www.activecampaign.com/partners/affiliate`
- Official affiliate help: `https://help.activecampaign.com/hc/en-us/articles/115000065864-Affiliate-program`
- Official application route: ActiveCampaign's current **Apply Now** button opens its PartnerStack application.

## Verified program facts

ActiveCampaign's current official affiliate page states the program is for content creators, influencers and publishers, does not require the applicant to be an ActiveCampaign customer, and issues a unique referral link after approval through a PartnerStack-powered affiliate portal. ActiveCampaign's help center, updated July 30, 2026, states eligible referrals earn a 30% recurring commission for up to 12 months.

## Decision

- `affiliate_url`: `null`
- `affiliate_status`: `browser_required_partnerstack_application`
- `cost`: `0`
- The stale `application_page_unavailable` observation is superseded: a live official application route now exists.
- No prior company-mailbox application evidence was found, so there is no known duplicate application to protect against at this point.
- Do not publish the ActiveCampaign homepage, PartnerStack application URL, PartnerStack dashboard, login URL, or onboarding URL as a customer affiliate/revenue link.
- Do not claim clicks, sign-ups, commissions or revenue until the partner system provides evidence.

## Next action

Use the existing COSHUMA PartnerStack identity if the ActiveCampaign application permits it. Submit only once with factual COSHUMA information. If CAPTCHA, OTP, forced identity verification or a legal consent requiring the user's action appears, leave only that step for the user. After approval, copy and independently verify the exact customer-facing referral URL before changing any COSHUMA revenue CTA to `approved_tracking`.
