from __future__ import annotations

from pathlib import Path

from apply_brand_protection import PROTECTION_BLOCK


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "methodology.html"
BUILT = ROOT / "dist" / "methodology.html"
ALLOWED_BUILD_INJECTION = (
    b'\n  <link rel="icon" href="/brand/coshuma-favicon.svg" '
    b'type="image/svg+xml" />\n'
    b'  <script defer src="/brand/brand-runtime.js"></script>'
)
ALLOWED_ORIGIN_PROTECTION = (PROTECTION_BLOCK + "\n").encode("utf-8")


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Authoritative methodology source is missing: {SOURCE}")
    if not BUILT.is_file():
        raise SystemExit(f"Built methodology page is missing: {BUILT}")
    source = SOURCE.read_bytes()
    built = BUILT.read_bytes()
    if built.count(ALLOWED_BUILD_INJECTION) != 1:
        raise SystemExit(
            "Final methodology page must contain exactly one allowlisted brand injection"
        )
    if built.count(ALLOWED_ORIGIN_PROTECTION) != 1:
        raise SystemExit(
            "Final methodology page must contain exactly one allowlisted origin-protection injection"
        )
    normalized = built.replace(ALLOWED_BUILD_INJECTION, b"", 1)
    normalized = normalized.replace(ALLOWED_ORIGIN_PROTECTION, b"", 1)
    if source != normalized:
        raise SystemExit(
            "Final dist/methodology.html must preserve public/methodology.html "
            "apart from the allowlisted brand and origin-protection injections"
        )
    print("Methodology source preserved in final dist")


if __name__ == "__main__":
    main()
