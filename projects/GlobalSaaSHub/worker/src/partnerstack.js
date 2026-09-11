const API_ROOT = 'https://api.partnerstack.com/api/v2';
const PAGE_LIMIT = 250;
const MAX_PAGES = 20;

async function request(path, apiKey) {
  const response = await fetch(`${API_ROOT}${path}`, {
    headers: { accept: 'application/json', authorization: `Bearer ${apiKey}` },
  });
  if (!response.ok) throw new Error(`PartnerStack API returned ${response.status}`);
  return response.json();
}

const list = (payload) => Array.isArray(payload?.data)
  ? payload.data
  : Array.isArray(payload?.data?.items)
    ? payload.data.items
    : Array.isArray(payload?.items)
      ? payload.items
      : (() => { throw new Error('PartnerStack response shape not recognized'); })();

async function listAll(path, apiKey) {
  const items = [];
  let cursor = null;
  let pages = 0;
  for (; pages < MAX_PAGES; pages += 1) {
    const separator = path.includes('?') ? '&' : '?';
    const cursorQuery = cursor ? `&starting_after=${encodeURIComponent(cursor)}` : '';
    const payload = await request(`${path}${separator}limit=${PAGE_LIMIT}${cursorQuery}`, apiKey);
    const page = list(payload);
    items.push(...page);
    if (page.length < PAGE_LIMIT) return { items, pages: pages + 1, complete: true };
    const nextCursor = page.at(-1)?.key;
    if (!nextCursor || nextCursor === cursor) return { items, pages: pages + 1, complete: false, reason: 'pagination_cursor_missing' };
    cursor = nextCursor;
  }
  return { items, pages, complete: false, reason: 'pagination_page_cap' };
}

const cents = (value) => {
  if (value === null || value === undefined || typeof value === 'boolean' || (typeof value === 'string' && value.trim() === '')) return null;
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? number : null;
};
const lower = (value) => String(value ?? '').trim().toLowerCase();

function addAmount(bucket, key, amount) {
  bucket[key] = (bucket[key] || 0) + amount;
}

