"""Fail closed on malformed public HTML table structure.

COSHUMA public pages are generated and normalized by several build stages. Internal-copy
sanitizers must never leave partial table rows behind. This validator treats table shape
as a production contract so a removed internal cell cannot silently become a broken row.

Usage:
    python scripts/validate_public_html_structure.py public
    python scripts/validate_public_html_structure.py dist
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import sys


class TableShapeParser(HTMLParser):
    def __init__(self, rel: str) -> None:
        super().__init__(convert_charrefs=True)
        self.rel = rel
        self.tables: list[dict] = []
        self.stack: list[dict] = []
        self.errors: list[str] = []

    @staticmethod
    def _positive_span(attrs, name: str) -> int:
        raw = dict(attrs).get(name, "1")
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return 1
        return value if value > 0 else 1

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "table":
            table = {"rows": [], "row": None, "rowspan": False, "line": self.getpos()[0]}
            self.stack.append(table)
            return
        if not self.stack:
            return
        table = self.stack[-1]
        if tag == "tr":
            if table["row"] is not None:
                self.errors.append(f"{self.rel}:{self.getpos()[0]}: nested/unclosed <tr>")
            table["row"] = {"width": 0, "cells": 0, "line": self.getpos()[0]}
            return
        if tag in {"td", "th"} and table["row"] is not None:
            table["row"]["cells"] += 1
            table["row"]["width"] += self._positive_span(attrs, "colspan")
            if self._positive_span(attrs, "rowspan") > 1:
                table["rowspan"] = True

    def handle_endtag(self, tag):
        tag = tag.lower()
        if not self.stack:
            return
        table = self.stack[-1]
        if tag == "tr":
            row = table["row"]
            if row is not None:
                table["rows"].append(row)
                table["row"] = None
            return
        if tag != "table":
            return

        if table["row"] is not None:
            table["rows"].append(table["row"])
            table["row"] = None
        self.stack.pop()
        self.tables.append(table)
        self._validate_table(table)

    def _validate_table(self, table: dict) -> None:
        rows = table["rows"]
        if not rows:
            return

        for row in rows:
            if row["cells"] == 0 or row["width"] == 0:
                self.errors.append(f"{self.rel}:{row['line']}: empty table row")
        if table["rowspan"]:
            return

        widths = [row["width"] for row in rows if row["width"] > 0]
        if len(widths) < 2:
            return
        counts = Counter(widths)
        expected = max(counts, key=lambda width: (counts[width], width))
        if expected <= 1:
            return
        for row in rows:
            if row["width"] > 0 and row["width"] != expected:
                self.errors.append(
                    f"{self.rel}:{row['line']}: table row width={row['width']} expected={expected}"
                )

    def close(self):
        super().close()
        if self.stack:
            for table in self.stack:
                self.errors.append(f"{self.rel}:{table['line']}: unclosed <table>")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target_arg = sys.argv[1] if len(sys.argv) > 1 else "public"
    target = Path(target_arg)
    if not target.is_absolute():
        target = root / target
    if not target.exists():
        raise SystemExit(f"Public HTML structure guard: missing {target}")

    files = sorted(target.rglob("*.html"))
    if not files:
        raise SystemExit(f"Public HTML structure guard: no HTML files under {target}")

    errors: list[str] = []
    tables = 0
    rows = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        parser = TableShapeParser(rel)
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        parser.close()
        tables += len(parser.tables)
        rows += sum(len(table["rows"]) for table in parser.tables)
        errors.extend(parser.errors)

    if errors:
        print("PUBLIC HTML STRUCTURE FAILED")
        for error in errors[:100]:
            print(f" - {error}")
        if len(errors) > 100:
            print(f" - ... and {len(errors) - 100} more")
        raise SystemExit(1)

    print(
        f"PASS: public HTML structure clean files={len(files)} tables={tables} rows={rows} "
        "malformed_table_rows=0"
    )


if __name__ == "__main__":
    main()
