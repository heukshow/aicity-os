"""Fail closed on malformed customer-facing HTML structures.

This guard is intentionally syntax/structure focused. Internal-policy guards handle
forbidden operations copy; this file prevents visually broken comparison tables from
shipping even when the text itself is otherwise allowed.

For each HTML table, all non-empty rows must have the same effective column width as
that table's first non-empty row. colspan is included in the effective width.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

TABLE_RE = re.compile(r"<table\b[^>]*>(.*?)</table\s*>", re.I | re.S)
ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr\s*>", re.I | re.S)
CELL_RE = re.compile(r"<t[dh]\b([^>]*)>", re.I | re.S)
COLSPAN_RE = re.compile(r"\bcolspan\s*=\s*[\"']?(\d+)", re.I)


def row_width(row: str) -> int:
    width = 0
    for attrs in CELL_RE.findall(row):
        m = COLSPAN_RE.search(attrs)
        width += int(m.group(1)) if m else 1
    return width


def scan_html(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for table_index, table_match in enumerate(TABLE_RE.finditer(raw), start=1):
        rows = ROW_RE.findall(table_match.group(1))
        widths = [(idx, row_width(row)) for idx, row in enumerate(rows, start=1)]
        non_empty = [(idx, width) for idx, width in widths if width > 0]
        if not non_empty:
            continue
        expected = non_empty[0][1]
        for row_index, width in non_empty[1:]:
            if width != expected:
                errors.append(
                    f"table {table_index} row {row_index}: effective columns={width}, expected={expected}"
                )
    return errors


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "public")
    if not root.exists():
        raise SystemExit(f"Markup integrity guard: missing {root}")
    files = sorted(root.rglob("*.html"))
    if not files:
        raise SystemExit(f"Markup integrity guard: no HTML files under {root}")

    errors: list[str] = []
    for path in files:
        for error in scan_html(path):
            errors.append(f"{path.relative_to(root).as_posix()}: {error}")

    if errors:
        print("ERROR: malformed public comparison/table markup detected.")
        for error in errors[:100]:
            print(f" - {error}")
        if len(errors) > 100:
            print(f" - ... and {len(errors)-100} more")
        raise SystemExit(1)

    print(f"PASS: public table structure consistent across {len(files)} HTML files")


if __name__ == "__main__":
    main()
