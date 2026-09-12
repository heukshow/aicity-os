# SheetProof Status — 2026-09-08

## Verified in this environment
- FastAPI home route returns HTTP 200.
- Automated tests: **25 passed** (5 added for the has_hint Korean-compound/English-substring fix, title-row header detection, CSV formula-injection neutralization, and event-loop-blocking fix; 3 more added for the follow-up regressions: '전화번호'/'우편번호' no longer misread as ID columns, and a sparse-but-real header row no longer gets replaced by its own first data row; 2 more added for CORS: disabled by default, enabled per-origin via ALLOWED_ORIGINS).
- CORS is opt-in via the `ALLOWED_ORIGINS` env var (comma-separated exact origins). Unset/empty means no CORS middleware is installed at all, so cross-origin browser requests stay blocked by default until a frontend domain is configured.
- Dockerfile now runs the app as a non-root user (`appuser`); a `.dockerignore` keeps local dev cruft (`.env`, `__pycache__`, `.git`, `tests/`, `docs/`) out of the build context.
- CSV/XLSX/XLSM upload support is present.
- Multi-sheet XLSX/XLSM workbooks are analyzed sheet-by-sheet.
- Every finding now carries structured `sheet`, `row`, and `column` location fields where applicable.
- Full findings can be downloaded as UTF-8 BOM CSV or JSON during the v0.3 validation stage.
- Upload safety checks cover supported extension, empty file, 10MB file-size cap, and 100,000 total-row cap across sheets.
- Files are parsed from request bytes in memory; the application does not intentionally write uploaded files to server disk.
- `/health` now reports the same `0.3.0-pre` version as the FastAPI application.
- Realistic fixtures included:
  - `ecommerce_clean.xlsx` → API result: 0 issues.
  - `ecommerce_broken.xlsx` → API result: 4 issues (3 high, 1 low).
  - `invoice_broken_cp949.csv` → API result: 2 issues (2 high).
- CP949 CSV parsing remains covered by automated tests.

## Known / intentional behavior
- A mostly-populated column is treated as a likely required field only when at least 85% of rows are populated. This is heuristic behavior, not a universal rule.
- Date detection remains conservative to avoid treating generic Korean column names containing `일` as dates.
- Duplicate numeric/type warnings remain reduced.
- The 100,000-row cap applies to the sum of all sheets in one workbook.
- CSV is represented as a single logical sheet named `CSV`; Excel retains real worksheet names.

## Not yet verified
- Production-scale false-positive/false-negative rate.
- Complex workbooks with formulas, merged cells, pivots, charts, external links, or macros that affect calculated values.
- Public internet deployment.
- Docker build/run in this environment.
- External users, payment, revenue, or marketplace listings.

## Current milestone
**v0.3 reliability core complete; next focus is deployment + privacy/public validation.**
