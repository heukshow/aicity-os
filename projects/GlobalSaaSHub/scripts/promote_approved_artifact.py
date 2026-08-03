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
import re

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


class SafeCrossHostRedirectHandler(urllib.request.HTTPRedirectHandler):
    """
    Custom HTTP Redirect Handler that strictly strips Authorization headers
    when redirecting across different hosts (e.g. api.github.com -> *.blob.core.windows.net),
    enforces HTTPS, blocks redirect loops, and limits max redirects to 10.
    """
    def __init__(self, max_redirects=10):
        super().__init__()
        self.max_redirects = max_redirects

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Count redirects stored on request object
        redirect_count = getattr(req, "_redirect_count", 0) + 1
        if redirect_count > self.max_redirects:
            raise urllib.error.HTTPError(
                newurl, code, f"FATAL: Max redirects ({self.max_redirects}) exceeded when downloading artifact ZIP.", headers, fp
            )

        parsed_new = urllib.parse.urlparse(newurl)

        # Enforce HTTPS scheme
        if parsed_new.scheme != "https":
            raise urllib.error.HTTPError(
                newurl, code, f"FATAL: Insecure redirect to non-HTTPS URL blocked: {newurl!r}", headers, fp
            )

        # Loop detection
        visited = getattr(req, "_visited_urls", set())
        if req.full_url in visited:
            visited.add(req.full_url)
        else:
            visited = set(visited)
            visited.add(req.full_url)

        if newurl in visited:
            raise urllib.error.HTTPError(
                newurl, code, f"FATAL: Redirect loop detected on URL: {newurl!r}", headers, fp
            )

        parsed_orig = urllib.parse.urlparse(req.full_url)
        orig_host = parsed_orig.netloc.lower()
        new_host = parsed_new.netloc.lower()

        # Create new Request object for redirected target
        new_req = urllib.request.Request(
            newurl,
            headers=dict(req.headers),
            origin_req_host=req.origin_req_host,
            unverifiable=req.unverifiable
        )
        new_req._redirect_count = redirect_count
        new_req._visited_urls = visited

        # If cross-host redirect (e.g., api.github.com -> azure blob storage), STRIP Authorization header!
        if orig_host != new_host:
            # Case-insensitive removal of Authorization header
            headers_to_remove = [h for h in new_req.headers if h.lower() == "authorization"]
            for h in headers_to_remove:
                del new_req.headers[h]
                if hasattr(new_req, "unredirected_hdrs"):
                    unred_remove = [u for u in new_req.unredirected_hdrs if u.lower() == "authorization"]
                    for u in unred_remove:
                        del new_req.unredirected_hdrs[u]

        return new_req


def download_artifact_zip(repo: str, artifact_id: str, token: str) -> bytes:
    """
    Download Artifact ZIP via GitHub API using SafeCrossHostRedirectHandler (returns raw bytes).
    Guarantees Authorization header is stripped when redirected to Azure Blob / S3 storage.
    """
    url = f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}/zip"
    log(f"Downloading artifact {artifact_id} from {repo}...")
    
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "GlobalSaaSHub-ArtifactPromoter/1.0",
        },
    )

    opener = urllib.request.build_opener(SafeCrossHostRedirectHandler(max_redirects=10))
    try:
        with opener.open(req, timeout=60) as resp:
            data = resp.read()
        log(f"Downloaded {len(data):,} bytes.")
        return data
    except urllib.error.HTTPError as e:
        fatal(f"HTTP error {e.code} when downloading artifact {artifact_id}: {e.reason or e.read().decode('utf-8', errors='replace')[:300]}")
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
            data = json.loads(resp.read())
            if not isinstance(data, dict):
                fatal(f"Artifact metadata API response must be a JSON object (dict), got {type(data).__name__}")
            return data
    except Exception as e:
        fatal(f"Could not fetch artifact metadata: {e}")


