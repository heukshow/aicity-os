"""
http_verification_status.py - Canonical HTTP Verification Status Enum
======================================================================
Single source of truth for http_verification_status values used by:
  - verify_manual_candidates.py  (writes status values)
  - validate_data.py             (validates status values)

All status strings and the allowed set MUST be defined here only.
Do NOT hardcode status strings or duplicate ALLOWED_HTTP_STATUSES elsewhere.
"""

# Canonical status constants
HTTP_VERIFIED_200       = "verified_http_200"
HTTP_REDIRECT_VERIFIED  = "redirect_verified"
HTTP_BOT_BLOCKED        = "bot_blocked"
HTTP_RATE_LIMITED       = "rate_limited"
HTTP_ERROR              = "http_error"
HTTP_NETWORK_ERROR      = "network_error"

# Allowed set (used by validate_data.py)
# None means "not yet verified" (auto-aggregated tools start unverified)
ALLOWED_HTTP_STATUSES = frozenset({
    HTTP_VERIFIED_200,
    HTTP_REDIRECT_VERIFIED,
    HTTP_BOT_BLOCKED,
    HTTP_RATE_LIMITED,
    HTTP_ERROR,
    HTTP_NETWORK_ERROR,
    None,
})


def http_code_to_status(http_code, is_redirect=False):
    """
    Map an integer HTTP status code to a canonical status string.

    Args:
        http_code:   Integer HTTP status code, or None if connection failed.
        is_redirect: True when urllib followed a redirect to a different URL.

    Returns:
        One of the HTTP_* constants above.
    """
    if http_code is None:
        return HTTP_NETWORK_ERROR
    if is_redirect:
        return HTTP_REDIRECT_VERIFIED
    if http_code == 200:
        return HTTP_VERIFIED_200
    if http_code in (401, 403):
        return HTTP_BOT_BLOCKED
    if http_code == 429:
        return HTTP_RATE_LIMITED
    return HTTP_ERROR
