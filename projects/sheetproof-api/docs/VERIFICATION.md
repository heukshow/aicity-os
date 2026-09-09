# Integration verification — 2026-09-10

Executed locally on Windows with Python 3.11.6 and Node 22.15.0:

- `python -m pytest -q` from this backend: **25 passed, 2 warnings in 2.30s**.
  Warnings concern Starlette/httpx and an AnyIO deprecated alias.
- Installed environment includes FastAPI 0.141.1, pandas 3.0.5,
  openpyxl 3.1.5, pytest 9.1.1 and httpx 0.28.1. Requirements retain the
  original lower bounds, so future dependency resolution can differ.
- Archive comparison: 18 original files byte-identical, including engine,
  tests, fixtures and Dockerfile. README intentionally gains documentation links.
- Real TestClient upload of `ecommerce_broken.xlsx`: HTTP 200,
  4 total findings, 3 preview findings, 1 omitted finding.
- Transpiled uploader rendered with that real API response and mocked React
  state: all three finding messages and the omitted count appeared in HTML.
  This is a local render-contract check, not a browser E2E test.
- `npm ci --no-audit --no-fund` and `npm run build` from the frontend:
  successful production build, lint/type validation and static page generation.
- CI YAML parsed; read-only permissions and test-only commands inspected.
  Workflow uses Ubuntu/Python 3.12 to align with the original Dockerfile.
- `git diff --check`: no whitespace errors.

## Remaining release checks

The frontend installer reports an existing vulnerability in Next.js 14.2.0.
No dependency upgrade is included in this integration; resolve the supported
patched version before public release. The build also warns of outdated
Browserslist data. These warnings did not fail the local build.

Docker is not available on this host, so container build/run is unverified.
Cloud Run resource sizing, public API reachability, browser CORS/E2E, Vercel
limit recovery and domain mapping remain unverified. No cloud deployment,
domain change, billing operation or PR merge was performed.

Remote CI and mergeability must be read from the current PR head after push;
local passing tests do not establish a remote CI outcome.
