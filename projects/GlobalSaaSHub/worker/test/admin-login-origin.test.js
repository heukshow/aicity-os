import test from 'node:test';
import assert from 'node:assert/strict';
import { privateLogin } from '../src/admin.js';

const encoder = new TextEncoder();
async function sha256(value) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(value)))]
    .map(byte => byte.toString(16).padStart(2,'0')).join('');
}

async function request(headers = {}) {
  const body = new URLSearchParams({ username: 'support@coshuma.com', password: 'synthetic-pass' });
  return new Request('https://globalsaashub-payments.example/ops-private/test/', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded', ...headers },
    body,
  });
}

test('private login accepts Chrome null-origin only for same-origin document navigation', async () => {
  const env = {
    ADMIN_USERNAME: 'support@coshuma.com',
    ADMIN_PASSWORD_SHA256: await sha256('synthetic-pass'),
    ADMIN_PATH: '/ops-private/test',
  };
  const response = await privateLogin(await request({
    origin: 'null',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-dest': 'document',
  }), env);
  assert.equal(response.status, 303);
  assert.match(response.headers.get('set-cookie') || '', /^coshuma_ops=/);
});

test('private login still rejects foreign and ambiguous null-origin requests', async () => {
  const env = {
    ADMIN_USERNAME: 'support@coshuma.com',
    ADMIN_PASSWORD_SHA256: await sha256('synthetic-pass'),
    ADMIN_PATH: '/ops-private/test',
  };
  assert.equal((await privateLogin(await request({ origin: 'https://evil.example' }), env)).status, 403);
  assert.equal((await privateLogin(await request({
    origin: 'null',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-dest': 'document',
  }), env)).status, 403);
  assert.equal((await privateLogin(await request({
    origin: 'null',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
  }), env)).status, 403);
});