def verify_head_sha(metadata: dict, approved_head_sha: str, expected_run_id: str = None):
    """Verify the artifact metadata fields, expected run ID, expired status, and approved head commit."""
    if not isinstance(metadata, dict):
        fatal(f"Artifact metadata must be a dict, got {type(metadata).__name__}")

    # Verify expired is exactly False
    expired = metadata.get("expired")
    if expired is not False:
        fatal(f"Artifact 'expired' field must be boolean False, got {expired!r}")

    # Verify workflow_run object
    workflow_run = metadata.get("workflow_run")
    if not isinstance(workflow_run, dict):
        fatal(f"Artifact metadata 'workflow_run' must be a JSON object (dict), got {type(workflow_run).__name__}")

    if expected_run_id:
        expected_name = f"pipeline-artifacts-{expected_run_id}"
        art_name = metadata.get("name")
        if art_name != expected_name:
            fatal(f"Artifact name '{art_name}' does not match expected name '{expected_name}'.")

        wf_run_id = str(workflow_run.get("id", ""))
        if wf_run_id != str(expected_run_id):
            fatal(f"Artifact workflow_run.id '{wf_run_id}' does not match expected run ID '{expected_run_id}'.")

    artifact_head_sha = workflow_run.get("head_sha", "")
    log(f"Artifact head_sha from metadata: {artifact_head_sha}")
    log(f"Approved head_sha:               {approved_head_sha}")

    if not approved_head_sha or not isinstance(approved_head_sha, str) or len(approved_head_sha.strip()) == 0:
        fatal("Approved head_sha cannot be null or empty.")

    clean_sha = approved_head_sha.strip()
    if not re.fullmatch(r"^[0-9a-fA-F]{40}$", clean_sha):
        fatal(f"Approved head_sha '{approved_head_sha}' is not a valid 40-character hex SHA string.")

    if artifact_head_sha.lower() != clean_sha.lower():
        fatal(
            f"HEAD SHA MISMATCH. Artifact was built from {artifact_head_sha!r}, "
            f"but approved head SHA is {approved_head_sha!r}."
        )
    log("head_sha and artifact metadata contract verified OK.")


def extract_and_validate_zip(zip_bytes: bytes, output_dir: str, approved_head_sha: str, metadata: dict = None) -> dict:
    """
    Extract ZIP, verify required files exist uniquely (basename count == 1),
    parse tools.next.json, validate run_summary.json internal security contracts,
    and write tools.next.json to output_dir.
    Returns the parsed tools and summary data.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as e:
        fatal(f"Downloaded artifact is not a valid ZIP: {e}")

    names = zf.namelist()
    log(f"ZIP contains: {names}")

    # Strict basename uniqueness check: exactly 1 for tools.next.json and 1 for run_summary.json
    for required in REQUIRED_ARTIFACT_FILES:
        matches = [n for n in names if os.path.basename(n) == required]
        if len(matches) == 0:
            fatal(f"Required file '{required}' not found in artifact ZIP. Contents: {names}")
        elif len(matches) > 1:
            fatal(f"Ambiguous ZIP structure! Found {len(matches)} files matching basename '{required}': {matches}")

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
    except json.JSONDecodeError as e:
        fatal(f"run_summary.json in artifact is not valid JSON: {e}")

    if not isinstance(summary_data, dict):
        fatal(f"run_summary.json must be a JSON object (dict), got {type(summary_data).__name__}")

    log(f"run_summary.json parsed OK. Keys: {list(summary_data.keys())[:10]}")

    # --- STRICT RUN_SUMMARY CONTRACT VALIDATION (NO BYPASSES) ---
    # 1. artifact_schema_version: exact string "1.0"
    schema_ver = summary_data.get("artifact_schema_version")
    if schema_ver != "1.0":
        fatal(f"run_summary.json artifact_schema_version must be exactly string '1.0', got {schema_ver!r}")

    # 2. source_head_sha vs approved_head_sha (no local-dev bypass)
    summary_head_sha = summary_data.get("source_head_sha")
    if not summary_head_sha or not isinstance(summary_head_sha, str) or summary_head_sha.lower() != approved_head_sha.lower():
        fatal(
            f"run_summary.json source_head_sha MISMATCH or invalid.\n"
            f"  run_summary.json: {summary_head_sha!r}\n"
            f"  approved_head:    {approved_head_sha!r}"
        )

    # 3. workflow_run.id and source_run_id strict match (no local-run bypass)
    if not metadata or "workflow_run" not in metadata or metadata["workflow_run"].get("id") is None:
        fatal("Artifact metadata is missing 'workflow_run.id'. Cannot verify artifact source.")

    expected_run_id = str(metadata["workflow_run"]["id"])
    summary_run_id = summary_data.get("source_run_id")
    if summary_run_id is None or str(summary_run_id).strip() == "" or str(summary_run_id) != expected_run_id:
        fatal(
            f"run_summary.json source_run_id MISMATCH or missing.\n"
            f"  run_summary.json: {summary_run_id!r}\n"
            f"  expected run_id:  {expected_run_id!r}"
        )

    # 4. dry_run must be JSON boolean True (string "true" rejected)
    dry_run_val = summary_data.get("dry_run")
    if dry_run_val is not True:
        fatal(f"run_summary.json dry_run must be JSON boolean True, got {dry_run_val!r} ({type(dry_run_val).__name__})")

    # 5. failure_test must be JSON boolean False (string "false" rejected)
    fail_test_val = summary_data.get("failure_test")
    if fail_test_val is not False:
        fatal(f"run_summary.json failure_test must be JSON boolean False, got {fail_test_val!r} ({type(fail_test_val).__name__})")

    log("run_summary.json strict security contract verified OK.")

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
