import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = path.resolve(SCRIPT_DIR, '..');
const TOOLS_PATH = path.join(PROJECT_DIR, 'data', 'tools.json');
const COMPARE_DIR = path.join(PROJECT_DIR, 'public', 'compare');
const TOOL_DIR = path.join(PROJECT_DIR, 'public', 'tool');

const DISCLOSURE =
  '      <p data-affiliate-disclosure="compare" class="text-[11px] leading-relaxed text-slate-500">' +
  'Affiliate disclosure: Some buttons on this comparison use verified COSHUMA partner links. ' +
  'COSHUMA may earn a commission if you become a paying customer after using them, at no extra cost to you.' +
  '</p>';

const TOOL_DISCLOSURE =
  '      <p data-affiliate-disclosure="tool" class="text-[11px] leading-relaxed text-slate-500">' +
  'Affiliate disclosure: This page may use a verified COSHUMA partner link. ' +
  'COSHUMA may earn a commission if you become a paying customer after using it, at no extra cost to you.' +
  '</p>';

const SPONSORSHIP_MAILTO =
  'mailto:support@coshuma.com?subject=COSHUMA%20%2449%20sponsorship%20inquiry&amp;' +
  'body=Product%20name%3A%0AWebsite%3A%0APlacement%20goal%3A%0A';

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
const verifiedById = new Map(verifiedRoutes.map((tool) => [tool.id, tool]));

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

let toolAffiliateFilesChanged = 0;
let toolLinksMonetized = 0;
let sponsorshipFilesChanged = 0;
let sponsorshipCtasNormalized = 0;
const legacySponsorshipAnchor =
  /<a(?<before>[^>]*)href="\/#submit"(?<after>[^>]*)>(?<label>[^<]*\$49\/yr[^<]*)<\/a>/gi;

for (const filename of fs.readdirSync(TOOL_DIR)) {
  if (!filename.endsWith('.html')) continue;

  const filePath = path.join(TOOL_DIR, filename);
  const original = fs.readFileSync(filePath, 'utf8');
  let updated = original;
  let affiliateChangesInFile = 0;
  let normalizedInFile = 0;

  const toolId = filename.slice(0, -5);
  const tool = verifiedById.get(toolId);
  if (tool) {
    const officialPatterns = [
      new RegExp(
        `<a data-cta="official" href="${escapeRegExp(tool.official_url)}" target="_blank" rel="noopener noreferrer"`,
        'g'
      ),
      new RegExp(
        `<a href="${escapeRegExp(tool.official_url)}" target="_blank" rel="noopener noreferrer"`,
        'g'
      ),
    ];

    for (const pattern of officialPatterns) {
      const matches = updated.match(pattern)?.length || 0;
      if (!matches) continue;
      const replacement =
        `<a data-cta="affiliate" data-tool-id="${tool.id}" data-cta-source="tool-primary-auto" ` +
        `href="${tool.affiliate_url}" target="_blank" rel="sponsored noopener noreferrer"`;
      updated = updated.replace(pattern, () => replacement);
      affiliateChangesInFile += matches;
      toolLinksMonetized += matches;
    }

    const existingAffiliatePattern = new RegExp(
      `<a href="${escapeRegExp(tool.affiliate_url)}" target="_blank" rel="[^"]*"`,
      'g'
    );
    const unattributedMatches = updated.match(existingAffiliatePattern)?.length || 0;
    if (unattributedMatches) {
      const replacement =
        `<a data-cta="affiliate" data-tool-id="${tool.id}" data-cta-source="tool-existing-affiliate-auto" ` +
        `href="${tool.affiliate_url}" target="_blank" rel="sponsored noopener noreferrer"`;
      updated = updated.replace(existingAffiliatePattern, () => replacement);
      affiliateChangesInFile += unattributedMatches;
      toolLinksMonetized += unattributedMatches;
    }

    if (affiliateChangesInFile && !updated.includes('/affiliate-attribution.js')) {
      updated = updated.replace(
        /\s*<\/head>/,
        '\n    <script defer src="/affiliate-attribution.js"></script>\n  </head>'
      );
    }

    if (affiliateChangesInFile && !updated.includes('data-affiliate-disclosure="tool"')) {
      updated = updated.replace(/(?=\s*<\/main>)/, `${TOOL_DISCLOSURE}\n`);
    }
  }

  updated = updated.replace(legacySponsorshipAnchor, (...args) => {
    const groups = args.at(-1);
    normalizedInFile += 1;
    return (
      `<a${groups.before}data-cta="sponsorship-inquiry" data-cta-source="tool-legacy-normalized" ` +
      `href="${SPONSORSHIP_MAILTO}"${groups.after}>Request $49 sponsored placement →</a>`
    );
  });

  if (updated === original) continue;

  fs.writeFileSync(filePath, updated, 'utf8');
  if (affiliateChangesInFile) toolAffiliateFilesChanged += 1;
  if (normalizedInFile) sponsorshipFilesChanged += 1;
  sponsorshipCtasNormalized += normalizedInFile;
}

const breakdown = [...changedByTool.entries()]
  .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  .map(([toolId, count]) => `${toolId}:${count}`)
  .join(', ');

console.log(
  `monetize_verified_compare_links: verified_routes=${verifiedRoutes.length} ` +
  `files_changed=${filesChanged} links_monetized=${linksMonetized} links_attributed=${linksAttributed} ` +
  `tool_affiliate_files_changed=${toolAffiliateFilesChanged} tool_links_monetized=${toolLinksMonetized} ` +
  `sponsorship_files_changed=${sponsorshipFilesChanged} sponsorship_ctas_normalized=${sponsorshipCtasNormalized}` +
  (breakdown ? ` [${breakdown}]` : '')
);
