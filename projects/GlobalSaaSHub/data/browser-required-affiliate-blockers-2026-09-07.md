# Browser/user-verification affiliate blockers — 2026-09-07

## Questmate
- Gmail message `1a07a9d7005f84a1` confirms COSHUMA has been welcomed to Questmate's Rewardful partner programme.
- Current blocker: email confirmation must be completed before the unique customer tracking link can be viewed in the Rewardful portal.
- State: `email_confirmation_required`; approval/link activation is not yet verified.
- Do not publish the Rewardful login URL or any confirmation token as a customer affiliate URL.

## AiAssistWorks
- Gmail message `1a07a9ada65fcb7e` is an affiliate-program login message containing a one-time password / login-verification link.
- Current blocker: OTP/login verification requires user intervention under the automation guardrails.
- State: `otp_required`; customer tracking URL remains unverified.
- Do not store or publish the OTP/token in repository data.

## JobHire.AI
- Human support reply in Gmail message `1a07a9f8bde2ff29` confirms the affiliate programme is free to join and that enrollment must be completed through the official `Join Now` route at https://jobhire.ai/affiliate-program.
- The agent explicitly said they cannot activate the account or assign a tracking link manually.
- Current blocker: browser form completion through the official Join Now route.
- State: `browser_required_application`; customer tracking URL remains unverified.

## Sendcloud
- Current official affiliate page: https://www.sendcloud.com/partnerships/affiliate-program/
- The vendor states the programme is free to join and routes applications through PartnerStack.
- New authoritative Gmail evidence: PartnerStack message `1a07bc61a476b59e` received 2026-09-07 confirms `Application received!` and says COSHUMA's Sendcloud application has been submitted for Sendcloud's review at `support@coshuma.com`.
- State: `application_submitted`; the earlier browser-form blocker is resolved.
- No approval, customer-facing tracking URL, conversion, commission, or revenue is claimed yet.
- Do not submit another Sendcloud application while this one is under review, and do not treat the PartnerStack application/dashboard URL as a customer affiliate link.

## AI Video Cut
- Current official affiliate page: https://www.aivideocut.com/affiliate
- Previous verification found the vendor requires its interactive application form; no authenticated browser submission completion evidence is available in this automation context.
- State: `browser_required_application`; do not mark `application_submitted` until the confirmation screen or vendor email is actually observed.

## Operating rule
These blockers must not stop other COSHUMA revenue work. Skip them while the user is absent, do not retry blindly, and resume only when the required browser or verification step is available. No revenue is claimed for any of these programmes yet.
