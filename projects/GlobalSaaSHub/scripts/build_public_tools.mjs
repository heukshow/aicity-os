import fs from './affiliate_state_fs.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const source = JSON.parse(fs.readFileSync(path.join(root, 'data', 'tools.json'), 'utf8'));
const countryDoc = JSON.parse(fs.readFileSync(path.join(root, 'data', 'tool_company_countries.json'), 'utf8'));
const countryRecords = countryDoc.tools || {};

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

function countrySlug(value) {
  return String(value || '')
    .normalize('NFKD')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
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

  const country = countryRecords[tool.id];
  if (country) {
    const code = String(country.country_code || '').trim().toUpperCase();
    const name = String(country.country_name || '').trim();
    const flag = String(country.flag || '').trim();
    const slug = countrySlug(name);
    if (!/^[A-Z]{2}$/.test(code) || !name || !flag || !slug) {
      throw new Error(`Invalid public country metadata for ${tool.id}`);
    }
    out.company_country_code = code;
    out.company_country_name = name;
    out.company_country_flag = flag;
    out.company_country_slug = slug;
  }

  out.outbound_url = sponsored
    ? tool.affiliate_url.trim()
    : (validHttp(tool.official_url) ? tool.official_url.trim() : null);
  out.is_sponsored = sponsored;
  return out;
});

const ALLOWED_OUTPUT_KEYS = new Set([...PUBLIC_FIELDS, 'company_country_code', 'company_country_name', 'company_country_flag', 'company_country_slug', 'outbound_url', 'is_sponsored']);
for (const tool of publicTools) {
  const unexpected = Object.keys(tool).filter((key) => !ALLOWED_OUTPUT_KEYS.has(key));
  if (unexpected.length) {
    throw new Error(`Public dataset contains non-allowlisted fields for ${tool.id}: ${unexpected.join(', ')}`);
  }
}

const serialized = JSON.stringify(publicTools);
const policy = JSON.parse(fs.readFileSync(path.join(root, 'config', 'public_content_policy.json'), 'utf8'));
for (const pattern of policy.public_internal_data.forbidden_value_patterns) {
  if (new RegExp(pattern, 'i').test(serialized)) {
    throw new Error(`Public tool dataset contains internal value: ${pattern}`);
  }
}
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
// Validate all keys and values before replacing the last safe artifact.
const dir = path.join(root, 'src', 'generated');
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(path.join(dir, 'public-tools.json'), serialized, 'utf8');
console.log(`Generated allowlisted customer-only tool dataset: ${publicTools.length} tools / ${ALLOWED_OUTPUT_KEYS.size} allowed fields max`);
