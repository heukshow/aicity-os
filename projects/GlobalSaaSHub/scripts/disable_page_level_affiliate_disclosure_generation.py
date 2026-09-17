"""Disable page-level affiliate disclosure generation at the source.

COSHUMA policy: the general affiliate disclosure belongs on the homepage only.
Individual tool/compare/best/category pages must never generate their own general
commission/disclosure notice. This script rewrites only generator source code in
the CI/worktree before those generators run, preserving affiliate URLs, CTA
attributes, rel=sponsored, analytics, and the dedicated disclosure policy page.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def patch_guard_public_copy() -> int:
    path = ROOT / "scripts" / "guard_public_copy.py"
    text = path.read_text(encoding="utf-8")
    before = text

    # Remove the reusable disclosure payload completely.
    text = re.sub(
        r"\nSTANDARD_AFFILIATE_DISCLOSURE = \(.*?\n\)\n",
        "\n",
        text,
        flags=re.S,
    )

    # normalize_affiliate_disclosure is cleanup-only: it may remove legacy
    # notices but must never insert a new notice after an affiliate CTA.
    text = text.replace("    has_affiliate = 'data-cta=\"affiliate\"' in text\n", "")
    text = text.replace(
        "    if not has_affiliate:\n        return text\n    text = re.sub(r'(<a\\b[^>]*data-cta=\"affiliate\"[^>]*>.*?</a>)', r'\\1\\n' + STANDARD_AFFILIATE_DISCLOSURE, text, count=1, flags=re.S)\n    return remove_empty_disclosure_sections(text)\n",
        "    return remove_empty_disclosure_sections(text)\n",
    )

    if text != before:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0


def patch_polish_public_copy() -> int:
    path = ROOT / "scripts" / "polish_public_copy.py"
    text = path.read_text(encoding="utf-8")
    before = text

    # No comparison-level disclosure constant or insertion helper.
    text = re.sub(
        r"\nCOMPARE_AFFILIATE_DISCLOSURE = \(.*?\n\)\n",
        "\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\ndef tag_existing_compare_disclosure\(.*?\n(?=def ensure_tool_revenue_alternative)",
        "\n",
        text,
        flags=re.S,
    )

    # Remove the disclosure paragraph embedded in revenue-alternative sections.
    text = re.sub(
        r"\n\s*'        <p class=\"text-\[10px\] text-slate-500\">Affiliate disclosure:.*?</p>\\n'",
        "",
        text,
        flags=re.S,
    )

    # Comparison processing still monetizes approved URLs, but never adds a
    # page-level disclosure.
    text = text.replace(
        "            if folder.name == \"compare\":\n                updated = monetize_verified_compare_links(updated)\n                updated = ensure_compare_affiliate_disclosure(updated)\n",
        "            if folder.name == \"compare\":\n                updated = monetize_verified_compare_links(updated)\n",
    )

    if text != before:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0


def main() -> None:
    changed = patch_guard_public_copy() + patch_polish_public_copy()
    print(f"Page-level affiliate disclosure generators disabled: files_changed={changed}")


if __name__ == "__main__":
    main()
