import { approvedTracking } from './approved_tracking_evidence.mjs';
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

// Later first-party or vendor-human evidence can authorize exact buyer-intent
// deeplinks/traffic tags even when the program predates or sits outside the
// legacy approved-tracking baseline. Never generate arbitrary variants here;
// preserve only the exact URLs backed by that evidence.
const vendorApprovedDeepLinks = new Map([
  ['getgenie', new Set(['https://getgenie.ai/pricing/?rui=3921'])],
  ['systeme-io', new Set([
    'https://systeme.io/?sa=sa0279779913657b281b5d2c1fed58680413f14dca&tk=coshuma-tool-free',
    'https://systeme.io/pricing?sa=sa0279779913657b281b5d2c1fed58680413f14dca&tk=coshuma-tool-pricing',
    'https://systeme.io/?sa=sa0279779913657b281b5d2c1fed58680413f14dca&tk=coshuma-tool-bottom-free',
  ])],
]);

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

// Normalize existing hand-authored CTAs as well as newly monetized anchors.
// Preserve vendor-approved buyer-intent deeplinks instead of forcing every CTA
// back to the account's default tracking URL. This keeps exact pricing/trial routes
// only when first-party or vendor-human evidence explicitly allowlists them.
for (const [directory, type] of [[TOOL_DIR, 'tool'], [COMPARE_DIR, 'compare']]) {
  for (const filename of fs.readdirSync(directory).filter(name => name.endsWith('.html'))) {
    const file = path.join(directory, filename);
    const original = fs.readFileSync(file, 'utf8');
    let relevant = false;
    let updated = original.replace(/<a\b[^>]*>/g, anchor => {
      const href = anchor.match(/href="([^"]+)"/)?.[1]?.replaceAll('&amp;', '&');
      const id = anchor.match(/data-tool-id="([^"]+)"/)?.[1] ||
        [...approvedTracking.values()].find(item => item.exact_tracking_url === href || item.allowed_cta_urls?.includes(href))?.id ||
        verifiedRoutes.find(item => item.affiliate_url === href)?.id;
      const approvedItem = approvedTracking.get(id);
      const verifiedTool = verifiedById.get(id);
      const exactTrackingUrl = approvedItem?.exact_tracking_url || verifiedTool?.affiliate_url;
      if (!exactTrackingUrl || !anchor.includes('data-cta="affiliate"')) return anchor;

      const allowedUrls = new Set(
        Array.isArray(approvedItem?.allowed_cta_urls) && approvedItem.allowed_cta_urls.length
          ? approvedItem.allowed_cta_urls
          : [exactTrackingUrl]
      );
      allowedUrls.add(exactTrackingUrl);
      for (const approvedUrl of vendorApprovedDeepLinks.get(id) || []) allowedUrls.add(approvedUrl);

      relevant = true;
      if (!anchor.includes('data-tool-id=')) anchor = anchor.replace('<a ', '<a data-tool-id="' + id + '" ');
      const normalizedHref = href && allowedUrls.has(href) ? href : exactTrackingUrl;
      anchor = anchor.replace(/href="[^"]*"/, () => 'href="' + normalizedHref + '"');
      if (!anchor.includes('data-cta-source=')) anchor = anchor.replace('<a ', '<a data-cta-source="' + type + '-existing-affiliate-auto" ');
      return anchor;
    });
    if (relevant && !updated.includes('/affiliate-attribution.js')) updated = updated.replace('</head>', '<script defer src="/affiliate-attribution.js"></script>\n</head>');
    if (relevant && !updated.includes('data-affiliate-disclosure="' + type + '"')) {
      if (/Affiliate disclosure:/i.test(updated)) updated = updated.replace(/<p([^>]*)>(\s*Affiliate disclosure:)/i, '<p data-affiliate-disclosure="' + type + '"$1>$2');
      else updated = updated.replace('</main>', (type === 'tool' ? TOOL_DISCLOSURE : DISCLOSURE) + '\n</main>');
    }
    if (updated !== original) fs.writeFileSync(file, updated);
  }
}