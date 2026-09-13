from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DIST = ROOT / "dist"

FORBIDDEN_FILENAMES = {
    ".env", ".env.local", ".env.production", "credentials.json", "client_secret.json",
    "token.json", "token.pickle", "google_token.pickle", "id_rsa", "id_ed25519",
}
FORBIDDEN_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}
PUBLIC_PRIVATE_MARKERS = [
    "websilonsg@gmail.com",
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "PAYPAL_CLIENT_SECRET=",
    "YOUTUBE_CLIENT_SECRET=",
    "YOUTUBE_REFRESH_TOKEN=",
]
SECRET_ASSIGNMENT = re.compile(
    r"(?i)(client_secret|api_secret|refresh_token|private_key|access_token|password)"
    r"\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)


def walk_files(base: Path):
    if not base.exists():
        return
    for path in base.rglob("*"):
        if path.is_file():
            yield path


def main() -> None:
    errors = []

    # COSHUMA must not track credential-shaped files anywhere in its own project.
    # Scope this check to GlobalSaaSHub so unrelated repository projects cannot
    # break the COSHUMA production pipeline because of their own fixtures/assets.
    for path in walk_files(ROOT):
        rel = path.relative_to(ROOT)
        if any(part in {"node_modules", ".git", "dist"} for part in rel.parts):
            continue
        if path.name in FORBIDDEN_FILENAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"credential-shaped file must not be tracked in COSHUMA: {rel}")

    # Public output receives stricter content checks. Environment-variable names
    # are allowed in server/source code, but values/assignments and private account
    # addresses must never reach public/ or the built production bundle.
    for base in (PUBLIC, DIST):
        for path in walk_files(base):
            if path.suffix.lower() not in {".html", ".js", ".json", ".txt", ".xml", ".css"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for marker in PUBLIC_PRIVATE_MARKERS:
                if marker.lower() in text.lower():
                    errors.append(f"public bundle contains forbidden marker {marker!r}: {path.relative_to(ROOT)}")
            if SECRET_ASSIGNMENT.search(text):
                errors.append(f"public bundle contains secret-like literal assignment: {path.relative_to(ROOT)}")

    if errors:
        print("SECURITY GUARD: FAIL")
        for error in sorted(set(errors)):
            print(f" - {error}")
        raise SystemExit(1)

    print("SECURITY GUARD: PASS — COSHUMA contains no tracked credential-shaped files or public secret markers")


if __name__ == "__main__":
    main()
