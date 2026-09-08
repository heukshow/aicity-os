/**
 * Validates and extracts a clean HTTP/HTTPS external URL from a tool object.
 * Uses affiliate_url only when a customer-facing tracking route is explicitly approved,
 * then falls back to official_url. Application/pending/closed program states must never
 * be treated as revenue-ready affiliate destinations.
 * Returns null if no valid URL is found (rejects null, undefined, none, #, empty strings).
 */
export const getValidExternalUrl = (tool) => {
  if (!tool) return null;

  const approvedAffiliate =
    tool.affiliate_verified === true && tool.affiliate_status === "approved_tracking";

  const candidates = approvedAffiliate
    ? [tool.affiliate_url, tool.official_url]
    : [tool.official_url];

  for (const value of candidates) {
    if (typeof value !== "string") continue;

    const url = value.trim();
    if (!url || ["null", "undefined", "none", "n/a", "#"].includes(url.toLowerCase())) {
      continue;
    }

    try {
      const parsed = new URL(url);
      if (parsed.protocol === "https:" || parsed.protocol === "http:") {
        return url;
      }
    } catch {
      // Invalid URL syntax
    }
  }

  return null;
};
