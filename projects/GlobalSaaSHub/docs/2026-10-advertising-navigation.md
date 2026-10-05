# Advertising navigation recovery — 6 October 2026

The owner reported that the shared advertising locations could not easily be found by entering the site normally. Current App.jsx had no advertising-information link in its header or footer. Its only sponsorship link was checkout-gated. normalize_sponsorship_offer.py also removed literal Advertise links.

This bounded navigation correction adds an always-visible Advertise header link, a mobile Menu with guides/comparisons/advertising, and footer links. The existing advertiser page now exposes its eight-location index near the top, with direct, descriptive links to each real ad position. The existing inventory producer generates these links; a new duplicate inventory source was not introduced.

The normalizer now preserves informational navigation while retaining removal of the obsolete inline purchase section. A failing regression also identified an incorrect regex boundary after the section ID; the boundary is corrected. Six navigation/safety tests run in prebuild. The existing public-copy compatibility tests remain required.

Only navigation and its producers change. No new ads, products, prices, logo assets, affiliate destinations, financial records, paid renderer, Worker configuration or paid checkout is enabled. No review PDF is published. The current email-draft interface remains separate from future direct booking. Links are not a claim that paid bookings are open.

QA query flags are preserved across the new homepage links and existing advertiser-example navigation. Existing event names and fixed 7/30-day windows remain unchanged. This navigation revision must be annotated at the verified publication time; no traffic or conversion uplift is claimed.

Canonical owner: Product Experience Team. Release requires canonical CI, exact source/build/Pages ancestry, and real public navigation checks. Synchronize evidence in #292 after verification; merge alone is not completion.
