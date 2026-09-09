# Typedesk affiliate tracking verification — 2026-09-09

## Verified evidence
- Company mailbox: `support@coshuma.com`.
- Human reply from Hennadiy Hlinskyy (`hennadiy@typedesk.com`), Gmail message `1a083d37fcdad998`.
- Exact customer-facing tracking URL provided by Typedesk: `https://www.typedesk.com?via=sangkwon`.
- The message explicitly identifies this as COSHUMA's unique tracking link and says reports are available in the Rewardful dashboard.
- Follow-up human reply from Hennadiy Hlinskyy, Gmail message `1a0841c6e959ea36`, confirms two conversion-safe implementation details: Typedesk currently provides no coupon codes, and the affiliate attribution can be used on any Typedesk page.
- Therefore COSHUMA may use a buyer-intent deep link such as `https://www.typedesk.com/pricing?via=sangkwon` while preserving the vendor-confirmed `via=sangkwon` attribution parameter.

## Safe state
- Affiliate status: approved/enrolled with exact tracking URL verified by vendor email.
- Customer-facing revenue URL: `https://www.typedesk.com?via=sangkwon`.
- Vendor-confirmed buyer-intent deep link: `https://www.typedesk.com/pricing?via=sangkwon`.
- No coupon or discount claim should be published because Typedesk explicitly said it does not provide coupon codes for now.
- Do not use Rewardful login/dashboard/onboarding URLs as revenue links.
- Do not infer clicks, signups, commissions, or revenue from link issuance or deep-link permission alone.
