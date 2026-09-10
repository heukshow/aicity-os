# COSHUMA Revenue Truth Rules

This file documents the revenue-accounting safety rules for COSHUMA.

1. Actual verified revenue is the primary KPI.
2. `null` means unknown / not yet reconciled. It must never be rendered or interpreted as zero.
3. Clicks, signups, trials, paid customers, commission and payout are separate stages. Never infer a later stage from an earlier stage.
4. Any non-null downstream value must have an evidence source and evidence timestamp.
5. PartnerStack data is partial network coverage unless all relevant programs and pages are explicitly reconciled.
6. FirstPromoter, Impact, Rewardful, Tapfiliate, Affonso and vendor-native dashboards remain separate coverage areas until verified data is ingested.
7. Vendor email reports may be used as direct evidence only when they explicitly state the metric and scope.
8. GA4 `affiliate_click` is outbound-click evidence only. It is not signup, sale or commission evidence.
9. A verified $0 for one vendor or one reporting period must not be promoted to an all-network $0.
10. Customer-facing affiliate URLs must be vendor-issued or explicitly verified; dashboard/login/homepage URLs are never revenue links by default.

Current seed data: `data/revenue-truth-2026-09-11.json`.
