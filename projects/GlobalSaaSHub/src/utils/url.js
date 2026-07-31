/**
 * Validates and extracts a clean HTTP/HTTPS external URL from a tool object.
 * Checks affiliate_url first, then falls back to official_url.
 * Returns null if no valid URL is found (rejects null, undefined, none, #, empty strings).
 */
export const getValidExternalUrl = (tool) => {
  if (!tool) return null;
  const candidates = [tool.affiliate_url, tool.official_url];

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
