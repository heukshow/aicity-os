#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
import subprocess
import sys
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
        if x.get("lifecycle") == "production_verification_requested"
        and not x.get("blocker")
    ]
    return sorted(rows, key=lambda x: (
        PRIORITY.get(x.get("priority"), 99),
        x.get("last_evidence_at", ""),
        x.get("record_id", ""),
    ))


def validate_contract(registry, specs, strict=True):
    records = specs.get("records", {})
    active_ids = {x.get("record_id") for x in registry.get("active_queue", [])}
    errors = []
    if specs.get("schema_version") != 1:
        errors.append("release_verification_specs schema_version must be 1")
    for row in registry.get("active_queue", []):
        if row.get("lifecycle") == "production_verification_requested" and row.get("record_id") not in records:
            errors.append(f"missing deterministic spec: {row.get('record_id')}")

    required_by_mode = {
        "public_boundary": ("source_glob", "gh_pages_glob", "live_url", "forbidden_regex", "live_required_substrings"),
        "generated_json_state": ("producer", "checks"),
        "bundle_markers": ("source_file", "source_required_regex", "source_forbidden_regex", "gh_pages_glob", "gh_pages_required_regex", "gh_pages_forbidden_regex", "live_url"),
    }

    for record_id, spec in records.items():
        if record_id not in active_ids:
            errors.append(f"verification spec references non-active record: {record_id}")
        mode = spec.get("mode")
        if mode not in required_by_mode:
            errors.append(f"unsupported verification mode for {record_id}: {mode}")
            continue
        for field in required_by_mode[mode]:
            if field not in spec:
                errors.append(f"{record_id} missing verification field {field}")

        regex_fields = []
        if mode == "public_boundary":
            regex_fields = ["forbidden_regex"]
        elif mode == "bundle_markers":
            regex_fields = ["source_required_regex", "source_forbidden_regex", "gh_pages_required_regex", "gh_pages_forbidden_regex"]
        for field in regex_fields:
            for pat in spec.get(field, []):
                try:
                    re.compile(pat, re.I | re.S)
                except re.error as exc:
                    errors.append(f"{record_id} invalid regex {pat!r}: {exc}")

        if mode == "generated_json_state":
            if not isinstance(spec.get("producer"), list) or not spec.get("producer"):
                errors.append(f"{record_id} producer must be a non-empty argv list")
            for idx, check in enumerate(spec.get("checks", [])):
                if "file" not in check or "path" not in check or "equals" not in check:
                    errors.append(f"{record_id} checks[{idx}] requires file/path/equals")
                if not isinstance(check.get("path"), list):
                    errors.append(f"{record_id} checks[{idx}].path must be a list")

    if errors and strict:
        raise SystemExit("release-verifier contract FAIL:\n- " + "\n- ".join(errors))
    if errors:
        print("release-verifier contract FAIL: " + "; ".join(errors), file=sys.stderr)
    else:
        print(f"release-verifier contract PASS specs={len(records)} eligible={len(eligible_records(registry))}")
    return errors


def run(*args, check=True):
    p = subprocess.run(args, cwd=ROOT.parent.parent, text=True, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{p.stderr.strip()}")
    return p


def run_project(argv, check=True):
    p = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"project command failed: {' '.join(argv)}\n{p.stderr.strip()}")
    return p


def git_show(ref_path):
    return run("git", "show", ref_path).stdout


def gh_pages_files(pattern):
    p = run("git", "ls-tree", "-r", "--name-only", "origin/gh-pages")
    names = [x.strip() for x in p.stdout.splitlines() if x.strip()]
    regex = re.compile("^" + re.escape(pattern).replace(r"\*", ".*") + "$")
    return [x for x in names if regex.match(x)]


def scan_forbidden(label, text, patterns):
    hits = []
    for pat in patterns:
        m = re.search(pat, text, re.I | re.S)
        if m:
            hits.append(f"{label}: forbidden pattern {pat!r} matched {m.group(0)[:120]!r}")
    return hits


def scan_required(label, text, patterns):
    misses = []
    for pat in patterns:
        if not re.search(pat, text, re.I | re.S):
            misses.append(f"{label}: required pattern missing {pat!r}")
    return misses


