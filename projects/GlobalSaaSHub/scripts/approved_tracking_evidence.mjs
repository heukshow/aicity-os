import fs from 'node:fs';

export const approvedTracking = new Map(JSON.parse(fs.readFileSync(new URL('../data/approved-tracking-2026-09-08.json', import.meta.url), 'utf8')).items.map(item => [item.id, item]));

// Newer authenticated Dub follow-up for a tool that already exists in the public catalog.
// Fillout approval remains valid operational evidence, but Fillout is not yet a catalog tool,
// so it must not enter this map because deployment verification requires a real tool page.
approvedTracking.set('krater', {
  id: 'krater',
  status: 'approved_tracking',
  exact_tracking_url: 'https://go.krater.ai/sang-kwon-an',
  destination: 'https://go.krater.ai/sang-kwon-an',
  evidence: 'Authenticated Dub partner dashboard shows Krater Approved/Enrolled and issues the exact customer-facing tracking link go.krater.ai/sang-kwon-an. The Dub partner-application URL is not treated as a customer tracking link. No referral, sale, commission, or revenue is inferred.',
  checked_at: '2026-09-08T14:00:00+09:00',
  evidence_file: 'data/krater-affiliate-enrollment-evidence-2026-09-08.md',
});

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
    affiliate_evidence_markers: [item.evidence, item.evidence_file || 'data/approved-tracking-2026-09-08.json'],
  });
  if ('affiliate_rejection_reason' in tool) tool.affiliate_rejection_reason = null;
  return true;
}
