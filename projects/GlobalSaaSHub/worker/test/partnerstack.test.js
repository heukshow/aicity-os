import assert from 'node:assert/strict';
import test from 'node:test';
import { fetchPartnerStackMetrics } from '../src/partnerstack.js';

const originalFetch = globalThis.fetch;

test('missing reward amounts are invalid rather than verified zero', async () => {
  globalThis.fetch = async url => new Response(JSON.stringify({data:String(url).includes('/rewards')?[{key:'missing',amount:null,status:'approved',currency:'USD'}]:[]}),{status:200});
  const result=await fetchPartnerStackMetrics({PARTNERSTACK_API_KEY:'test'});
  assert.equal(result.invalidAmountCount,1);
});

test.afterEach(() => { globalThis.fetch = originalFetch; });

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json' } });
}

test('keeps reward status separate from payment status and never counts withdrawn as pending', async () => {
  globalThis.fetch = async url => {
    const value = String(url);
    if (value.includes('/rewards')) return json({ data: [
      { key: 'r1', amount: 1000, status: 'approved', payment_status: 'available', currency: 'USD' },
      { key: 'r2', amount: 500, reward_status: 'paid', payment_status: 'withdrawn', currency: 'USD' },
      { key: 'r3', amount: 700, status: 'declined', payment_status: null, currency: 'USD' },
      { key: 'r4', amount: 300, status: 'pending', payment_status: 'pending', currency: 'USD' },
    ] });
    if (value.includes('/partnerships')) return json({ data: [
      { key: 'p1', status: 'approved' },
      { key: 'p2', status: 'pending' },
    ] });
    if (value.includes('/payouts')) return json({ data: [{ key: 'pay1' }] });
    return json({}, 404);
  };

  const result = await fetchPartnerStackMetrics({ PARTNERSTACK_API_KEY: 'test' });
  assert.equal(result.connected, true);
  assert.equal(result.rewardCount, 4);
  assert.equal(result.total, 18);
  assert.equal(result.pending, 13);
  assert.equal(result.paid, 5);
  assert.equal(result.available, 10);
  assert.equal(result.withdrawn, 5);
  assert.equal(result.declined, 7);
  assert.equal(result.paymentStatusCounts.withdrawn, 1);
  assert.equal(result.rewardStatusCounts.paid, 1);
  assert.equal(result.coverage.payouts.count, 1);
});

test('payout endpoint failure does not hide verified reward metrics', async () => {
  globalThis.fetch = async url => {
    const value = String(url);
    if (value.includes('/rewards')) return json({ data: [{ key: 'r1', amount: 1200, status: 'approved', payment_status: 'available', currency: 'USD' }] });
    if (value.includes('/partnerships')) return json({ data: [] });
    if (value.includes('/payouts')) return json({ error: 'forbidden' }, 403);
    return json({}, 404);
  };
  const result = await fetchPartnerStackMetrics({ PARTNERSTACK_API_KEY: 'test' });
  assert.equal(result.total, 12);
  assert.equal(result.available, 12);
  assert.equal(result.coverage.payouts.connected, false);
  assert.equal(result.coverage.payouts.count, null);
});

test('paginates rewards beyond the first 250 records so older commissions are not silently dropped', async () => {
  let rewardCalls = 0;
  globalThis.fetch = async url => {
    const value = String(url);
    if (value.includes('/rewards')) {
      rewardCalls += 1;
      if (rewardCalls === 1) return json({ data: Array.from({ length: 250 }, (_, i) => ({ key: `r${i}`, amount: 100, status: 'approved', payment_status: 'available', currency: 'USD' })) });
      return json({ data: [{ key: 'r250', amount: 250, status: 'paid', payment_status: 'withdrawn', currency: 'USD' }] });
    }
    if (value.includes('/partnerships')) return json({ data: [] });
    if (value.includes('/payouts')) return json({ data: [] });
    return json({}, 404);
  };
  const result = await fetchPartnerStackMetrics({ PARTNERSTACK_API_KEY: 'test' });
  assert.equal(rewardCalls, 2);
  assert.equal(result.rewardCount, 251);
  assert.equal(result.total, 252.5);
  assert.equal(result.coverage.rewardsComplete, true);
  assert.equal(result.coverage.rewardPages, 2);
});

test('does not collapse mixed currencies into a misleading scalar total', async () => {
  globalThis.fetch = async url => {
    const value = String(url);
    if (value.includes('/rewards')) return json({ data: [
      { key: 'usd', amount: 1000, status: 'approved', payment_status: 'available', currency: 'USD' },
      { key: 'eur', amount: 900, status: 'approved', payment_status: 'available', currency: 'EUR' },
    ] });
    if (value.includes('/partnerships')) return json({ data: [] });
    if (value.includes('/payouts')) return json({ data: [] });
    return json({}, 404);
  };
  const result = await fetchPartnerStackMetrics({ PARTNERSTACK_API_KEY: 'test' });
  assert.equal(result.mixedCurrency, true);
  assert.equal(result.total, null);
  assert.equal(result.amountsByCurrency.USD.recognized_earned, 10);
  assert.equal(result.amountsByCurrency.EUR.recognized_earned, 9);
});
