import assert from 'node:assert/strict';
import test from 'node:test';
import { targetPageMatchesPlacement } from '../src/advertiser-api.js';

test('sponsorship products only target their reserved page families', () => {
  assert.equal(targetPageMatchesPlacement('tool_page', '/tool/example.html'), true);
  assert.equal(targetPageMatchesPlacement('buyer_intent', '/best/example.html'), true);
  assert.equal(targetPageMatchesPlacement('comparison', '/compare/a-vs-b.html'), true);

  assert.equal(targetPageMatchesPlacement('tool_page', '/best/example.html'), false);
  assert.equal(targetPageMatchesPlacement('buyer_intent', '/compare/a-vs-b.html'), false);
  assert.equal(targetPageMatchesPlacement('comparison', '/tool/example.html'), false);
  assert.equal(targetPageMatchesPlacement('unknown', '/tool/example.html'), false);
});
