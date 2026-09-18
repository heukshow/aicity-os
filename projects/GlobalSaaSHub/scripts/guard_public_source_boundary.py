"""Fail closed when internal affiliate state enters customer-facing frontend source.

The browser app consumes only generated/public-tools.json, built from an explicit
allowlist. Internal repository data and evidence files are never imported by src/.
Files under public/ are customer surfaces and must not carry partner correspondence,
network names, verification mechanics or affiliate status labels. Tracking URLs may
contain network domains; URL values are treated as routing data, not explanatory copy.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PUBLIC = ROOT / "public"
TEXT_EXTENSIONS = {".html", ".txt", ".xml", ".json", ".js", ".webmanifest"}
URL = re.compile(r"https?://[^\s\"'<>]+", re.I)

FORBIDDEN_SOURCE = {
    "raw-tool-data-import": re.compile(r"(?:\.\./|/)data/tools(?:\.next)?\.json", re.I),
    "affiliate-verified-state": re.compile(r"\baffiliate_verified\b", re.I),
    "affiliate-status-state": re.compile(r"\baffiliate_status\b", re.I),
    "affiliate-evidence-state": re.compile(r"\baffiliate_evidence(?:_markers)?\b", re.I),
    "affiliate-next-action": re.compile(r"\baffiliate_next_action\b", re.I),
    "application-state": re.compile(r"\bapplication_state\b", re.I),
    "revenue-truth": re.compile(r"\brevenue[_ -]?truth\b", re.I),
    "partnerstack-name": re.compile(r"\bPartnerStack\b", re.I),
    "firstpromoter-name": re.compile(r"\bFirstPromoter\b", re.I),
    "partner-correspondence": re.compile(
        r"\b(?:affiliate|partner)\s+(?:team|manager)\b[^\n<>]{0,120}\b(?:message|email|reply|told|confirmed|supplied|reconfirmed)\b"
        r"|\b(?:message|email|reply)\b[^\n<>]{0,120}\b(?:affiliate|partner)\s+(?:team|manager)\b"
        r"|\bfirst-party\s+reporting\s+(?:verifies|confirms)\b",
        re.I,
    ),
}

FORBIDDEN_PUBLIC_COPY = {
    "partnerstack-name": re.compile(r"\bPartnerStack\b", re.I),
    "firstpromoter-name": re.compile(r"\bFirstPromoter\b", re.I),
    "public-partner-status": re.compile(
        r"\bverified\s+(?:partner|affiliate|referral|tracking)\b"
        r"|\bverified\s+link\b",
        re.I,
    ),
    "internal-state-language": re.compile(
        r"\b(?:approved_tracking|affiliate_verified|affiliate_status|affiliate_evidence|"
        r"application_state|revenue[_ -]?truth|browser[_ -]?queue|verified customer-facing|"
        r"partner-side evidence|verification evidence)\b",
        re.I,
    ),
}

ALLOWED_GENERATED_KEYS = {
    "id", "name", "category", "category_display", "description", "pricing",
    "key_features", "rating", "rating_source_url", "logo_url", "primary_category",
    "comparison_group", "official_url", "pricing_source_url", "pricing_verified_at",
    "pricing_verified", "currency", "billing_period", "outbound_url", "is_sponsored",
}
URL_FIELDS = {"outbound_url", "official_url", "pricing_source_url", "rating_source_url", "logo_url"}


def mask_urls(text: str) -> str:
    return URL.sub("https://PUBLIC-OUTBOUND-URL", text)


errors = []

# React/browser source must never import or serialize raw internal state.
for path in SRC.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in {".js", ".jsx"}:
        continue
    text = mask_urls(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT).as_posix()
    for label, pattern in FORBIDDEN_SOURCE.items():
        m = pattern.search(text)
        if m:
            errors.append(f"{rel}: {label}: {m.group(0)}")

# public/ is copied into the customer bundle. Scan every public text surface after
# the sanitizer so a new generator cannot silently reintroduce internal status copy.
public_patterns = {**FORBIDDEN_SOURCE, **FORBIDDEN_PUBLIC_COPY}
for path in PUBLIC.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
        continue
    try:
        text = mask_urls(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        continue
    rel = path.relative_to(ROOT).as_posix()
    for label, pattern in public_patterns.items():
        m = pattern.search(text)
        if m:
            errors.append(f"{rel}: {label}: {m.group(0)}")

public_json = SRC / "generated" / "public-tools.json"
if not public_json.exists():
    errors.append("src/generated/public-tools.json: missing generated customer-only dataset")
else:
    data = json.loads(public_json.read_text(encoding="utf-8"))
    for idx, tool in enumerate(data):
        extra = sorted(set(tool) - ALLOWED_GENERATED_KEYS)
        if extra:
            errors.append(f"src/generated/public-tools.json[{idx}]: non-allowlisted keys: {extra}")
        for key, value in tool.items():
            if key in URL_FIELDS or value is None:
                continue
            values = value if isinstance(value, list) else [value]
            for item in values:
                if not isinstance(item, str):
                    continue
                for label, pattern in FORBIDDEN_PUBLIC_COPY.items():
                    m = pattern.search(item)
                    if m:
                        errors.append(
                            f"src/generated/public-tools.json[{idx}].{key}: {label}: {m.group(0)}"
                        )

if errors:
    raise SystemExit("Public source boundary violation:\n" + "\n".join(errors[:100]))

print("PASS: frontend source boundary is private-by-default; raw affiliate state imports=0; public text ops/status leaks=0")
