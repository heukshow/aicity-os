"""
promote_approved_artifact.py
============================
Downloads and validates an approved dry-run Artifact before Production promotion.

Usage (called by GitHub Actions Production branch):
  python promote_approved_artifact.py \
      --artifact-id <ARTIFACT_ID> \
      --artifact-sha256 <SHA256_HEX> \
      --approved-head-sha <GIT_SHA> \
      --repo <owner/repo> \
      --output-dir projects/GlobalSaaSHub/data

Safety contract:
  - NEVER calls Tavily, Gemini, or any external discovery API.
  - NEVER generates new tool data.
  - Exits code 1 on ANY validation failure.
  - Exits code 0 only when all checks pass and tools.next.json is written.
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
import zipfile
import io

REQUIRED_ARTIFACT_FILES = ["tools.next.json", "run_summary.json"]


def fatal(msg):
    print(f"FATAL: {msg}", file=sys.stderr)
    sys.exit(1)


def log(msg):
    print(f"[promote] {msg}")


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get_github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        fatal("GITHUB_TOKEN environment variable is not set.")
    return token


def download_artifact_zip(repo: str, artifact_id: str, token: str) -> bytes:
    """Download Artifact ZIP via GitHub API (returns raw bytes)."""
    url = f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}/zip"
    log(f"Downloading artifact {artifact_id} from {repo}...")
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        # GitHub API redirects to S3; urlopen follows redirects automatically.
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        log(f"Downloaded {len(data):,} bytes.")
        return data
    except urllib.error.HTTPError as e:
        fatal(f"GitHub API HTTP {e.code} when downloading artifact {artifact_id}: {e.read().decode('utf-8', errors='replace')[:300]}")
    except Exception as e:
        fatal(f"Network error downloading artifact: {type(e).__name__}: {e}")


def verify_artifact_sha256(zip_bytes: bytes, expected_sha256: str):
    """Compare SHA256 of downloaded ZIP bytes to approved value."""
    actual = sha256_of_bytes(zip_bytes)
    log(f"Artifact SHA256: {actual}")
    log(f"Expected SHA256: {expected_sha256}")
    if actual.lower() != expected_sha256.lower():
        fatal(
            f"SHA256 MISMATCH. Downloaded artifact does not match approved digest.\n"
            f"  Expected: {expected_sha256}\n"
            f"  Actual:   {actual}"
        )
    log("SHA256 verified OK.")


def get_artifact_metadata(repo: str, artifact_id: str, token: str) -> dict:
    """Fetch artifact metadata to verify head_sha and workflow_run."""
    url = f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except Exception as e:
        fatal(f"Could not fetch artifact metadata: {e}")


def verify_head_sha(metadata: dict, approved_head_sha: str):
    """Verify the artifact was generated from the approved head commit."""
    workflow_run = metadata.get("workflow_run", {})
    artifact_head_sha = workflow_run.get("head_sha", "")
    artifact_repo = workflow_run.get("repository_id", "")
    log(f"Artifact head_sha from metadata: {artifact_head_sha}")
    log(f"Approved head_sha:               {approved_head_sha}")
    if artifact_head_sha.lower() != approved_head_sha.lower():
        fatal(
            f"HEAD SHA MISMATCH. Artifact was built from {artifact_head_sha!r}, "
            f"but approved head SHA is {approved_head_sha!r}."
        )
    log("head_sha verified OK.")


def extract_and_validate_zip(zip_bytes: bytes, output_dir: str, approved_head_sha: str, metadata: dict = None) -> dict:
    """
    Extract ZIP, verify required files exist, parse tools.next.json,
    validate run_summary.json internal security contracts,
    and write tools.next.json to output_dir.
    Returns the parsed tools and summary data.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as e:
        fatal(f"Downloaded artifact is not a valid ZIP: {e}")

    names = zf.namelist()
    log(f"ZIP contains: {names}")

    # Verify required files
    for required in REQUIRED_ARTIFACT_FILES:
        matches = [n for n in names if os.path.basename(n) == required]
        if not matches:
            fatal(f"Required file '{required}' not found in artifact ZIP. Contents: {names}")

    # Extract tools.next.json
    tools_matches = [n for n in names if os.path.basename(n) == "tools.next.json"]
    tools_raw = zf.read(tools_matches[0])

    try:
        tools_data = json.loads(tools_raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        fatal(f"tools.next.json in artifact is not valid JSON: {e}")

    if not isinstance(tools_data, list):
        fatal(f"tools.next.json must be a JSON array, got {type(tools_data).__name__}")

    if len(tools_data) == 0:
        fatal("tools.next.json contains 0 tools. Refusing to promote empty dataset.")

    log(f"tools.next.json: {len(tools_data)} tools. JSON valid.")

    # Extract run_summary.json and validate internal security contract
    summary_matches = [n for n in names if os.path.basename(n) == "run_summary.json"]
    summary_raw = zf.read(summary_matches[0])
    try:
        summary_data = json.loads(summary_raw.decode("utf-8"))
        log(f"run_summary.json parsed OK. Keys: {list(summary_data.keys())[:10]}")
    except json.JSONDecodeError as e:
        fatal(f"run_summary.json in artifact is not valid JSON: {e}")

    # --- RUN_SUMMARY CONTRACT VALIDATION ---
    # 1. artifact_schema_version
    schema_ver = summary_data.get("artifact_schema_version")
    if not schema_ver or str(schema_ver) != "1.0":
        fatal(f"run_summary.json artifact_schema_version mismatch or missing. Expected '1.0', got {schema_ver!r}")

    # 2. source_head_sha vs approved_head_sha
    summary_head_sha = summary_data.get("source_head_sha", "")
    if summary_head_sha != "local-dev" and summary_head_sha.lower() != approved_head_sha.lower():
        fatal(
            f"run_summary.json source_head_sha MISMATCH.\n"
            f"  run_summary.json: {summary_head_sha!r}\n"
            f"  approved_head:    {approved_head_sha!r}"
        )

    # 3. dry_run must be True
    dry_run_val = summary_data.get("dry_run")
    if dry_run_val is not True and str(dry_run_val).lower() != "true":
        fatal(f"run_summary.json dry_run must be True for an approved artifact, got {dry_run_val!r}")

    # 4. failure_test must be False
    fail_test_val = summary_data.get("failure_test")
    if fail_test_val is not False and str(fail_test_val).lower() != "false":
        fatal(f"run_summary.json failure_test must be False for an approved artifact, got {fail_test_val!r}")

    # 5. source_run_id vs workflow_run.id (if metadata provided)
    if metadata and "workflow_run" in metadata:
        expected_run_id = str(metadata["workflow_run"].get("id", ""))
        summary_run_id = str(summary_data.get("source_run_id", ""))
        if summary_run_id != "local-run" and expected_run_id and summary_run_id != expected_run_id:
            fatal(
                f"run_summary.json source_run_id MISMATCH.\n"
                f"  run_summary.json: {summary_run_id!r}\n"
                f"  metadata run id:  {expected_run_id!r}"
            )

    log("run_summary.json internal security contract verified OK.")

    # Write tools.next.json to output_dir
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "tools.next.json")
    with open(out_path, "wb") as f:
        f.write(tools_raw)
    log(f"Written: {out_path} ({len(tools_raw):,} bytes)")

    return {"tools": tools_data, "summary": summary_data}


