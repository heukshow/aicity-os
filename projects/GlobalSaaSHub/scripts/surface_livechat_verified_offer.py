"""Surface the already verified LiveChat customer tracking route on its buyer page.

The repository records an authenticated, account-specific LiveChat campaign URL.
It is a customer-facing tracked route, but it is not a direct pricing or trial deep
link. Keep the official pricing page available for terms, and make the commercial
CTA honest about opening LiveChat before the visitor starts the 14-day trial.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "tool" / "livechat.html"
TRACKING_URL = "https://www.livechat.com/?a=8IetMhQv&utm_campaign=pp_livechat-default&utm_source=PP"
OFFICIAL_PRICING_URL = "https://www.livechat.com/pricing/"

CTA_RE = re.compile(
    r'<a\s+data-cta="official"\s+href="https://www\.livechat\.com/pricing/"'
    r'(?P<attrs>[^>]*)>\s*<span>Start the official 14-day trial</span><span>→</span>\s*</a>',
    re.I | re.S,
)


def main() -> None:
    if not PAGE.exists():
        raise SystemExit(f"LiveChat buyer page not found: {PAGE}")

    original = PAGE.read_text(encoding="utf-8")
    if TRACKING_URL in original and 'data-tool-id="livechat"' in original:
        updated = original
    else:
        def replace(match: re.Match[str]) -> str:
            attrs = match.group("attrs")
            # Replace any pre-existing rel/target values from the official CTA so
            # the tracked outbound link carries the correct sponsored attribution.
            attrs = re.sub(r'\s+rel="[^"]*"', '', attrs, flags=re.I)
            attrs = re.sub(r'\s+target="[^"]*"', '', attrs, flags=re.I)
            return (
                '<a data-cta="affiliate" data-tool-id="livechat" '
                'data-cta-source="livechat-pricing-trial" '
                f'href="{TRACKING_URL}" target="_blank" '
                'rel="sponsored noopener noreferrer"'
                f'{attrs}>'
                '<span>Open LiveChat → start 14-day trial</span><span>→</span></a>'
            )

        updated, count = CTA_RE.subn(replace, original, count=1)
        if count != 1:
            raise SystemExit("Expected LiveChat official trial CTA was not found exactly once")

    # Keep an untracked official pricing source on-page so buyers can confirm the
    # current plans and trial terms independently of the tracked commercial CTA.
    if OFFICIAL_PRICING_URL not in updated:
        raise SystemExit("LiveChat official pricing source disappeared")
    if updated.count(TRACKING_URL) != 1:
        raise SystemExit("LiveChat tracking URL must appear exactly once on the buyer page")
    if 'data-cta="affiliate" data-tool-id="livechat"' not in updated:
        raise SystemExit("LiveChat tracked CTA is missing affiliate instrumentation")
    if 'rel="sponsored noopener noreferrer"' not in updated:
        raise SystemExit("LiveChat tracked CTA is missing sponsored attribution")
    if 'data-cta="affiliate" data-tool-id="livechat" data-cta-source="livechat-pricing-trial" href="https://www.livechat.com/"' in updated:
        raise SystemExit("Refusing to publish a generic untracked LiveChat homepage as an affiliate CTA")

    if updated != original:
        PAGE.write_text(updated, encoding="utf-8")
        print(f"LiveChat verified offer surfaced: {TRACKING_URL}")
    else:
        print("LiveChat verified offer already current")


if __name__ == "__main__":
    main()
