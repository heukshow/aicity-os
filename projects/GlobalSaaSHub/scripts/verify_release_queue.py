#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "operations_registry.json"
SPECS_PATH = ROOT / "data" / "release_verification_specs.json"
PRIORITY = {"critical": 0, "high": 1, "normal": 2, "low": 3}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def eligible_records(registry):
    rows = [
        x for x in registry.get("active_queue", [])
        if x.get("next_owner") == "Release & Reliability Team"
        and x.get("lifecycle") == "production_verification_requested"
    ]
    return sorted(rows, key=lambda x: (
        PRIORITY.get(x.get("priority"), 99),
        x.get("last_evidence_at", ""),
        x.get("record_id", ""),
    ))


def validate_contract(registry, specs):
    records = specs.get("records", {})
    active_ids = {x.get("record_id") for x in registry.get("active_queue", [])}
    errors = []
    if specs.get("schema_version") != 1:
        errors.append("release_verification_specs schema_version must be 1")
    for record_id, spec in records.items():
        if record_id not in active_ids:
            errors.append(f"verification spec references non-active record: {record_id}")
        if spec.get("mode") != "public_boundary":
            errors.append(f"unsupported verification mode for {record_id}: {spec.get('mode')}")
        for field in ("source_glob", "gh_pages_glob", "live_url", "forbidden_regex", "live_required_substrings"):
            if field not in spec:
                errors.append(f"{record_id} missing verification field {field}")
        for pat in spec.get("forbidden_regex", []):
            try:
                re.compile(pat, re.I)
            except re.error as exc:
                errors.append(f"{record_id} invalid regex {pat!r}: {exc}")
    if errors:
        raise SystemExit("release-verifier contract FAIL:\n- " + "\n- ".join(errors))
    print(f"release-verifier contract PASS specs={len(records)} eligible={len(eligible_records(registry))}")


def run(*args, check=True):
    p = subprocess.run(args, cwd=ROOT.parent.parent, text=True, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{p.stderr.strip()}")
    return p


def git_show(ref_path):
    p = run("git", "show", ref_path)
    return p.stdout


def gh_pages_files(pattern):
    p = run("git", "ls-tree", "-r", "--name-only", "origin/gh-pages")
    names = [x.strip() for x in p.stdout.splitlines() if x.strip()]
    regex = re.compile("^" + re.escape(pattern).replace(r"\*", ".*") + "$")
    return [x for x in names if regex.match(x)]


def scan_text(label, text, forbidden):
    hits = []
    for pat in forbidden:
        m = re.search(pat, text, re.I)
        if m:
            hits.append(f"{label}: forbidden pattern {pat!r} matched {m.group(0)[:120]!r}")
    return hits


def fetch_live(url):
    req = urllib.request.Request(url, headers={"User-Agent": "COSHUMA-Release-Verifier/1.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, body


def deployed_source_sha():
    msg = run("git", "log", "-1", "--pretty=%B", "origin/gh-pages").stdout
    m = re.search(r"deploy: sync COSHUMA production bundle from ([0-9a-f]{40})", msg, re.I)
    return m.group(1) if m else None


def github_api(method, path, token, payload=None):
    repo = os.environ.get("GITHUB_REPOSITORY", "heukshow/aicity-os")
    url = f"https://api.github.com/repos/{repo}{path}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "COSHUMA-Release-Verifier/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def has_existing_result(record, token, issue_number=292):
    page = 1
    marker = f"record_id: `{record['record_id']}`"
    merge = record.get("evidence", {}).get("merge_commit")
    while True:
        rows = github_api("GET", f"/issues/{issue_number}/comments?per_page=100&page={page}", token)
        if not rows:
            return False
        for row in rows:
            body = row.get("body", "")
            if marker in body and "RELEASE_VERIFICATION" in body and (not merge or merge in body):
                return True
        page += 1


def post_result(record, result, details, token, issue_number=292):
    evidence = record.get("evidence", {})
    lines = [
        "### RELEASE_VERIFICATION — deterministic control-plane",
        f"- record_id: `{record['record_id']}`",
        f"- task_key: `{record['task_key']}`",
        f"- incident_key: `{record.get('incident_key')}`",
        f"- merge: `{evidence.get('merge_commit')}`",
        f"- implementation_pr: `{evidence.get('implementation_pr')}`",
    ]
    for detail in details:
        lines.append(f"- {detail}")
    lines += [
        f"- result: `{result}`",
        "- verifier: deterministic GitHub Actions fallback for public production checks",
        "- next_owner: Operations Governance Team — synchronize the canonical operations registry from this evidence.",
    ]
    github_api("POST", f"/issues/{issue_number}/comments", token, {"body": "\n".join(lines)})


def verify_public_boundary(record, spec):
    failures = []
    details = []
    forbidden = spec.get("forbidden_regex", [])

    source_paths = sorted(glob.glob(str(ROOT.parent.parent / spec["source_glob"])))
    if not source_paths:
        failures.append(f"source glob matched no files: {spec['source_glob']}")
    for path in source_paths:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        failures.extend(scan_text(f"source:{Path(path).name}", text, forbidden))
    details.append(f"source recurrence scan: {len(source_paths)} files checked")

    gh_paths = gh_pages_files(spec["gh_pages_glob"])
    if not gh_paths:
        failures.append(f"gh-pages glob matched no files: {spec['gh_pages_glob']}")
    for path in gh_paths:
        text = git_show(f"origin/gh-pages:{path}")
        failures.extend(scan_text(f"gh-pages:{path}", text, forbidden))
    details.append(f"gh-pages recurrence scan: {len(gh_paths)} files checked")

    merge = record.get("evidence", {}).get("merge_commit")
    deployed = deployed_source_sha()
    if spec.get("verify_deployed_ancestry"):
        if not merge or not deployed:
            failures.append("could not establish merge/deployed source SHA ancestry")
        else:
            p = run("git", "merge-base", "--is-ancestor", merge, deployed, check=False)
            if p.returncode != 0:
                failures.append(f"deployed source {deployed} does not contain target merge {merge}")
            else:
                details.append(f"deployed lineage: source `{deployed}` contains target merge `{merge}`")

    try:
        status, live = fetch_live(spec["live_url"])
        details.append(f"live HTTP: {status} `{spec['live_url']}`")
        if status != 200:
            failures.append(f"live HTTP status was {status}")
        failures.extend(scan_text("live", live, forbidden))
        for required in spec.get("live_required_substrings", []):
            if required not in live:
                failures.append(f"live required substring missing: {required!r}")
        if not failures:
            details.append("public-boundary forbidden patterns absent; required customer-facing markers present")
    except Exception as exc:
        failures.append(f"live fetch failed: {type(exc).__name__}: {exc}")

    return failures, details


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    registry = load_json(REGISTRY_PATH)
    specs = load_json(SPECS_PATH)
    validate_contract(registry, specs)
    if args.validate_only:
        return 0

    candidates = eligible_records(registry)
    configured = [(x, specs.get("records", {}).get(x["record_id"])) for x in candidates]
    configured = [(x, spec) for x, spec in configured if spec]
    if not configured:
        print("release-verifier: no deterministic public verification candidate")
        return 0

    record, spec = configured[0]
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required outside --validate-only")

    if has_existing_result(record, token):
        print(f"release-verifier: existing result found for {record['record_id']}; skipping")
        return 0

    failures, details = verify_public_boundary(record, spec)
    if failures:
        details.extend([f"failure: {x}" for x in failures])
        post_result(record, "verification_failed", details, token)
        print("release-verifier: verification_failed")
        return 1

    post_result(record, "production_verified", details, token)
    print("release-verifier: production_verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
