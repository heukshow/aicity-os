import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = path.resolve(SCRIPT_DIR, '..');
const TOOLS_PATH = path.join(PROJECT_DIR, 'data', 'tools.json');
const COMPARE_DIR = path.join(PROJECT_DIR, 'public', 'compare');

const DISCLOSURE =
  '      <p data-affiliate-disclosure="compare" class="text-[11px] leading-relaxed text-slate-500">' +
  'Affiliate disclosure: Some buttons on this comparison use verified COSHUMA partner links. ' +
  'COSHUMA may earn a commission if you become a paying customer after using them, at no extra cost to you.' +
  '</p>';

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function isSafeHttpUrl(value) {
  try {
    const parsed = new URL(value);
    return parsed.protocol === 'https:' || parsed.protocol === 'http:';
  } catch {
    return false;
  }
}

const tools = JSON.parse(fs.readFileSync(TOOLS_PATH, 'utf8'));
const verifiedRoutes = tools.filter((tool) =>
  tool?.id &&
  tool?.affiliate_verified === true &&
  tool?.affiliate_status === 'approved_tracking' &&
  isSafeHttpUrl(tool?.affiliate_url) &&
  isSafeHttpUrl(tool?.official_url) &&
  tool.affiliate_url !== tool.official_url
);

let filesChanged = 0;
let linksMonetized = 0;
let linksAttributed = 0;
const changedByTool = new Map();

for (const filename of fs.readdirSync(COMPARE_DIR)) {
  if (!filename.endsWith('.html')) continue;

  const filePath = path.join(COMPARE_DIR, filename);
  const original = fs.readFileSync(filePath, 'utf8');
  let updated = original;
  let changedThisFile = 0;

  for (const tool of verifiedRoutes) {
    const exactGeneratedAnchor = new RegExp(
      `<a href="${escapeRegExp(tool.official_url)}" target="_blank" rel="noopener noreferrer"`,
      'g'
    );
    const matches = updated.match(exactGeneratedAnchor)?.length || 0;

    if (matches) {
      const replacement =
        `<a data-cta="affiliate" data-tool-id="${tool.id}" data-cta-source="compare-generated-auto" ` +
        `href="${tool.affiliate_url}" target="_blank" rel="sponsored noopener noreferrer"`;

      updated = updated.replace(exactGeneratedAnchor, () => replacement);
      changedThisFile += matches;
      linksMonetized += matches;
      changedByTool.set(tool.id, (changedByTool.get(tool.id) || 0) + matches);
    }

    const exactUnattributedAffiliateAnchor = new RegExp(
      `<a href="${escapeRegExp(tool.affiliate_url)}" target="_blank" rel="[^"]*"`,
      'g'
    );
    const unattributedMatches = updated.match(exactUnattributedAffiliateAnchor)?.length || 0;

    if (unattributedMatches) {
      const attributedReplacement =
        `<a data-cta="affiliate" data-tool-id="${tool.id}" data-cta-source="compare-existing-affiliate-auto" ` +
        `href="${tool.affiliate_url}" target="_blank" rel="sponsored noopener noreferrer"`;

      updated = updated.replace(exactUnattributedAffiliateAnchor, () => attributedReplacement);
      changedThisFile += unattributedMatches;
      linksAttributed += unattributedMatches;
      changedByTool.set(tool.id, (changedByTool.get(tool.id) || 0) + unattributedMatches);
    }
  }

  if (!changedThisFile) continue;

  if (!updated.includes('/affiliate-attribution.js')) {
    updated = updated.replace(
      /\s*<\/head>/,
      '\n    <script defer src="/affiliate-attribution.js"></script>\n  </head>'
    );
  }

  if (!updated.includes('data-affiliate-disclosure="compare"')) {
    updated = updated.replace(/(?=\s*<\/main>)/, `${DISCLOSURE}\n`);
  }

  fs.writeFileSync(filePath, updated, 'utf8');
  filesChanged += 1;
}

const breakdown = [...changedByTool.entries()]
  .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  .map(([toolId, count]) => `${toolId}:${count}`)
  .join(', ');

console.log(
  `monetize_verified_compare_links: verified_routes=${verifiedRoutes.length} ` +
  `files_changed=${filesChanged} links_monetized=${linksMonetized} links_attributed=${linksAttributed}` +
  (breakdown ? ` [${breakdown}]` : '')
);
