import fs from 'node:fs';

const evidence = 'data/tidio-affiliate-rejection-evidence-2026-08-25.md';
const authoritative = {
  affiliate_url: null,
  affiliate_verified: true,
  affiliate_status: 'rejected',
  affiliate_verified_at: '2026-08-25T00:00:00Z',
  affiliate_source_url: null,
  affiliate_evidence_markers: [
    'PartnerStack application confirmation received 2026-08-24.',
    'Newer PartnerStack status on 2026-08-25 states Tidio declined the COSHUMA application.',
    `Authoritative repository evidence: ${evidence}`,
    'Do not reapply automatically; no COSHUMA customer-facing Tidio tracking URL is verified.',
  ],
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const tool = tools.find((item) => item.id === 'tidio');
  if (!tool) throw new Error(`Tidio record missing from ${file}`);
  Object.assign(tool, authoritative);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

console.log('Tidio authoritative rejected state enforced in tools.json and tools.next.json');
