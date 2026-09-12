# Cloud Run preparation — do not deploy while Billing is blocked

This is an unexecuted deployment recipe. Billing recovery, a usable project,
the final frontend origin, image registry and service identity must be verified
before deployment. No project recovery, billing change or cloud build is part
of this PR. Do not assume an older project ID is available.

## Proposed small-service settings

| Setting | Value |
| --- | --- |
| Billing | Request-based, `--cpu-throttling` |
| Minimum instances | 0 at service and revision levels |
| Maximum instances | 1 initially at service and revision levels; 2 after review |
| CPU / memory | 1 vCPU / 1 GiB |
| Concurrency | 1, to limit simultaneous in-memory workbook parsing |
| Timeout | 120 seconds, subject to real workbook testing |
| Startup CPU boost | Disabled |
| Application port | 8000, supplied through PORT |
| CORS | Exact frontend origins in ALLOWED_ORIGINS, never `*` |

These are cost controls, not a guaranteed spending cap. Requests, startup,
network transfer, builds, logs and artifact storage can still incur charges.
Maximum instances can be temporarily exceeded by platform behavior. A compressed
10 MiB workbook can expand considerably in memory; 1 GiB is a starting allocation,
not a validated worst-case memory bound. CORS is browser policy, not authentication
or abuse prevention. Before public launch, assess rate limits and upload expansion
limits. Budget alerts inform spending decisions but do not stop charges.

## Future deployment recipe (PowerShell; not executed)

First build/test the existing Dockerfile locally using `projects/sheetproof-api`
as the build context. After Billing recovery and approval, publish a tested image
to the chosen registry, then fill the placeholders below. No build/push automation
is included here. Use a dedicated service account with no unnecessary cloud access.

```powershell
$sheetproofProject = 'REPLACE_WITH_VERIFIED_PROJECT_ID'
$sheetproofRegion = 'REPLACE_WITH_APPROVED_REGION'
$sheetproofImage = 'REPLACE_WITH_TESTED_IMAGE_DIGEST'
$sheetproofIdentity = 'REPLACE_WITH_SERVICE_ACCOUNT_EMAIL'
# env.yaml must contain ALLOWED_ORIGINS as a quoted comma-separated string.
# Example only after domain confirmation:
# ALLOWED_ORIGINS: "https://cosuma.co.kr"
gcloud run deploy sheetproof-api `
  --project $sheetproofProject `
  --region $sheetproofRegion `
  --image $sheetproofImage `
  --service-account $sheetproofIdentity `
  --cpu 1 --memory 1Gi `
  --cpu-throttling --no-cpu-boost `
  --min 0 --max 1 --min-instances 0 --max-instances 1 `
  --concurrency 1 --timeout 120 --port 8000 `
  --env-vars-file env.yaml `
  --no-allow-unauthenticated
```

Start private for authenticated smoke tests. Direct browser uploads from the
current frontend require public invocation; enable it only as part of a separately
approved public launch, after abuse controls and the exact CORS origin are reviewed.
Keep both maximum settings aligned if increasing the cap to 2.

## Evidence to collect after an authorized deployment

1. Inspect the service and active revision configuration, Billing state and IAM.
2. Record the actual service URL; verify authenticated `/health` returns 200.
3. Upload clean/broken XLSX and CP949 CSV fixtures; compare with local tests.
4. Verify allowed-origin preflight and an unlisted-origin rejection.
5. After approved public invocation, set NEXT_PUBLIC_SHEETPROOF_API_URL to the
   actual origin, rebuild the frontend and verify browser upload/result rendering.
6. Review memory, latency, errors and billing metrics before changing the cap.

Official references checked for this recipe:
- [gcloud run deploy flags](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy)
- [Billing settings](https://docs.cloud.google.com/run/docs/configuring/billing-settings)
- [Cloud Run pricing](https://cloud.google.com/run/pricing)
- [Maximum instance limits](https://docs.cloud.google.com/run/docs/configuring/max-instances)
- [Budget alerts](https://docs.cloud.google.com/billing/docs/how-to/budgets)
