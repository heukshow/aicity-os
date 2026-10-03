# COSHUMA Operations Control Plane

`data/operations_registry.json` is the machine-readable lifecycle authority for active COSHUMA work.

GitHub issues #763 and #292 remain evidence/audit channels. They do not independently override the registry after a state has been synchronized.

Rules:
- one active record per task/target;
- one DRI and one next owner;
- merge/build success is not completion;
- production work stays open until production verification evidence exists;
- user gates are limited to CAPTCHA, OTP, legal consent, payment, or forced identity verification;
- recurring incidents reuse the same incident key;
- teams consume assigned queue entries instead of creating duplicate work.

Run:

```bash
python scripts/validate_operations_registry.py
python scripts/next_operations_task.py
```

Every PR touching the registry must pass the validator before any source-mutating build preparation.

## Site quality operating contract (2026-09-28 KST)

Apply these standards to the existing approved COSHUMA operation. This is not authorization for the proposed 2028 profit plan, new revenue assumptions, new KPIs, or a new large project.

1. State the visitor's task clearly; exclude internal operations and ingestion copy from customer surfaces.
2. Support decisions with prices, capabilities, differences, tradeoffs, suitable users and reasons not to buy. Never favor a partner without product evidence.
3. Use official or direct evidence. Never fabricate reviews, facts, prices or outcomes; missing information stays unknown.
4. Verify public mobile layouts, touch targets, keyboard access, links, CTAs, forms, filters, save/share and comparison interactions. Separate emulator evidence from physical-device evidence.
5. Keep editorial judgments independent from commission. Publish only independently verified exact customer affiliate destinations with consumer disclosure and sponsored attribution.
6. Improve existing buyer-intent assets using actual search evidence; require a real buyer benefit before adding save/share/revisit features.
7. Separate page views, CTA impressions, affiliate clicks, signup/referral, trial, paid customer, commission and payout. Preserve confirmed zero, unknown, unavailable, stale and current; never sum unmatched periods or overlapping funnel stages.
8. Repair reusable producers and validators so growth does not require proportional manual intervention.
9. Isolate individual vendor/API/authentication/tool blockers. Detect, diagnose, minimally fix, test, deploy, verify live and record the result.
10. Concentrate work on observed customer behavior and revenue evidence. Claim improvements only after the matched measurement period matures.

Use fresh main, `data/operations_registry.json`, #292, existing PRs, live pages and analytics/affiliate evidence. Continue a matching task rather than creating a duplicate. Classify each finding as already resolved, partially resolved, confirmed problem, insufficient data, external waiting, runtime/tool blocker, or genuinely required user action, and record its next executable action.

Priority: security/public information incidents/production failures → existing traffic conversion leaks → buyer-intent search click leaks → approved missing exact tracking → downstream revenue truth gaps → mobile/accessibility/usability → revisit/save/share → new features. Do not invent scores or revenue forecasts.

Fix-First: the discovering team may safely reproduce, diagnose, narrowly fix, test, PR, merge and verify production before handing off to the canonical maintenance owner. Record `found_by`, `fixed_by`, `canonical_owner`, `changed_scope`, `verification` and `handoff`. Release & Reliability may remain read-only.

Protect active 7/30-day fixed matched windows: no broad redesign, event name/definition changes, mass pages or CTA restructuring. Confirmed bugs, inaccessible controls, wrong destinations and public internal-copy leaks may be fixed narrowly; record deployment time and scope as a measurement annotation. Keep QA visits excluded. Never relabel incomplete windows as performance gains.

No new paid service/account/secret/token/advertising spend, unapproved legal acceptance, CAPTCHA/OTP bypass, review/comment feature, speculative KPI or large content project. Constant Contact remains approved with terms not accepted and tracking URL null until official clarification and the existing legal decision gate. Keep EVAL-001 below active measurement and affiliate work.

Use atomic writes with fresh file SHA and check each result. Do not repeat a rejected payload unchanged; after two same-cause capability failures isolate that write and continue unrelated work. Do not turn a tool block into a user gate.

Completion requires actual deployed ancestry and live expected behavior where production is the gate, followed by registry/#292 synchronization. Enabled automations alone do not prove liveness: inspect actual runs against twice the intended interval and preserve existing recovery evidence.

## Explicit one-month campaign authorization (2026-10-04 KST)

The user explicitly requested one month of autonomous operation and aggressive marketing, with goals and revenue expectations reported first and execution immediately afterward. The reported plan is recorded in `data/campaigns/2026-10-autonomous-growth.json` and `docs/2026-10-autonomous-growth-plan.md`.

Within **2026-10-04T05:27:29+09:00 to 2026-11-04T05:27:29+09:00**, this is new authorization for the bounded management targets and eight substantive buyer assets in that plan, plus up to 24 organic posts on verified existing authorized COSHUMA channels if access is available. This specific approval supersedes earlier restrictions on unapproved new KPIs/content only within this campaign. It does not approve the proposed 2028 profit plan, guarantee revenue, authorize new spend/accounts/secrets, bypass authentication, authorize unsolicited bulk messages, or reset protected experiments.

Use existing schedules and cost/runtime boundaries. Count only verified deployed assets and actual public posts. Record blocked access and unavailable financial values honestly. At the stated end, stop campaign-specific new work, retain regular operations and deliver the closeout defined in the campaign source of truth.

## User operating constraint: text and static content only (2026-10-04 06:29 KST)

The user explicitly excluded video production and YouTube-style video uploads. Until the user explicitly changes this instruction, do not assign video generation/editing, Shorts/Reels/TikTok/YouTube uploads, video-plugin/credit acquisition, or YouTube authentication recovery as COSHUMA growth work. Apply this newer constraint to the monthly campaign and regular content/distribution tasks even if an older backlog or prompt allowed video. Use evidence-backed articles, comparison tables, buyer checklists, downloadable worksheets and permitted screenshots/static graphics. The monthly external-post goal remains conditional on authorized access to at most two existing owned text/static channels. Preserve already published media. Written reviews of video SaaS remain allowed without fabricated hands-on or video-production claims.

## Necessary non-video channel signup authorized (2026-10-04 06:31 KST)

The user authorized platform-specific non-video marketing, signup where needed and direct completion of supported ordinary authentication. Reuse existing COSHUMA accounts first; if no suitable account exists, a necessary free dedicated COSHUMA non-video channel account may be created. This supersedes earlier blanket no-new-account restrictions only for this purpose. Keep at most two active distribution channels and zero additional spend. Use supported authentication capabilities and their rules for genuine consent/identity/CAPTCHA/OTP gates; no bypass, stored-secret extraction, fabricated identity or unrelated privilege expansion. Prepare and publish platform-appropriate text/static content with verified facts and traceable public evidence; historical drafts and intended posts are not publications.
