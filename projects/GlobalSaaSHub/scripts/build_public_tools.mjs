import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const source = JSON.parse(fs.readFileSync(path.join(root, 'data', 'tools.json'), 'utf8'));

const blockedExact = new Set([
  'application_state',
  'official_verification_status',
  'official_verified_at',
  'official_evidence_url',
  'is_manual_override',
  'evidence_source_type',
]);

function isBlockedKey(key) {
  const k = key.toLowerCase();
  return k.startsWith('affiliate_') ||
    k.startsWith('application_') ||
    k.includes('revenue_truth') ||
    k.includes('browser_required') ||
    k.includes('evidence_marker') ||
    k.includes('verification_evidence') ||
    blockedExact.has(k);
}

function validHttp(value) {
  if (typeof value !== 'string') return false;
  try {
    const u = new URL(value.trim());
    return u.protocol === 'https:' || u.protocol === 'http:';
  } catch {
    return false;
  }
}

const publicTools = source.map((tool) => {
  const sponsored =
    tool.affiliate_verified === true &&
    tool.affiliate_status === 'approved_tracking' &&
    validHttp(tool.affiliate_url);
  const out = {};
  for (const [key, value] of Object.entries(tool)) {
    if (!isBlockedKey(key)) out[key] = value;
  }
  delete out.affiliate_url;
  out.outbound_url = sponsored ? tool.affiliate_url.trim() : (validHttp(tool.official_url) ? tool.official_url.trim() : null);
  out.is_sponsored = sponsored;
  return out;
});

const dir = path.join(root, 'src', 'generated');
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(path.join(dir, 'public-tools.json'), JSON.stringify(publicTools), 'utf8');

const serialized = JSON.stringify(publicTools);
for (const forbidden of [
  'affiliate_evidence_markers',
  'affiliate_status',
  'affiliate_verified',
  'affiliate_next_action',
  'application_state',
  'revenue_truth',
  'PartnerStack',
  'FirstPromoter',
]) {
  if (serialized.includes(forbidden)) {
    throw new Error(`Public tool dataset still contains internal marker: ${forbidden}`);
  }
}
console.log(`Generated customer-only tool dataset: ${publicTools.length} tools`);
