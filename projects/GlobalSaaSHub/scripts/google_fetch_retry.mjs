// Retry only transient failures for read-only Google analytics requests.
export async function googleFetch(url, init, {
  fetchImpl = fetch, sleep = ms => new Promise(resolve => setTimeout(resolve, ms)), attempts = 3,
} = {}) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await fetchImpl(url, { ...init, signal: AbortSignal.timeout(25000) });
      if (![408, 429, 500, 502, 503, 504].includes(response.status) || attempt === attempts - 1) return response;
      await response.body?.cancel();
    } catch (error) {
      if (attempt === attempts - 1) throw error;
    }
    await sleep(500 * 2 ** attempt);
  }
}
