"""Fail closed when internal affiliate state enters customer-facing frontend source.

The browser app may consume only generated/public-tools.json, which is built from an
explicit allowlist. Internal repository data and evidence files are never imported by
src/.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

FORBIDDEN = {
    "raw-tool-data-import": re.compile(r"(?:\.\./|/)data/tools(?:\.next)?\.json", re.I),
    "affiliate-verified-state": re.compile(r"\baffiliate_verified\b", re.I),
    "affiliate-status-state": re.compile(r"\baffiliate_status\b", re.I),
    "affiliate-evidence-state": re.compile(r"\baffiliate_evidence(?:_markers)?\b", re.I),
    "affiliate-next-action": re.compile(r"\baffiliate_next_action\b", re.I),
    "application-state": re.compile(r"\bapplication_state\b", re.I),
    "revenue-truth": re.compile(r"\brevenue[_ -]?truth\b", re.I),
    "partnerstack-name": re.compile(r"\bPartnerStack\b", re.I),
    "firstpromoter-name": re.compile(r"\bFirstPromoter\b", re.I),
}

ALLOWED_GENERATED_KEYS = {
    "id", "name", "category", "category_display", "description", "pricing",
    "key_features", "rating", "rating_source_url", "logo_url", "primary_category",
    "comparison_group", "official_url", "pricing_source_url", "pricing_verified_at",
    "pricing_verified", "currency", "billing_period", "outbound_url", "is_sponsored",
}

errors = []
for path in SRC.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in {".js", ".jsx", ".json"}:
        continue
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    for label, pattern in FORBIDDEN.items():
        m = pattern.search(text)
        if m:
            errors.append(f"{rel}: {label}: {m.group(0)}")

public_json = SRC / "generated" / "public-tools.json"
if not public_json.exists():
    errors.append("src/generated/public-tools.json: missing generated customer-only dataset")
else:
    import json
    data = json.loads(public_json.read_text(encoding="utf-8"))
    for idx, tool in enumerate(data):
        extra = sorted(set(tool) - ALLOWED_GENERATED_KEYS)
        if extra:
            errors.append(f"src/generated/public-tools.json[{idx}]: non-allowlisted keys: {extra}")

if errors:
    raise SystemExit("Public source boundary violation:\n" + "\n".join(errors[:100]))

print("PASS: frontend source boundary is private-by-default; raw affiliate state imports=0")
