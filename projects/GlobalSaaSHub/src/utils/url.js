/**
 * Verified affiliate links that have been confirmed outside the catalog data pipeline
 * but are not yet migrated into tools.json. Keep this list small and evidence-backed.
 */
const VERIFIED_AFFILIATE_OVERRIDES = {
  castmagic: "https://castmagic.io?fpr=sangkwon-an54",
  descript: "https://get.descript.com/ole5fu20j5sq",
  "fireflies-ai": "https://fireflies.ai/?fpr=sangkwon53",
  pictory: "https://pictory.ai?fpr=sangkwon-an23",
  vidiq: "https://vidiq.com/coshuma",
};

/**
 * Validates and extracts a clean HTTP/HTTPS external URL from a tool object.
 * Uses an explicit verified override first, then affiliate_url only after explicit
 * verification, and finally falls back to official_url.
 * Returns null if no valid URL is found (rejects null, undefined, none, #, empty strings).
 */
export const getValidExternalUrl = (tool) => {
  if (!tool) return null;

  const verifiedOverride = VERIFIED_AFFILIATE_OVERRIDES[tool.id];
  const candidates = verifiedOverride
    ? [verifiedOverride, tool.official_url]
    : tool.affiliate_verified === true
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
