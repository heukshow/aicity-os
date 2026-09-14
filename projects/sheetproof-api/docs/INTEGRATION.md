# SheetProof v3 repository integration

## Source and scope

Imported `SheetProof_Project_v0.3-pre_patched_v3.zip` from the local Downloads
folder. Archive SHA-256:
`8909c31c686433dac9c0789ed976b2c098f8b2821ed3ad6882a0568ae3fb7c6c`.
The referenced `/mnt/data` archive was not accessible on this Windows host;
the matching local filename is the source used here, not proof of byte identity
with the inaccessible attachment. Original engine, tests, fixtures and Dockerfile
are preserved. The original dated STATUS document describes the source archive.

Backend: `projects/sheetproof-api`. Frontend: `projects/cosuma-market`.
Run backend commands from its directory so the `app` module resolves independently
of other projects. CI only installs dependencies and runs tests; it has read-only
repository access and no deployment credentials or deployment steps.

## Local connection

```powershell
# From projects/sheetproof-api, after creating/activating a virtual environment:
python -m pip install -r requirements.txt
$env:ALLOWED_ORIGINS = 'http://localhost:3000'
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a separate terminal, from `projects/cosuma-market`:

```powershell
$env:NEXT_PUBLIC_SHEETPROOF_API_URL = 'http://localhost:8000'
npm ci
npm run dev
```

Open `http://localhost:3000`. Use the exact origin; `127.0.0.1` and `localhost`
are different browser origins. The backend reads ALLOWED_ORIGINS when imported;
restart it after changes. `.env.example` is documentation, not an automatically
loaded backend environment file. APP_ENV and MAX_UPLOAD_MB in the original
example are not implemented configuration knobs: the current size cap is 10 MiB.

The frontend variable is the API origin only (no `/api/analyze` suffix). It is
public and embedded at Next.js build time; change it before rebuilding. Blank
configuration shows the existing server-not-connected message.

## Actual API contract

- `GET /health`: status and version.
- `POST /api/analyze`: multipart field `file`, XLSX/XLSM/CSV.
- Summary: `issues_total`, `high`, `medium`, `low`.
- Details: `preview` (up to three findings), `locked_count` for omitted findings.
- Finding fields: `severity`, `check`, `message`, `sheet`, `row`, `column`.
- `POST /api/report/json` and `/api/report/csv` accept the same upload and
  expose the full report in this validation version. There is no payment gate.

The Next.js uploader now reads `preview` and `check` instead of nonexistent
`issues` and `type`. It explicitly reports omitted findings. Download endpoints
remain available in the backend; this change does not add a frontend checkout.

## PR and deployment boundary

Initial PR head: `ef508c4f9afbcabc32829c728a3f29de9dee4b8d`.
Main fetched for reconciliation: `6a0df932ccdd20fcc116bd411cee74cebdd5972c`.
`git merge --no-commit --no-ff origin/main` succeeded without conflict markers
or unmerged paths. No file-level conflict was reproduced. The initial GitHub
connector reported mergeable=false; its cause was not established by that flag.
The merge commit preserves both histories without force-pushing.

Initial Vercel checks for `cosuma-market-b2b` and `coshuma-official` both linked
to `upgradeToPro=build-rate-limit`; this is not a compiler failure.
Branch-specific `git.deploymentEnabled` guards at the repository root and the
two site roots disable Git deployments for `sheetproof-site-conversion` only.
Other branches retain default behavior. Do not merge, deploy or change domains
until separately authorized. No Vercel limit upgrade is requested.

See [Vercel Git configuration](https://vercel.com/docs/project-configuration/git-configuration)
and [Cloud Run preparation](CLOUD_RUN.md).
