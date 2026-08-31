import assert from 'node:assert/strict';
import test from 'node:test';
import worker from '../src/index.js';

const hash = async (value) => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)))].map((b) => b.toString(16).padStart(2, '0')).join('');
const env = async () => ({ ADMIN_PATH: '/ops-private/secret-console', ADMIN_USERNAME: 'owner', ADMIN_PASSWORD_SHA256: await hash('correct horse battery staple') });

test('admin route shows only a login form to unauthenticated visitors and blocks indexing', async () => {
  const response = await worker.fetch(new Request('https://worker.example/ops-private/secret-console'), await env());
  assert.equal(response.status, 200);
  assert.match(response.headers.get('x-robots-tag'), /noindex/);
  assert.equal(response.headers.get('cache-control'), 'no-store, private');
  const body = await response.text();
  assert.match(body, /안전하게 로그인/);
  assert.doesNotMatch(body, /Affiliate 우선순위/);
});

test('admin route accepts correct server-side credentials', async () => {
  const request = new Request('https://worker.example/ops-private/secret-console', { headers: { authorization: `Basic ${btoa('owner:correct horse battery staple')}` } });
  const response = await worker.fetch(request, await env());
  assert.equal(response.status, 200);
  assert.match(await response.text(), /COSHUMA 운영센터/);
});

test('form login sets a secure HttpOnly session cookie', async () => {
  const body = new URLSearchParams({ username: 'owner', password: 'correct horse battery staple' });
  const request = new Request('https://worker.example/ops-private/secret-console', { method: 'POST', body });
  const response = await worker.fetch(request, await env());
  assert.equal(response.status, 303);
  assert.match(response.headers.get('set-cookie'), /HttpOnly; Secure; SameSite=Strict/);
});

test('unknown paths do not reveal the configured admin route', async () => {
  const response = await worker.fetch(new Request('https://worker.example/admin'), await env());
  assert.equal(response.status, 503);
  assert.doesNotMatch(await response.text(), /ops-private|secret-console/);
});
