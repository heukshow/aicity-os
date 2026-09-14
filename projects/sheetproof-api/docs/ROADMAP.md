# Roadmap

## v0.3 — Reliability + deployment readiness
- [x] Add realistic XLSX/CSV fixtures (clean and intentionally broken).
- [x] Add regression tests for current error classes.
- [x] Add upload-size/type safety without server-side upload persistence.
- [x] Add structured sheet/row/column locations to findings.
- [x] Add multi-sheet workbook analysis.
- [x] Add downloadable JSON/CSV full report for validation.
- [ ] Add public-facing privacy/retention page and explicit limitations.
- [ ] Add production server/deployment configuration and build/run Docker image.
- [ ] Deploy to a public host and verify externally.

## v0.4 — Public validation
1. Collect only anonymous aggregate usage counters.
2. Test with real external users and record false positives/negatives.
3. Improve rules from observed failures rather than adding speculative AI features.
4. Measure upload-to-result and report-download funnels.

## v0.5 — Monetization test
1. Keep basic scan free.
2. Test a low-friction one-time full-report purchase only after public usage exists.
3. Only after purchase validation: bundles/subscription.

## Later
- Custom business rules/templates
- Google Sheets add-on
- Microsoft Marketplace version
- Optional AI explanation/repair suggestions after deterministic checks are trusted
- ChatGPT app/plugin entry point, subject to current platform rules