def main():
    parser = argparse.ArgumentParser(description="Promote approved Artifact to Production.")
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--artifact-sha256", required=True)
    parser.add_argument("--approved-head-sha", required=True)
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--output-dir", default="projects/GlobalSaaSHub/data")
    args = parser.parse_args()

    # Guard: all three required inputs must be non-empty
    for field, val in [
        ("artifact-id", args.artifact_id),
        ("artifact-sha256", args.artifact_sha256),
        ("approved-head-sha", args.approved_head_sha),
    ]:
        if not val or not val.strip():
            fatal(f"--{field} is required and must not be empty.")

    log("=== Artifact Promotion Validation START ===")
    log(f"Artifact ID:       {args.artifact_id}")
    log(f"Approved head SHA: {args.approved_head_sha}")
    log(f"Output dir:        {args.output_dir}")

    token = get_github_token()

    # 1. Fetch metadata and verify head_sha
    metadata = get_artifact_metadata(args.repo, args.artifact_id, token)
    verify_head_sha(metadata, args.approved_head_sha)

    # 2. Download ZIP
    zip_bytes = download_artifact_zip(args.repo, args.artifact_id, token)

    # 3. Verify SHA256
    verify_artifact_sha256(zip_bytes, args.artifact_sha256)

    # 4. Extract, validate, and write
    result = extract_and_validate_zip(zip_bytes, args.output_dir, args.approved_head_sha, metadata)

    log(f"=== Artifact Promotion Validation PASSED ===")
    log(f"tools.next.json ready at {args.output_dir}/tools.next.json")
    log(f"Tool count: {len(result['tools'])}")
    sys.exit(0)


if __name__ == "__main__":
    main()
