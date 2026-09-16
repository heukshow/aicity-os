import assert from 'node:assert/strict';
import test from 'node:test';
import { targetInventoryAvailable, targetPageMatchesPlacement } from '../src/advertiser-api.js';

test('sponsorship products only target their reserved page families', () => {
  assert.equal(targetPageMatchesPlacement('tool_page', '/tool/example.html'), true);
  assert.equal(targetPageMatchesPlacement('buyer_intent', '/best/example.html'), true);
  assert.equal(targetPageMatchesPlacement('comparison', '/compare/a-vs-b.html'), true);

  assert.equal(targetPageMatchesPlacement('tool_page', '/best/example.html'), false);
  assert.equal(targetPageMatchesPlacement('buyer_intent', '/compare/a-vs-b.html'), false);
  assert.equal(targetPageMatchesPlacement('comparison', '/tool/example.html'), false);
  assert.equal(targetPageMatchesPlacement('unknown', '/tool/example.html'), false);
});

test('target inventory must exist on the exact COSHUMA page before auto-publication', async () => {
  const goodFetch = async (url, options) => {
    assert.equal(url, 'https://coshuma.com/tool/example.html');
    assert.equal(options.method, 'GET');
    return new Response('<section data-sponsored-slot="tool-primary" hidden></section>', {
      status: 200,
      headers: { 'content-type': 'text/html' },
    });
  };
  assert.equal(await targetInventoryAvailable(
    'tool_page', '/tool/example.html', 'https://coshuma.com', goodFetch,
  ), true);

  const missingSlot = async () => new Response('<main>No sponsored inventory</main>', { status: 200 });
  assert.equal(await targetInventoryAvailable(
    'tool_page', '/tool/example.html', 'https://coshuma.com', missingSlot,
  ), false);

  const notFound = async () => new Response('Not found', { status: 404 });
  assert.equal(await targetInventoryAvailable(
    'tool_page', '/tool/missing.html', 'https://coshuma.com', notFound,
  ), false);
});
