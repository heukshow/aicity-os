# SheetProof Project Manifest

## Product thesis
A self-service spreadsheet validation tool that checks CSV/XLSX/XLSM files for deterministic data-quality and consistency problems, then can later add optional AI explanations and repair suggestions.

## Current MVP scope
- Upload CSV/XLSX/XLSM
- Analyze all worksheets in Excel workbooks
- Analyze common spreadsheet quality issues
- Show summary and preview findings
- Attach sheet/row/column locations to findings
- Download full findings as CSV/JSON during validation
- No login
- No payment
- No public deployment yet

## Current verified engineering state
- 15 automated tests pass.
- Existing realistic clean/broken fixtures pass expected regressions.
- CP949 CSV is supported.
- File type, empty-file, 10MB, and 100,000 total-row safety gates exist.
- Uploaded request bytes are analyzed in memory; no intentional server-disk upload persistence is implemented.
- Health endpoint reports `0.3.0-pre` consistently.

## Next objective
Get to a **publicly reachable v0.3** with an explicit privacy/retention notice and limitations, then measure whether real people upload files and download reports before adding payment.

## Next engineering tasks
1. Add public privacy/retention/limitations page.
2. Build and run the Docker image in an environment with Docker available.
3. Add production deployment configuration for the selected host.
4. Deploy and verify the public URL from outside the development environment.
5. Add anonymous aggregate usage counters only after the privacy text matches the implementation.

## Monetization gate
Do not claim product-market fit or add a subscription until external use is observed. Initial monetization test should be a low-friction one-time full report purchase only after public-use validation.
