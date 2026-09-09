import fs from 'node:fs';

const observedAt = '2026-09-10T08:26:43+09:00';

const promoted = new Map([
  ['fillout', {
    affiliate_status: 'approved_tracking',
    affiliate_verified: true,
    affiliate_url: 'https://try.fillout.com/sang-kwon-an-hxwn',
    affiliate_final_url: 'https://try.fillout.com/sang-kwon-an-hxwn',
    affiliate_status_checked_at: observedAt,
    affiliate_verified_at: observedAt,
    marker: 'Newer authenticated Dub/vendor evidence verifies COSHUMA customer tracking URL https://try.fillout.com/sang-kwon-an-hxwn; do not regress to application_submitted or reapply.',
  }],
  ['beefree', {
    affiliate_status: 'approved_tracking',
    affiliate_verified: true,
    affiliate_url: 'https://partners.beefree.io/kqi520hezix2',
    affiliate_final_url: 'https://partners.beefree.io/kqi520hezix2',
    affiliate_status_checked_at: observedAt,
    affiliate_verified_at: observedAt,
    marker: 'Newer PartnerStack approval evidence verifies COSHUMA customer referral URL https://partners.beefree.io/kqi520hezix2; do not regress to application_submitted or reapply.',
  }],
  ['gravity-forms', {
    affiliate_status: 'approved',
    affiliate_verified: true,
    affiliate_url: null,
    affiliate_final_url: null,
    affiliate_status_checked_at: observedAt,
    affiliate_verified_at: observedAt,
    marker: 'Newer vendor correspondence confirms the COSHUMA Gravity Forms affiliate account is approved, but the exact customer-facing tracking URL is still unresolved; do not regress to application_submitted or invent a link.',
  }],
]);

function mergeMarkers(existing, marker) {
  const current = Array.isArray(existing) ? existing : [];
  return current.includes(marker) ? current : [...current, marker];
}

for (const relativePath of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(relativePath, 'utf8'));
  let changed = 0;
  for (const tool of tools) {
    const desired = promoted.get(tool.id);
    if (!desired) continue;
    const next = {
      ...tool,
      affiliate_status: desired.affiliate_status,
      affiliate_verified: desired.affiliate_verified,
      affiliate_url: desired.affiliate_url,
      affiliate_final_url: desired.affiliate_final_url,
      affiliate_status_checked_at: desired.affiliate_status_checked_at,
      affiliate_verified_at: desired.affiliate_verified_at,
      affiliate_evidence_markers: mergeMarkers(tool.affiliate_evidence_markers, desired.marker),
    };
    if (JSON.stringify(next) !== JSON.stringify(tool)) {
      Object.assign(tool, next);
      changed += 1;
    }
  }
  fs.writeFileSync(relativePath, `${JSON.stringify(tools, null, 2)}\n`);
  console.log(`reconcile_promoted_affiliate_states: ${relativePath} changed=${changed}`);
}
