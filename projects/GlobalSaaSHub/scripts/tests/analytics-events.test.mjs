import { test } from 'node:test';
import assert from 'node:assert/strict';
import { trackPageView, trackToolClick } from '../../src/utils/analytics.js';

test('acquisition uses browser URL/referrer even when local storage is blocked', () => {
  const calls = [];
  globalThis.window = {
    location: { href:'https://coshuma.com/?utm_source=youtube&utm_medium=social', pathname:'/', search:'?utm_source=youtube&utm_medium=social' },
    gtag: (...args) => calls.push(args),
  };
  globalThis.document = { title:'COSHUMA', referrer:'https://www.google.com/' };
  globalThis.localStorage = { getItem() { throw new Error('blocked'); } };
  const warn = console.warn;
  console.warn = () => {};
  try {
    trackPageView();
    trackToolClick('pictory','Pictory','https://pictory.ai/?fpr=example',true);
    trackToolClick('example','Example','https://example.com/',false);
  } finally { console.warn = warn; }
  assert.deepEqual(calls.map(c=>c[1]),['page_view','affiliate_click','outbound_click']);
  for (const [, , payload] of calls) {
    assert.equal(payload.page_referrer,'https://www.google.com/');
    assert.equal(payload.page_location,window.location.href);
    for (const key of ['source','medium','campaign','country','flag']) assert.equal(key in payload,false);
  }
  assert.equal(calls[1][2].tool_id,'pictory');
  assert.equal(calls[1][2].tool_name,'Pictory');
  assert.equal(calls[1][2].outbound_domain,'pictory.ai');
  assert.equal(calls[1][2].transport_type,'beacon');
});
