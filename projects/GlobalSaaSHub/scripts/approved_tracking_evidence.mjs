import fs from 'node:fs';
export const approvedTracking = new Map(JSON.parse(fs.readFileSync(new URL('../data/approved-tracking-2026-09-08.json', import.meta.url), 'utf8')).items.map(item => [item.id, item]));
export function applyApprovedTracking(tool) {
  const item = approvedTracking.get(tool.id);
  if (!item) return false;
  if (tool.affiliate_url === item.exact_tracking_url && tool.affiliate_status === 'approved_tracking' && tool.affiliate_verified === true) return true;
  Object.assign(tool, {
    affiliate_url: item.exact_tracking_url,
    affiliate_status: 'approved_tracking',
    affiliate_verified: true,
    affiliate_verified_at: item.checked_at,
    affiliate_final_url: item.destination,
    affiliate_evidence_markers: [item.evidence, 'data/approved-tracking-2026-09-08.json'],
  });
  if ('affiliate_rejection_reason' in tool) tool.affiliate_rejection_reason = null;
  return true;
}
