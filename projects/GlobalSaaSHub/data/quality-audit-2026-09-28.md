# COSHUMA quality audit — 2026-09-28 KST

Scope: fresh main `bda268261de0bed41d68458f4f2982bdcf409380`, current registry (36 prior records), #292 through comment 5858398134, open PR inventory, recent Actions, authenticated-session availability, current live home/interaction checks, all 179 source tool records and generated public artifacts. No matching open COSHUMA PR existed at discovery. This is an operating-quality audit, not a new business plan or KPI approval.

## Ten standards

| Standard | Classification at discovery | Evidence / action |
|---|---|---|
| Clear user purpose and customer-only copy | Confirmed problem | Live Supademo pricing displayed an ingestion placeholder; Synthflow pricing displayed referral-plan wording. Two source values leaked into the home dataset and six static tool/compare pages. Remove them without inventing prices; guard source, producer and final artifacts. |
| Buyer decision support | Confirmed problem; partly resolved elsewhere | Home unknown prices were assigned 25 and matched the $20–$50 budget. Reproduced with Supademo. Remove invented fallback and preserve decimal boundaries. #883 comparison-neutrality work is already deployed; do not duplicate. |
| Trust and evidence | Confirmed problem / insufficient data | Missing pricing stays unknown with an official-pricing action. Existing verified product facts and exact affiliate URLs are unchanged. This audit is not a claim that every vendor fact has been independently revalidated today. |
| Mobile, performance and accessibility | Partly resolved / runtime limitation | Existing mobile fixes and compare controls are present. Repeat 320/360/375/390/412/430 portrait plus 844×390 emulator checks. Main search has no persistent accessible name; add one. Physical-device completion remains open in PRODUCT:REAL-DEVICE-COMPARE-QA-20260927. |
| Revenue and user benefit | Structural checks resolved; outcome data insufficient | All 72 approved_tracking tools have buyer pages, exact primary URLs and affiliate CTAs in generated source. Constant Contact is the sole approved-without-link tool and remains an intentional legal hold. Preserve disclosures and sponsored rel attributes. |
| Search and revisit value | Partial / insufficient mature outcome data | Analytics run 36337947871 confirms existing demand on Gamma compare/home and buyer-intent GSC pages including Unbounce, Brand24, Omnisend, Beefree and Pipedrive. GSC latest record is 2026-09-25. Do not compare different table periods or assume titles alone caused low CTR. Existing assets take priority; no new pages/features. |
| Accurate measurement | Implementation checks present; incomplete windows | Latest successful snapshot collected 2026-09-27T17:42:44.663Z. Fixed 7-day post period Sep28–Oct4 is available Oct7; 30-day Sep28–Oct27 is available Oct30 (Asia/Seoul). New-event baseline is unavailable_before_instrumentation; post metrics are not_matured; downstream vendor funnel remains unavailable where unobserved. Preserve events/periods and QA exclusion. |
| Operating efficiency | Partly resolved | Eleven canonical teams and Watchdog are enabled and have actual recent runs within twice their intended interval at audit start. Reusable generation/build guards cover recurrence. Apply the operating contract through existing teams; no additional scheduler/service. |
| Fault isolation and recovery | Partly resolved / external waiting / runtime limitation | Source→build→live gates and deterministic release specs exist. Native scheduler fidelity still needs its existing two-consecutive-run gate despite verified operational fallback. Browser owner session expired; existing Cloudflare API read returned 401 and Wrangler returned code10000. Do not classify this as lost data or invent current revenue. Analytics collection/upload succeeded independently; continue public fixes. |
| Evidence-led improvement | Insufficient mature outcome data | Prior Gamma baseline has views but zero affiliate clicks; recent changes are in measurement. No uplift or revenue forecast is justified. Continue matched-period observation and independently sourced vendor stages. |

## Fix-First continuation

- Task/record: `QUALITY:PUBLIC-PRICING-TRUTH-20260928`; discovery #292 comment 5858523358.
- Found/fixed by Operations Governance; canonical maintenance: Product Experience (filter/accessibility), Editorial Quality (public source/producer boundary).
- Minimal change: two unverified text values, six affected static pages, shared fail-closed value policy, public projection validation-before-write, budget filter truth and search aria-label. No verified price, affiliate URL, event definition or broad layout change.
- Regression evidence: unknown price cannot match paid budgets; decimal amounts retain correct boundaries; poisoned source values cause producer/source/dist failures; rejected generation preserves the previous safe artifact.
- Completion is pending until PR Build Check, merge, current deployed ancestry, live filter/copy behavior and registry/#292 release evidence are recorded. Audit documentation alone is not production verification.
- Measurement annotation: record the actual deployment time in the registry/#292. This narrow home filter/accessibility correction falls within the active home comparison measurement window; do not attribute all subsequent changes to #863 or claim a clean causal experiment.

## Remaining executable actions

- Revenue Intelligence: existing authenticated owner recovery or existing connected collector evidence; inspect current timestamp/period/unknown fields. API401 and CLI10000 are authentication failures, not proof of empty revenue. No new account/token.
- Audience Growth: continue AG-DIRECT-MEASURE-002 authenticated eight-event observation; current browser raw-JSON capability gap is not a production pass.
- Product Experience: retain physical-device task until an actual controllable device is available; emulator passes must remain labeled emulator.
- Governance/Watchdog: continue the current scheduler record and observe two consecutive native scheduled runs within the accepted interval; do not open a duplicate incident.
- Affiliate Partnerships: wait in the existing Constant Contact clarification thread; keep approved, terms_not_accepted and tracking_url=null. This is external waiting plus intentional hold, not a technical failure.
- Growth/Revenue Optimization: evaluate the existing 7/30-day matched reports only when available; work on confirmed errors meanwhile. EVAL-001 remains low-priority paper feasibility.

Public audit references identify evidence and coverage, not a copied private revenue ledger. Fresh authenticated financial values remain unverified in this pass.
