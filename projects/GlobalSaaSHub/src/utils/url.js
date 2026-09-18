/** Return the already-selected public outbound URL from the customer-only tool dataset. */
export const getValidExternalUrl = (tool) => {
  if (!tool) return null;
  for (const value of [tool.outbound_url, tool.official_url]) {
    if (typeof value !== 'string') continue;
    const url = value.trim();
    if (!url || ['null','undefined','none','n/a','#'].includes(url.toLowerCase())) continue;
    try {
      const parsed = new URL(url);
      if (parsed.protocol === 'https:' || parsed.protocol === 'http:') return url;
    } catch {
      // Ignore malformed public URLs.
    }
  }
  return null;
};
