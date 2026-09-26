import fs from './affiliate_state_fs.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const source = JSON.parse(fs.readFileSync(path.join(root, 'data', 'tools.json'), 'utf8'));

// Fail closed: only these explicitly customer-safe fields may ever reach the browser.
// New source fields are PRIVATE BY DEFAULT until intentionally reviewed and added here.
const PUBLIC_FIELDS = Object.freeze([
  'id',
  'name',
  'category',
  'category_display',
  'description',
  'pricing',
  'key_features',
  'rating',
  'rating_source_url',
  'logo_url',
  'primary_category',
  'comparison_group',
  'official_url',
  'pricing_source_url',
  'pricing_verified_at',
  'pricing_verified',
  'currency',
  'billing_period',
]);

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
  for (const key of PUBLIC_FIELDS) {
    if (Object.prototype.hasOwnProperty.call(tool, key)) out[key] = tool[key];
  }

  out.outbound_url = sponsored
    ? tool.affiliate_url.trim()
    : (validHttp(tool.official_url) ? tool.official_url.trim() : null);
  out.is_sponsored = sponsored;
  return out;
});

const ALLOWED_OUTPUT_KEYS = new Set([...PUBLIC_FIELDS, 'outbound_url', 'is_sponsored']);
for (const tool of publicTools) {
  const unexpected = Object.keys(tool).filter((key) => !ALLOWED_OUTPUT_KEYS.has(key));
  if (unexpected.length) {
    throw new Error(`Public dataset contains non-allowlisted fields for ${tool.id}: ${unexpected.join(', ')}`);
  }
}

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
  'browser_required_queue',
  'PartnerStack',
  'FirstPromoter',
]) {
  if (serialized.includes(forbidden)) {
    throw new Error(`Public tool dataset still contains internal marker: ${forbidden}`);
  }
}
console.log(`Generated allowlisted customer-only tool dataset: ${publicTools.length} tools / ${PUBLIC_FIELDS.length + 2} allowed fields max`);
