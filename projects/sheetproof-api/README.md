# SheetProof

Spreadsheet QA MVP for CSV/XLSX/XLSM files.

Repository integration and frontend connection: [docs/INTEGRATION.md](docs/INTEGRATION.md).
Billing-blocked deployment preparation: [docs/CLOUD_RUN.md](docs/CLOUD_RUN.md).
Current local verification: [docs/VERIFICATION.md](docs/VERIFICATION.md).

## Current verified state
- Local FastAPI MVP exists.
- CSV/XLSX/XLSM upload endpoints exist.
- Multi-sheet Excel workbooks are analyzed sheet-by-sheet.
- Core checks include missing values, duplicate rows/IDs/SKUs, mixed types, numeric/date formatting inconsistencies, and quantity × unit price vs amount mismatches.
- Findings include worksheet, row, and column locations where applicable.
- Full findings can be downloaded as CSV or JSON during validation.
- Automated test suite: **25 passed**.
- No public deployment, real external users, payment, or revenue has been verified yet.

## Run on Windows
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## Run tests
```powershell
pytest -q
```

## Project layout
- `app/` application code and UI
- `tests/` automated tests and realistic fixtures
- `docs/STATUS.md` verified project state
- `docs/ROADMAP.md` next steps
- `Dockerfile` deployment-ready container entry point