export async function fetchPartnerStackMetrics(env) {
  if (!env.PARTNERSTACK_API_KEY) return { connected: false, reason: 'API 키 없음' };

  const [rewardsResult, partnershipsResult] = await Promise.all([
    listAll('/rewards?order_by=-created_at', env.PARTNERSTACK_API_KEY),
    listAll('/partnerships?order_by=-updated_at', env.PARTNERSTACK_API_KEY),
  ]);
  const rewards = rewardsResult.items;
  const partnerships = partnershipsResult.items;

  const rewardStatusCents = { hold: 0, pending: 0, approved: 0, paid: 0, declined: 0, other: 0 };
  const paymentStatusCents = { pending: 0, available: 0, withdrawn: 0, none: 0, other: 0 };
  const amountsByCurrency = {};
  let invalidAmountCount = 0;

  for (const reward of rewards) {
    const amount = cents(reward.amount);
    if (amount === null) {
      invalidAmountCount += 1;
      continue;
    }
    const currency = String(reward.currency || 'USD').trim().toUpperCase() || 'USD';
    const rewardStatus = lower(reward.reward_status || reward.status);
    const paymentStatus = lower(reward.payment_status);
    const recognizedRewardStatus = ['hold', 'pending', 'approved', 'paid', 'declined'].includes(rewardStatus) ? rewardStatus : 'other';
    const recognizedPaymentStatus = !paymentStatus ? 'none' : ['pending', 'available', 'withdrawn'].includes(paymentStatus) ? paymentStatus : 'other';

    addAmount(rewardStatusCents, recognizedRewardStatus, amount);
    addAmount(paymentStatusCents, recognizedPaymentStatus, amount);
    if (!amountsByCurrency[currency]) amountsByCurrency[currency] = { recognized_earned: 0, hold: 0, pending: 0, approved: 0, paid: 0, declined: 0, available: 0, withdrawn: 0, unknown_status: 0 };
    const currencyBucket = amountsByCurrency[currency];
    addAmount(currencyBucket, recognizedRewardStatus === 'other' ? 'unknown_status' : recognizedRewardStatus, amount);
    if (recognizedPaymentStatus === 'available' || recognizedPaymentStatus === 'withdrawn') addAmount(currencyBucket, recognizedPaymentStatus, amount);
    if (['hold', 'pending', 'approved', 'paid'].includes(recognizedRewardStatus)) currencyBucket.recognized_earned += amount;
  }

  const statusCounts = { approved: 0, pending: 0, declined: 0, other: 0 };
  for (const partnership of partnerships) {
    const status = lower(partnership.approved_status || partnership.status);
    if (status === 'approved' || status === 'active') statusCounts.approved += 1;
    else if (status === 'pending') statusCounts.pending += 1;
    else if (status === 'declined' || status === 'rejected') statusCounts.declined += 1;
    else statusCounts.other += 1;
  }

  const currencies = Object.keys(amountsByCurrency);
  const scalarSafe = currencies.length <= 1;
  const earnedCents = rewardStatusCents.hold + rewardStatusCents.pending + rewardStatusCents.approved + rewardStatusCents.paid;
  const pendingCents = rewardStatusCents.hold + rewardStatusCents.pending + rewardStatusCents.approved;

  let payouts = { connected: false, count: null, complete: false, pages: 0, reason: 'not_checked' };
  try {
    const payoutResult = await listAll('/payouts?order_by=-created_at', env.PARTNERSTACK_API_KEY);
    payouts = { connected: true, count: payoutResult.items.length, complete: payoutResult.complete, pages: payoutResult.pages, reason: payoutResult.reason || null };
  } catch (error) {
    payouts = { connected: false, count: null, complete: false, pages: 0, reason: String(error?.message || 'PartnerStack payouts API 조회 실패') };
  }

  const toDollars = (value) => scalarSafe ? value / 100 : null;
  const currency = currencies.length === 1 ? currencies[0] : currencies.length === 0 ? 'USD' : null;
  const byCurrency = Object.fromEntries(Object.entries(amountsByCurrency).map(([code, bucket]) => [code, Object.fromEntries(Object.entries(bucket).map(([key, value]) => [key, value / 100]))]));

  return {
    connected: true,
    source: 'PartnerStack API',
    checkedAt: new Date().toISOString(),
    rewardCount: rewards.length,
    partnershipCount: partnerships.length,
    currency,
    mixedCurrency: !scalarSafe,
    total: toDollars(earnedCents),
    pending: toDollars(pendingCents),
    paid: toDollars(rewardStatusCents.paid),
    available: toDollars(paymentStatusCents.available),
    withdrawn: toDollars(paymentStatusCents.withdrawn),
    declined: toDollars(rewardStatusCents.declined),
    unknownRewardStatus: toDollars(rewardStatusCents.other),
    invalidAmountCount,
    amountsByCurrency: byCurrency,
    rewardStatusCounts: rewards.reduce((acc, reward) => {
      const status = lower(reward.reward_status || reward.status);
      const key = ['hold', 'pending', 'approved', 'paid', 'declined'].includes(status) ? status : 'other';
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, { hold: 0, pending: 0, approved: 0, paid: 0, declined: 0, other: 0 }),
    paymentStatusCounts: rewards.reduce((acc, reward) => {
      const status = lower(reward.payment_status);
      const key = !status ? 'none' : ['pending', 'available', 'withdrawn'].includes(status) ? status : 'other';
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, { pending: 0, available: 0, withdrawn: 0, none: 0, other: 0 }),
    statusCounts,
    coverage: {
      rewardsComplete: rewardsResult.complete,
      rewardPages: rewardsResult.pages,
      rewardsReason: rewardsResult.reason || null,
      partnershipsComplete: partnershipsResult.complete,
      partnershipPages: partnershipsResult.pages,
      partnershipsReason: partnershipsResult.reason || null,
      payouts,
    },
    semantics: {
      total: 'Recognized non-declined reward statuses only: hold + pending + approved + paid.',
      pending: 'Recognized reward statuses not yet paid: hold + pending + approved.',
      paid: 'Reward status = paid. This is not silently inferred from payment_status.',
      available: 'Payment status = available (withdrawable).',
      withdrawn: 'Payment status = withdrawn. Reported separately from reward status paid.',
      mixedCurrency: 'Scalar money fields are null when multiple reward currencies are present; use amountsByCurrency instead.',
    },
  };
}
