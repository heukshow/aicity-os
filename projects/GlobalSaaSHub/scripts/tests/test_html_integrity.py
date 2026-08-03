"""Strict UTF-8 and structural audit for generated GlobalSaaSHub HTML."""
import sys
from html.parser import HTMLParser
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PUBLIC = PROJECT / "public"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
CORRUPTION = ("??", "狩?", "?뽳툘", "?몟", "?좑툘", "?룇", "?쭬", "\ufffd", "<span>??/span>")


class StrictHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        return

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"unexpected </{tag}>")
            return
        if self.stack[-1] != tag:
            self.errors.append(f"expected </{self.stack[-1]}>, got </{tag}>")
            return
        self.stack.pop()

    def close(self):
        super().close()
        if self.stack:
            self.errors.append("unclosed: " + ", ".join(self.stack))


def main():
    files = sorted((PUBLIC / "tool").glob("*.html")) + sorted((PUBLIC / "compare").glob("*.html"))
    errors = []
    if len(files) != 381:
        errors.append(f"generated HTML count is {len(files)}, expected 381")
    for path in files:
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"BOM: {path.relative_to(PUBLIC)}")
        try:
            html = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            errors.append(f"UTF-8 decode: {path.relative_to(PUBLIC)}: {exc}")
            continue
        for marker in CORRUPTION:
            if marker in html:
                errors.append(f"corruption {marker!r}: {path.relative_to(PUBLIC)}")
        parser = StrictHTMLParser()
        try:
            parser.feed(html)
            parser.close()
        except Exception as exc:
            errors.append(f"parse: {path.relative_to(PUBLIC)}: {exc}")
        errors.extend(f"HTML {path.relative_to(PUBLIC)}: {error}" for error in parser.errors)
    if errors:
        print(f"HTML INTEGRITY: FAIL ({len(errors)} errors)")
        for error in errors[:50]:
            print(f"- {error}")
        return 1
    print(f"HTML INTEGRITY: PASS ({len(files)} files; UTF-8/BOM/corruption/tag errors: 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
