# Production affiliate verification — 2026-09-07 20:39 KST

## Scope

Production-state verification for high-value approved affiliate CTAs on the `gh-pages` branch. This file records what is actually present in the deployed artifact and is not evidence of clicks, signups, commission, or revenue.

## Jotform

- Production artifact: `gh-pages/tool/jotform.html`
- Verified customer-facing partner URL present in the hero CTA: `https://www.jotform.com/ai/agents/?partner=coshuma`
- CTA source: `jotform-hero-ai-agents`
- Link is marked `rel="sponsored noopener noreferrer"`.
- The page also keeps the normal pricing URL as a non-affiliate official link.
- Result: **production revenue CTA verified**.

## Gamma

- Production artifact: `gh-pages/tool/gamma.html`
- Verified affiliate URL present in the hero CTA: `https://try.gamma.app/pu20lusdpn1j`
- Additional affiliate CTAs on the same page use the same exact URL.
- CTA sources include `gamma_hero_free`, `gamma_plan_fit_free`, and `gamma_bottom_free`.
- Links are marked `rel="sponsored noopener noreferrer"`.
- Result: **production revenue CTA verified**.

## Deployment interpretation

- GitHub Pages deployment for `gh-pages` completed successfully on 2026-09-07 before this verification.
- Vercel bot comments reporting the separate `coshuma-official` project hitting its daily resource limit do not negate the verified contents of the `gh-pages` production artifact used for `coshuma.com`.
- Do not claim revenue until click/signup/commission/sale evidence exists.

## Next safe priorities

1. Keep newly submitted affiliate programs in their current submitted/pending state; do not resubmit.
2. Prefer newly issued customer tracking URLs over generic dashboards or onboarding URLs.
3. Continue free enrollment work only for candidates with no prior submitted/approved/rejected/pending/cooldown/closed state.
