"""Repair and validate the known SaneBox FAQ JSON-LD regression.

The Sep 17 page-level disclosure cleanup removed only part of an affiliate FAQ
entry and left malformed structured data in the SaneBox buyer page. This pass
repairs only that known regression, preserves the exact customer tracking URL
and buyer claims, and prevents malformed SaneBox JSON-LD from shipping again.
"""
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DIST = ROOT / "dist"

JSONLD_RE = re.compile(
    r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S,
)

SANEBOX_FAQ = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "How much does SaneBox cost?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "SaneBox currently lists Snack at $4.54/month, Lunch at $7.46/month, and Dinner at $22.04/month when paid biyearly. Prices and billing options can change.",
            },
        },
        {
            "@type": "Question",
            "name": "How long is the SaneBox trial?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "SaneBox's current public pricing page shows a 7-day trial. The offer linked from this page currently states a 14-day trial for eligible referred customers, so confirm the trial length shown at the destination before signup.",
            },
        },
        {
            "@type": "Question",
            "name": "Is SaneBox worth it?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "SaneBox is a stronger fit when inbox prioritization, reminders, screening and digest workflows are the problem while you want to keep your existing email provider. It is not a substitute for an email-marketing platform used to manage subscriber lists and campaigns.",
            },
        },
    ],
}


def repair_sanebox() -> bool:
    path = PUBLIC / "tool" / "sanebox.html"
    if not path.exists():
        return False
    source = path.read_text(encoding="utf-8")
    changed = False

    def rewrite(match: re.Match[str]) -> str:
        nonlocal changed
        body = match.group(2).strip()
        if '"@type": "FAQPage"' not in body or "SaneBox" not in body:
            return match.group(0)
        try:
            json.loads(body)
            return match.group(0)
        except json.JSONDecodeError:
            changed = True
            payload = json.dumps(SANEBOX_FAQ, ensure_ascii=False, indent=2)
            return f'{match.group(1)}\n{payload}\n    {match.group(3)}'

    repaired = JSONLD_RE.sub(rewrite, source)
    if changed:
        path.write_text(repaired, encoding="utf-8")
    return changed


def validate_sanebox(path: Path) -> list[str]:
    if not path.exists():
        return []
    errors: list[str] = []
    source = path.read_text(encoding="utf-8")
    blocks = list(JSONLD_RE.finditer(source))
    if not blocks:
        return [f"{path.relative_to(ROOT).as_posix()}: no JSON-LD blocks found"]
    for index, match in enumerate(blocks, start=1):
        try:
            json.loads(match.group(2).strip())
        except json.JSONDecodeError as exc:
            rel = path.relative_to(ROOT).as_posix()
            errors.append(f"{rel} JSON-LD #{index}: {exc.msg} at line {exc.lineno} column {exc.colno}")
    return errors


def main() -> None:
    repaired = repair_sanebox()
    errors = validate_sanebox(PUBLIC / "tool" / "sanebox.html")
    if DIST.exists():
        errors.extend(validate_sanebox(DIST / "tool" / "sanebox.html"))
    if errors:
        raise SystemExit("Invalid SaneBox JSON-LD:\n- " + "\n- ".join(errors))
    print(f"SaneBox JSON-LD validation passed; repaired={str(repaired).lower()}")


if __name__ == "__main__":
    main()