def fetch_live(url):
    req = urllib.request.Request(url, headers={"User-Agent": "COSHUMA-Release-Verifier/1.1"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def deployed_source_sha():
    msg = run("git", "log", "-1", "--pretty=%B", "origin/gh-pages").stdout
    m = re.search(r"deploy: sync COSHUMA production bundle from ([0-9a-f]{40})", msg, re.I)
    return m.group(1) if m else None


def verify_deployed_ancestry(record, spec, failures, details):
    if not spec.get("verify_deployed_ancestry"):
        return
    merge = record.get("evidence", {}).get("merge_commit")
    deployed = deployed_source_sha()
    if not merge or not deployed:
        failures.append("could not establish merge/deployed source SHA ancestry")
        return
    p = run("git", "merge-base", "--is-ancestor", merge, deployed, check=False)
    if p.returncode != 0:
        failures.append(f"deployed source {deployed} does not contain target merge {merge}")
    else:
        details.append(f"deployed lineage: source `{deployed}` contains target merge `{merge}`")
    # gh-pages is a publication artifact, not proof that Pages has deployed it.
    # Require the exact artifact commit's successful deployment, then retain the
    # existing live HTTP/content checks. A pending deployment is retryable.
    pages_sha = run("git", "rev-parse", "origin/gh-pages").stdout.strip()
    runs = github_api("GET", f"/actions/runs?head_sha={pages_sha}&per_page=30",
                      os.environ.get("GITHUB_TOKEN", "")).get("workflow_runs", [])
    deployed_runs = [r for r in runs if r.get("name") == "pages build and deployment"
                     and r.get("head_sha") == pages_sha and r.get("status") == "completed"
                     and r.get("conclusion") == "success"]
    if not deployed_runs:
        failures.append(f"Pages deployment is not yet successful for artifact {pages_sha}; retry after deployment")
    else:
        details.append(f"Pages deployment: run `{deployed_runs[0]['id']}` succeeded for artifact `{pages_sha}`")


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
            "User-Agent": "COSHUMA-Release-Verifier/1.1",
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
            if (
                marker in body
                and "RELEASE_VERIFICATION" in body
                and "result: `production_verified`" in body
                and (not merge or merge in body)
            ):
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
        f"- verification_run: `{os.environ.get('GITHUB_RUN_ID', 'local')}`",
        "- verifier: deterministic GitHub Actions control-plane release verifier",
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
        failures.extend(scan_forbidden(f"source:{Path(path).name}", text, forbidden))
    details.append(f"source recurrence scan: {len(source_paths)} files checked")

    gh_paths = gh_pages_files(spec["gh_pages_glob"])
    if not gh_paths:
        failures.append(f"gh-pages glob matched no files: {spec['gh_pages_glob']}")
    for path in gh_paths:
        failures.extend(scan_forbidden(f"gh-pages:{path}", git_show(f"origin/gh-pages:{path}"), forbidden))
    details.append(f"gh-pages recurrence scan: {len(gh_paths)} files checked")

    verify_deployed_ancestry(record, spec, failures, details)

    try:
        status, live = fetch_live(spec["live_url"])
        details.append(f"live HTTP: {status} `{spec['live_url']}`")
        if status != 200:
            failures.append(f"live HTTP status was {status}")
        failures.extend(scan_forbidden("live", live, forbidden))
        for required in spec.get("live_required_substrings", []):
            if required not in live:
                failures.append(f"live required substring missing: {required!r}")
        if not failures:
            details.append("public-boundary forbidden patterns absent; required customer-facing markers present")
    except Exception as exc:
        failures.append(f"live fetch failed: {type(exc).__name__}: {exc}")

    return failures, details


def select_json_value(data, check):
    current = data
    finder = check.get("find")
    if finder is not None:
        if not isinstance(current, list):
            raise ValueError("find requires a top-level list")
        matches = [row for row in current if isinstance(row, dict) and all(row.get(k) == v for k, v in finder.items())]
        if len(matches) != 1:
            raise ValueError(f"find {finder!r} matched {len(matches)} rows")
        current = matches[0]
    for part in check.get("path", []):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and isinstance(part, int) and 0 <= part < len(current):
            current = current[part]
        else:
            raise ValueError(f"path component {part!r} not found")
    return current


def verify_generated_json_state(record, spec):
    failures = []
    details = []
    try:
        producer = spec.get("producer", [])
        p = run_project(producer)
        details.append(f"producer executed successfully: `{' '.join(producer)}`")
        if p.stdout.strip():
            details.append(f"producer output: {p.stdout.strip()[:200]}")
    except Exception as exc:
        failures.append(f"producer execution failed: {type(exc).__name__}: {exc}")
        return failures, details

    for check in spec.get("checks", []):
        path = ROOT / check["file"]
        try:
            data = load_json(path)
            actual = select_json_value(data, check)
            expected = check.get("equals")
            if actual != expected:
                failures.append(f"{check['file']} {check.get('find', '')} path {check['path']} expected {expected!r}, got {actual!r}")
            else:
                details.append(f"generated state verified: `{check['file']}` path `{'.'.join(map(str, check['path']))}`")
        except Exception as exc:
            failures.append(f"generated state check failed for {check['file']}: {type(exc).__name__}: {exc}")

    verify_deployed_ancestry(record, spec, failures, details)
    if not failures:
        details.append("generated lifecycle remains canonical after producer execution; stale state did not reappear")
    return failures, details


def verify_bundle_markers(record, spec):
    failures = []
    details = []
    source_path = ROOT / spec["source_file"]
    if not source_path.exists():
        failures.append(f"source file missing: {spec['source_file']}")
    else:
        source = source_path.read_text(encoding="utf-8", errors="replace")
        failures.extend(scan_required("source", source, spec.get("source_required_regex", [])))
        failures.extend(scan_forbidden("source", source, spec.get("source_forbidden_regex", [])))
        details.append(f"source marker scan: `{spec['source_file']}`")

    gh_paths = gh_pages_files(spec["gh_pages_glob"])
    if not gh_paths:
        failures.append(f"gh-pages glob matched no files: {spec['gh_pages_glob']}")
    else:
        texts = [git_show(f"origin/gh-pages:{path}") for path in gh_paths]
        joined = "\n".join(texts)
        failures.extend(scan_required("gh-pages bundle", joined, spec.get("gh_pages_required_regex", [])))
        failures.extend(scan_forbidden("gh-pages bundle", joined, spec.get("gh_pages_forbidden_regex", [])))
        details.append(f"gh-pages bundle marker scan: {len(gh_paths)} files checked")

    verify_deployed_ancestry(record, spec, failures, details)
    try:
        status, live = fetch_live(spec["live_url"])
        details.append(f"live HTTP: {status} `{spec['live_url']}`")
        if status != 200:
            failures.append(f"live HTTP status was {status}")
        # HTTP 200 alone does not establish that the deployed JS reached customers.
        for marker in spec.get("live_required_substrings", []):
            if marker not in live:
                failures.append(f"live page missing required marker: {marker}")
        failures.extend(scan_forbidden("live page", live, spec.get("live_forbidden_regex", [])))
        cursor = 0
        for marker in spec.get("live_ordered_substrings", []):
            position = live.find(marker, cursor)
            if position < 0:
                failures.append(f"live page missing ordered marker: {marker}")
                break
            cursor = position + len(marker)
        if spec["gh_pages_glob"].endswith(".js"):
            from urllib.parse import urljoin, urlparse
            refs = re.findall(r'''(?:src|href)=["']([^"']+\.js(?:\?[^"']*)?)["']''', live)
            asset_texts = []
            for ref in refs:
                url = urljoin(spec["live_url"], ref)
                if urlparse(url).netloc != urlparse(spec["live_url"]).netloc:
                    continue
                asset_status, asset = fetch_live(url)
                if asset_status != 200:
                    failures.append(f"live asset HTTP {asset_status}")
                asset_texts.append(asset)
            live = "\n".join(asset_texts)
        failures.extend(scan_required("live content", live, spec.get("gh_pages_required_regex", [])))
        failures.extend(scan_forbidden("live content", live, spec.get("gh_pages_forbidden_regex", [])))
    except Exception as exc:
        failures.append(f"live fetch failed: {type(exc).__name__}: {exc}")

    if not failures:
        details.append("successful-copy measurement markers are present in source and deployed bundle with required bounded parameters")
    return failures, details


def verify_record(record, spec):
    mode = spec.get("mode")
    if mode == "public_boundary":
        return verify_public_boundary(record, spec)
    if mode == "generated_json_state":
        return verify_generated_json_state(record, spec)
    if mode == "bundle_markers":
        return verify_bundle_markers(record, spec)
    return [f"unsupported verification mode: {mode}"], []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    registry = load_json(REGISTRY_PATH)
    specs = load_json(SPECS_PATH)
    contract_errors = validate_contract(registry, specs, strict=args.validate_only)
    if args.validate_only:
        return 1 if contract_errors else 0

    candidates = eligible_records(registry)
    if not candidates:
        print("release-verifier: no release candidate")
        return 1 if contract_errors else 0

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required outside --validate-only")

    failed = bool(contract_errors)
    for record in candidates:
        spec = specs.get("records", {}).get(record["record_id"])
        try:
            if has_existing_result(record, token):
                print(f"release-verifier: existing production evidence: {record['record_id']}")
                continue
            if not spec:
                failures, details = ["missing deterministic spec; next_owner=Operations Governance Team"], []
            else:
                failures, details = verify_record(record, spec)
            result = "verification_failed" if failures else "production_verified"
            details.extend([f"failure: {x}" for x in failures])
            post_result(record, result, details, token)
            failed |= bool(failures)
            print(f"release-verifier: {record['record_id']} {result}")
        except Exception as exc:
            failed = True
            print(f"release-verifier: {record['record_id']} failed: {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
