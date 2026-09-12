"""Surface the verified-offers buyer hub from COSHUMA's homepage.

The production buyer hub now contains many vendor-verified customer routes, but the
hydrated homepage does not give visitors a direct path into it. This patch adds one
prominent internal CTA to the React homepage plus one crawler/fallback link. It does
not change affiliate URLs, vendor claims, ranking, commission state, or payment
behavior.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "App.jsx"
INDEX = ROOT / "index.html"
DESTINATION = "/best/verified-software-free-trials-deals.html"
APP_MARKER = "COSHUMA_HOME_VERIFIED_OFFERS_CTA_V1"
INDEX_MARKER = "data-home-verified-offers-cta=\"v1\""

APP_BLOCK = r'''        {/* COSHUMA_HOME_VERIFIED_OFFERS_CTA_V1 */}
        <div className="mx-auto mt-6 flex max-w-4xl justify-center px-2">
          <a
            href="/best/verified-software-free-trials-deals.html"
            className="inline-flex min-h-12 items-center justify-center gap-2 rounded-full border border-emerald-400/25 bg-emerald-400/10 px-5 py-3 text-sm font-black text-emerald-100 transition hover:border-emerald-300/50 hover:bg-emerald-400/15 hover:text-white"
          >
            <ShieldCheck className="h-4 w-4" />
            Browse verified free trials &amp; partner offers
            <ArrowRight className="h-4 w-4" />
          </a>
        </div>

'''

INDEX_BLOCK = r'''        <p data-home-verified-offers-cta="v1" style="margin-top: 18px; font-size: 14px; line-height: 1.7;">
          <a href="/best/verified-software-free-trials-deals.html"><strong>Browse verified free trials &amp; partner offers →</strong></a><br />
          <span style="font-size: 12px; color: #64748b;">A focused hub of buyer offers whose customer routes are checked separately from editorial pricing sources.</span>
        </p>

'''


def patch_app(text: str) -> str:
    if APP_MARKER in text:
        return text
    anchor = '        <div className="mx-auto mt-10 grid max-w-4xl grid-cols-3 gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-3 sm:p-4">'
    if anchor not in text:
        raise SystemExit("Homepage stats anchor missing; refusing verified-offers CTA patch")
    return text.replace(anchor, APP_BLOCK + anchor, 1)


def patch_index(text: str) -> str:
    if INDEX_MARKER in text:
        return text
    anchor = '        <section aria-label="Trending AI and SaaS buyer guides"'
    if anchor not in text:
        raise SystemExit("Static homepage trending anchor missing; refusing verified-offers CTA patch")
    return text.replace(anchor, INDEX_BLOCK + anchor, 1)


def main() -> None:
    if not APP.exists() or not INDEX.exists():
        raise SystemExit("Homepage source missing; refusing verified-offers CTA patch")

    app = patch_app(APP.read_text(encoding="utf-8"))
    index = patch_index(INDEX.read_text(encoding="utf-8"))

    required_app = (APP_MARKER, DESTINATION, "Browse verified free trials &amp; partner offers", "ShieldCheck", "ArrowRight")
    required_index = (INDEX_MARKER, DESTINATION, "Browse verified free trials &amp; partner offers")
    for token in required_app:
        if token not in app:
            raise SystemExit(f"Homepage app CTA lost required token: {token}")
    for token in required_index:
        if token not in index:
            raise SystemExit(f"Static homepage CTA lost required token: {token}")

    APP.write_text(app, encoding="utf-8")
    INDEX.write_text(index, encoding="utf-8")
    print("home-verified-offers-discovery-v1")


if __name__ == "__main__":
    main()
