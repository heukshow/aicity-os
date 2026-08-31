#!/usr/bin/env python3
"""Fail closed if Korean text is introduced into the GlobalSaaSHub public site.

GlobalSaaSHub targets a global English-speaking audience. This guard scans the
user-facing source/data files and generated public pages that can put text in a
visitor's browser. It intentionally does not scan internal documentation or
operational notes.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANGUL = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣ]")


def iter_targets():
    fixed = [ROOT / "index.html", ROOT / "data" / "tools.json"]
    for path in fixed:
        if path.exists():
            yield path

    for base, patterns in (
        (ROOT / "src", ("*.js", "*.jsx", "*.ts", "*.tsx", "*.html")),
        (ROOT / "public", ("*.html", "*.xml", "*.txt")),
    ):
        if not base.exists():
            continue
        for pattern in patterns:
            yield from base.rglob(pattern)


def main() -> int:
    failures = []
    seen = set()

    for path in iter_targets():
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)

        text = path.read_text(encoding="utf-8", errors="strict")
        for line_no, line in enumerate(text.splitlines(), 1):
            match = HANGUL.search(line)
            if match:
                snippet = line.strip()
                if len(snippet) > 180:
                    snippet = snippet[:177] + "..."
                failures.append(
                    f"{path.relative_to(ROOT)}:{line_no}: Hangul detected: {snippet}"
                )

    if failures:
        print("FAIL: GlobalSaaSHub must remain English-only in user-facing files.")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PASS: English-only guard checked {len(seen)} user-facing files; no Hangul detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
