"""
affiliate_url_verifier.py - Affiliate URL Evidence Verifier (v2)
================================================================
Single source of truth for affiliate URL verification logic.

Safety rules:
  1. SSL certificate validation is ALWAYS ON. Certificate errors = verification failure.
  2. Path-based pre-blocking is REMOVED. Pages are always fetched before judgment.
  3. Evidence requires STRONG signals, not just a single word anywhere on the page.
  4. Returns a full metadata dict (not just a URL string).

Strong evidence: at least 1 of these compound patterns must be found in the
page title, h1, or first 50KB of body text (case-insensitive):
  - "affiliate program" or "affiliate application" or "join affiliate"
  - "referral program" or "join referral"
  - "partner program" + ("commission" or "payout" or "earn")
  - "commission rate" or "commission percentage" or "payout terms"
  - "cookie duration" or "referral tracking"
  - "affiliate dashboard" or "affiliate application form"
  - "refer a friend" + ("earn" or "reward" or "commission")

Weak signals (NOT sufficient alone):
  - Single occurrence of "affiliate" in footer, privacy policy, or blog link
  - Generic "partners" or "contact" text
"""

import ssl
import urllib.request
import urllib.error
import re
from datetime import datetime, timezone


MAX_REDIRECTS = 10  # Safety limit to prevent redirect loops


class _Redirect308Handler(urllib.request.HTTPRedirectHandler):
    """
    Extends the default redirect handler to also follow
    HTTP 307 (Temporary Redirect) and 308 (Permanent Redirect)
    with the same method as 301/302.
    Python's built-in handler misses 308 in older versions.
    SSL validation is NOT relaxed by this handler.
    """
    def http_error_307(self, req, fp, code, msg, headers):
        return self.http_error_302(req, fp, code, msg, headers)

    def http_error_308(self, req, fp, code, msg, headers):
        return self.http_error_301(req, fp, code, msg, headers)


# Strong compound evidence patterns (regex, case-insensitive)
# At least ONE must match for the URL to be accepted.
STRONG_EVIDENCE_PATTERNS = [
    r"affiliate\s+program",
    r"affiliate\s+application",
    r"join\s+(our\s+)?affiliate",
    r"become\s+an?\s+affiliate",
    r"referral\s+program",
    r"join\s+(our\s+)?referral",
    r"partner\s+program.{0,80}(commission|payout|earn)",
    r"commission\s+rate",
    r"commission\s+percentage",
    r"payout\s+terms",
    r"cookie\s+duration",
    r"referral\s+tracking",
    r"affiliate\s+dashboard",
    r"affiliate\s+application\s+form",
    r"refer\s+a\s+friend.{0,80}(earn|reward|commission)",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in STRONG_EVIDENCE_PATTERNS]

# Path risk signals (used only as informational metadata, NOT as pre-blockers)
GENERIC_PARTNER_PATH_SIGNALS = [
    "/partners",
    "/contact",
    "/resellers",
    "/enterprise",
    "/business",
]

# Maximum HTML body to read (50KB is enough for above-fold + main content)
MAX_HTML_BYTES = 51_200


def _make_ssl_context():
    """Returns a default SSL context with full certificate validation (no bypass)."""
    return ssl.create_default_context()


def _build_opener(ssl_ctx):
    """
    Build a urllib opener with:
      - Full SSL validation (via HTTPSHandler with custom context)
      - 307/308 redirect support (_Redirect308Handler)
      - Max redirect limit enforced
    Uses urllib.request.build_opener for standard handler chain integration.
    """
    https_handler = urllib.request.HTTPSHandler(context=ssl_ctx)
    redirect_handler = _Redirect308Handler()
    redirect_handler.max_redirections = MAX_REDIRECTS
    return urllib.request.build_opener(https_handler, redirect_handler)


def _has_path_risk_signal(url: str) -> bool:
    """Informational: True if the URL path contains a generic partner-page pattern."""
    try:
        lower = url.lower().split("?")[0].rstrip("/")
        return any(lower.endswith(sig) for sig in GENERIC_PARTNER_PATH_SIGNALS)
    except Exception:
        return False


def _find_strong_evidence(html: str) -> list:
    """Returns list of matched strong evidence pattern strings."""
    found = []
    for pat, src in zip(_COMPILED_PATTERNS, STRONG_EVIDENCE_PATTERNS):
        if pat.search(html):
            found.append(src)
    return found


