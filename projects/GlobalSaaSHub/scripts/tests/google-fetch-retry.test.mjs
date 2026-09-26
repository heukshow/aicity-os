import assert from 'node:assert/strict';
import { googleFetch } from '../google_fetch_retry.mjs';

let calls = 0;
const recovered = await googleFetch('https://example.test', {}, {
  fetchImpl: async () => new Response('', { status: ++calls < 3 ? 503 : 200 }), sleep: async () => {},
});
assert.equal(calls, 3);
assert.equal(recovered.status, 200);
calls = 0;
const denied = await googleFetch('https://example.test', {}, {
  fetchImpl: async () => { calls++; return new Response('', { status: 403 }); }, sleep: async () => {},
});
assert.equal(calls, 1);
assert.equal(denied.status, 403);
calls = 0;
await assert.rejects(googleFetch('https://example.test', {}, {
  fetchImpl: async () => { calls++; throw new Error('connection reset'); }, sleep: async () => {},
}));
assert.equal(calls, 3);
console.log('PASS bounded retry, transient recovery, no permission retries');
