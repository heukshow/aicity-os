import assert from 'node:assert/strict';
import test from 'node:test';
import worker from '../src/entry.js';

test('worker entry exposes fetch and scheduled handlers', () => {
  assert.equal(typeof worker.fetch, 'function');
  assert.equal(typeof worker.scheduled, 'function');
});

test('scheduled maintenance is a no-op without D1 binding', async () => {
  let waitUntilCalled = false;
  await worker.scheduled(
    { scheduledTime: Date.parse('2026-09-17T00:00:00.000Z') },
    {},
    { waitUntil() { waitUntilCalled = true; } },
  );
  assert.equal(waitUntilCalled, false);
});
