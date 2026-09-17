"""Sanitize the built Vite output after config-time generators have finished.

Vite imports project config modules during the build, and some of those modules
write public buyer pages. That means a source-only cleanup can be reintroduced
during `vite build`. This pass runs against `dist/` immediately before public-copy
tests and deployment.
"""
from pathlib import Path
from guard_customer_only_copy import clean_html, clean_public_js, clean_llms

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main() -> None:
    if not DIST.exists():
        raise RuntimeError("dist/ does not exist; run vite build first")

    changed = []
    for path in DIST.rglob("*.html"):
        before = path.read_text(encoding="utf-8")
        after = clean_html(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(path.relative_to(DIST).as_posix())

    js = DIST / "affiliate-attribution.js"
    if js.exists():
        before = js.read_text(encoding="utf-8")
        after = clean_public_js(before)
        if after != before:
            js.write_text(after, encoding="utf-8")
            changed.append(js.relative_to(DIST).as_posix())

    llms = DIST / "llms.txt"
    if llms.exists():
        before = llms.read_text(encoding="utf-8")
        after = clean_llms(before)
        if after != before:
            llms.write_text(after, encoding="utf-8")
            changed.append(llms.relative_to(DIST).as_posix())

    print(f"Built customer-only copy guard: {len(changed)} files normalized")


if __name__ == "__main__":
    main()
