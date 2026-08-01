"""
affiliate_url_verifier.py - Affiliate URL Evidence Verifier
============================================================
Single source of truth for affiliate URL verification logic.
Used by:
  - auto_aggregator.py  (validates Gemini-discovered affiliate URLs)
  - verify_manual_candidates.py (can be used for manual candidate validation)

Safety rule:
  HTTP 200 alone is NOT sufficient to accept an affiliate_url.
  The page must contain at least one affiliate evidence marker.
  Generic partner/contact/reseller pages are rejected.

Evidence markers required (at least 1 must appear in page HTML):
  affiliate, referral, commission, payout, refer-a-friend, earn money,
  partner program revenue, revenue share

Blocked page patterns (overrides evidence markers):
  If the URL path matches /partners$, /contact, /reseller, /enterprise
  without any affiliate evidence, it is rejected.
"""

import ssl
import urllib.request
import urllib.error

# Minimum evidence: at least one of these must appear in the page HTML (case-insensitive)
AFFILIATE_EVIDENCE_MARKERS = [
    "affiliate",
    "referral",
    "commission",
    "payout",
    "refer-a-friend",
    "earn money",
    "revenue share",
]

# URL path suffixes that indicate a generic (non-affiliate) partner page
GENERIC_PARTNER_PATH_SUFFIXES = [
    "/partners",
    "/contact",
    "/resellers",
    "/enterprise",
    "/business",
]

# Fields to record in tool data for affiliate verification
AFFILIATE_VERIFIED_FIELDS = [
    "affiliate_url",
    "affiliate_verified",           # bool
    "affiliate_source_url",         # URL actually fetched
    "affiliate_final_url",          # URL after redirects
    "affiliate_http_status",        # int or None
    "affiliate_evidence_markers",   # list of found markers
    "affiliate_verified_at",        # ISO-8601 UTC string or None
]


def _make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _is_generic_partner_path(url: str) -> bool:
    """Returns True if the URL path looks like a generic partner page (not affiliate)."""
    try:
        lower = url.lower().split("?")[0].rstrip("/")
        for suffix in GENERIC_PARTNER_PATH_SUFFIXES:
            if lower.endswith(suffix):
                return True
    except Exception:
        pass
    return False


def verify_affiliate_url(url: str, timeout: int = 10) -> dict:
    """
    Verify that a URL is a genuine affiliate/referral program page.

    Returns a dict with:
        accepted (bool)         - True if URL passes all checks
        http_status (int|None)  - HTTP response code
        final_url (str|None)    - URL after redirects
        markers_found (list)    - Evidence markers found in page HTML
        rejection_reason (str)  - Non-empty string if rejected
    """
    result = {
        "accepted": False,
        "http_status": None,
        "final_url": None,
        "markers_found": [],
        "rejection_reason": "",
    }

    if not url or not isinstance(url, str) or not url.strip().startswith(("http://", "https://")):
        result["rejection_reason"] = "Invalid or missing URL"
        return result

    # Reject generic partner paths before HTTP call
    if _is_generic_partner_path(url):
        result["rejection_reason"] = f"URL path matches generic partner pattern (not affiliate): {url}"
        return result

    ssl_ctx = _make_ssl_context()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )

    try:
        resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=timeout)
        result["http_status"] = resp.status
        result["final_url"] = resp.geturl()
        html = resp.read(200_000).decode("utf-8", errors="replace").lower()

        # Check affiliate evidence markers
        found = [m for m in AFFILIATE_EVIDENCE_MARKERS if m in html]
        result["markers_found"] = found

        if not found:
            result["rejection_reason"] = (
                f"HTTP {resp.status} but no affiliate evidence markers found in page. "
                f"Required at least one of: {AFFILIATE_EVIDENCE_MARKERS}"
            )
        else:
            result["accepted"] = True

    except urllib.error.HTTPError as e:
        result["http_status"] = e.code
        result["rejection_reason"] = f"HTTP error {e.code}"
    except Exception as e:
        result["rejection_reason"] = f"Network error: {type(e).__name__}: {e}"

    return result


def safe_affiliate_url(url: str, tool_name: str = "") -> str | None:
    """
    Convenience wrapper: returns url if it passes verification, else None.
    Prints result for pipeline logging.
    """
    if not url:
        return None
    verdict = verify_affiliate_url(url)
    if verdict["accepted"]:
        print(f"   affiliate_url OK [{tool_name}]: {url} (markers: {verdict['markers_found']})")
        return url
    else:
        print(f"   affiliate_url REJECTED [{tool_name}]: {verdict['rejection_reason']}")
        return None
