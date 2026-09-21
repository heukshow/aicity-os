"""Fail closed when any public HTML file contains malformed JSON-LD.

This validator intentionally does not repair files during the build. A build-time
self-heal can make the deploy artifact look valid while leaving broken committed
source ready to be copied back by a later content edit. Source must be valid before
Vite runs, and the built artifact is validated again after Vite.
"""
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DIST = ROOT / "dist"

JSONLD_OPEN_RE = re.compile(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>', re.I
)
JSONLD_RE = re.compile(
    r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S,
)


def validate_tree(root: Path) -> list[str]:
    if not root.exists():
        return []
    errors: list[str] = []
    for path in root.rglob("*.html"):
        source = path.read_text(encoding="utf-8", errors="replace")
        open_count = len(JSONLD_OPEN_RE.findall(source))
        blocks = list(JSONLD_RE.finditer(source))
        rel = path.relative_to(ROOT).as_posix()
        if open_count != len(blocks):
            errors.append(
                f"{rel}: JSON-LD script count mismatch "
                f"(opened={open_count}, closed={len(blocks)})"
            )
        for index, match in enumerate(blocks, start=1):
            try:
                payload = json.loads(match.group(2).strip())
            except json.JSONDecodeError as exc:
                errors.append(
                    f"{rel}: JSON-LD #{index}: {exc.msg} "
                    f"at line {exc.lineno} column {exc.colno}"
                )
                continue

            stack = [payload]
            while stack:
                node = stack.pop()
                if isinstance(node, list):
                    stack.extend(node)
                    continue
                if not isinstance(node, dict):
                    continue
                stack.extend(node.values())
                if node.get("@type") != "FAQPage":
                    continue
                seen: set[str] = set()
                for question in node.get("mainEntity", []):
                    if not isinstance(question, dict):
                        continue
                    name = question.get("name")
                    if not isinstance(name, str):
                        continue
                    normalized = " ".join(name.split()).casefold()
                    if normalized in seen:
                        errors.append(
                            f'{rel}: JSON-LD #{index}: duplicate FAQ question "{name}"'
                        )
                    seen.add(normalized)
    return errors


def main() -> None:
    errors = validate_tree(PUBLIC)
    if DIST.exists():
        errors.extend(validate_tree(DIST))
    if errors:
        raise SystemExit("Invalid public JSON-LD:\n- " + "\n- ".join(errors))
    print("Public JSON-LD validation passed")


if __name__ == "__main__":
    main()