def verify_affiliate_url(url: str, timeout: int = 10) -> dict:
    """
    Verify that a URL is a genuine affiliate/referral program page.

    SSL validation is ALWAYS enforced. SSL errors = rejection.
    The page is ALWAYS fetched before any content judgment.
    A single word match is NOT sufficient; compound patterns are required.

    Returns dict with keys:
        accepted (bool)
        http_status (int|None)
        final_url (str|None)
        evidence_patterns (list)      - strong patterns matched
        path_risk_signal (bool)       - informational only
        rejection_reason (str)        - non-empty if rejected
        verified_at (str|None)        - ISO-8601 UTC if accepted
    """
    result = {
        "accepted": False,
        "http_status": None,
        "final_url": None,
        "evidence_patterns": [],
        "path_risk_signal": False,
        "rejection_reason": "",
        "verified_at": None,
    }

    if not url or not isinstance(url, str) or not url.strip().startswith(("http://", "https://")):
        result["rejection_reason"] = "Invalid or missing URL"
        return result

    result["path_risk_signal"] = _has_path_risk_signal(url)

    ssl_ctx = _make_ssl_context()
    opener = _build_opener(ssl_ctx)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )

    try:
        resp = opener.open(req, timeout=timeout)
        if resp is None:
            result["rejection_reason"] = "Response object is None"
            return result

        result["http_status"] = resp.status
        final_url = resp.geturl()
        result["final_url"] = final_url

        if not final_url or not final_url.startswith(("http://", "https://")):
            result["rejection_reason"] = "Final URL after redirect is invalid"
            return result

        html = resp.read(MAX_HTML_BYTES).decode("utf-8", errors="replace")
        evidence = _find_strong_evidence(html)
        result["evidence_patterns"] = evidence

        if not evidence:
            result["rejection_reason"] = (
                "HTTP 200 but no strong affiliate evidence found. "
                "Required at least one compound pattern (e.g. 'affiliate program', "
                "'commission rate', 'cookie duration'). "
                "Single-word matches in footer/privacy/blog are not accepted."
            )
        else:
            result["accepted"] = True
            result["verified_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    except ssl.SSLError as e:
        result["http_status"] = None
        result["rejection_reason"] = f"SSL certificate error: {e}"
    except urllib.error.HTTPError as e:
        result["http_status"] = e.code
        result["rejection_reason"] = f"HTTP error {e.code}"
        # Extract final_url from HTTPError if available
        final = getattr(e, "filename", None) or getattr(e, "url", None)
        if final and isinstance(final, str) and final.startswith(("http://", "https://")):
            result["final_url"] = final
    except urllib.error.URLError as e:
        result["rejection_reason"] = f"URL error: {e.reason}"
    except Exception as e:
        result["rejection_reason"] = f"Network error: {type(e).__name__}: {e}"

    return result


def safe_affiliate_result(url: str, tool_name: str = "") -> dict:
    """
    Verify affiliate URL and return a full metadata dict suitable for
    direct merge into a tool's data record.

    Keys returned:
        affiliate_url               - verified URL or None
        affiliate_verified          - bool
        affiliate_source_url        - original URL attempted
        affiliate_final_url         - URL after redirects (or None)
        affiliate_http_status       - int or None
        affiliate_evidence_markers  - list of matched strong patterns
        affiliate_verified_at       - ISO-8601 UTC string or None
        affiliate_rejection_reason  - non-empty string if rejected
    """
    verdict = verify_affiliate_url(url)

    if verdict["accepted"]:
        print(
            f"   affiliate program found [{tool_name}]: {url}; "
            "an approved account-specific tracking link is still required"
        )
        return {
            "affiliate_url": None,
            "affiliate_verified": False,
            "affiliate_status": "program_available_unapproved",
            "affiliate_source_url": url,
            "affiliate_final_url": verdict["final_url"],
            "affiliate_http_status": verdict["http_status"],
            "affiliate_evidence_markers": verdict["evidence_patterns"],
            "affiliate_verified_at": None,
            "affiliate_rejection_reason": "Program exists, but no approved COSHUMA tracking link is present",
        }
    else:
        print(f"   affiliate_url REJECTED [{tool_name}]: {verdict['rejection_reason']}")
        return {
            "affiliate_url": None,
            "affiliate_verified": False,
            "affiliate_status": "unverified",
            "affiliate_source_url": url,
            "affiliate_final_url": verdict["final_url"],
            "affiliate_http_status": verdict["http_status"],
            "affiliate_evidence_markers": [],
            "affiliate_verified_at": None,
            "affiliate_rejection_reason": verdict["rejection_reason"],
        }
