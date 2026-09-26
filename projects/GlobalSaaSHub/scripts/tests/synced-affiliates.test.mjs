import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {verifySyncedAffiliates} from '../verify_synced_affiliates.mjs';
const fixture = () => JSON.parse(fs.readFileSync(new URL('../../data/tools.json', import.meta.url), 'utf8'));
test('current direct evidence permits Gravity promotion without relaxing other checks', () => {
  assert.doesNotThrow(() => verifySyncedAffiliates(fixture()));
});
test('Gravity generic homepage cannot replace the issued customer link', () => {
  const tools=fixture(); tools.find(t=>t.id==='gravity-forms').affiliate_url='https://www.gravityforms.com/';
  assert.throws(()=>verifySyncedAffiliates(tools), /gravity-forms/);
});
test('stale approval or unverified link cannot pass the shared deployment contract', () => {
  for (const patch of [{affiliate_status:'approved'}, {affiliate_verified:false}]) {
    const tools=fixture(); Object.assign(tools.find(t=>t.id==='gravity-forms'),patch);
    assert.throws(()=>verifySyncedAffiliates(tools), /gravity-forms/);
  }
});
