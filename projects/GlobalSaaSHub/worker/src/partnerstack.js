const API_ROOT = 'https://api.partnerstack.com/api/v2';

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
      : [];

const cents = (value) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
};

export async function fetchPartnerStackMetrics(env) {
  if (!env.PARTNERSTACK_API_KEY) return { connected: false, reason: 'API 키 없음' };
  const [rewardsPayload, partnershipsPayload] = await Promise.all([
    request('/rewards?limit=250&order_by=-created_at', env.PARTNERSTACK_API_KEY),
    request('/partnerships?limit=250&order_by=-updated_at', env.PARTNERSTACK_API_KEY),
  ]);
  const rewards = list(rewardsPayload);
  const partnerships = list(partnershipsPayload);
  let pending = 0;
  let paid = 0;
  let total = 0;
  for (const reward of rewards) {
    const amount = cents(reward.amount);
    total += amount;
    const status = String(reward.payment_status || reward.status || '').toLowerCase();
    if (['paid', 'completed', 'sent'].includes(status)) paid += amount;
    else if (!['declined', 'rejected', 'void', 'cancelled', 'canceled'].includes(status)) pending += amount;
  }
  const statusCounts = { approved: 0, pending: 0, declined: 0, other: 0 };
  for (const partnership of partnerships) {
    const status = String(partnership.approved_status || partnership.status || '').toLowerCase();
    if (status === 'approved' || status === 'active') statusCounts.approved += 1;
    else if (status === 'pending') statusCounts.pending += 1;
    else if (status === 'declined' || status === 'rejected') statusCounts.declined += 1;
    else statusCounts.other += 1;
  }
  return {
    connected: true,
    source: 'PartnerStack API',
    checkedAt: new Date().toISOString(),
    rewardCount: rewards.length,
    partnershipCount: partnerships.length,
    total: total / 100,
    pending: pending / 100,
    paid: paid / 100,
    statusCounts,
  };
}
