import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { approvedTracking } from './approved_tracking_evidence.mjs';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = path.resolve(SCRIPT_DIR, '..');
const TOOL_DIR = path.join(PROJECT_DIR, 'public', 'tool');
const COMPARE_DIR = path.join(PROJECT_DIR, 'public', 'compare');

const aweberDeepLinkConfig = {
  id: 'aweber',
  authoritativeUrl: 'https://www.aweber.com/easy-email.htm?id=561868',
  allowedCtaUrls: [
    'https://www.aweber.com/easy-email.htm?id=561868',
    'https://www.aweber.com/pricing.htm?id=561868',
  ],
  deepUrl: 'https://www.aweber.com/pricing.htm?id=561868',
  evidenceFile: 'data/aweber-buyer-deeplink-evidence-2026-09-09.md',
};

const routes = [
  {
    id: 'typedesk',
    filename: 'typedesk.html',
    sources: ['typedesk-pricing-deeplink'],
    deepUrl: 'https://www.typedesk.com/pricing?via=sangkwon',
    evidenceFile: 'data/typedesk-approved-tracking-2026-09-09.md',
  },
  {
    ...aweberDeepLinkConfig,
    filename: 'aweber.html',
    sources: ['aweber-pricing-hero', 'aweber-pricing-bottom'],
  },
  {
    ...aweberDeepLinkConfig,
    filename: 'beefree.html',
    sources: [
      'beefree_hero_email_marketing_alternative',
      'beefree_decision_email_marketing_alternative',
    ],
  },
  {
    ...aweberDeepLinkConfig,
    filename: 'sanebox.html',
    sources: ['sanebox-intent-aweber'],
  },
];

let changed = 0;
for (const route of routes) {
  const evidencePath = path.join(PROJECT_DIR, route.evidenceFile);
  if (!fs.existsSync(evidencePath)) {
    throw new Error(`${route.id}: missing deep-link evidence file ${route.evidenceFile}`);
  }

  const primaryEvidence = approvedTracking.get(route.id);
  const authoritativeUrl = primaryEvidence?.exact_tracking_url || route.authoritativeUrl;
  const allowed = new Set(
    primaryEvidence?.allowed_cta_urls || route.allowedCtaUrls || (authoritativeUrl ? [authoritativeUrl] : [])
  );

  if (!authoritativeUrl) {
    throw new Error(`${route.id}: missing authoritative account tracking URL`);
  }
  if (!allowed.has(authoritativeUrl)) {
    throw new Error(`${route.id}: allowed CTA URLs must retain the authoritative account tracking URL`);
  }
  if (!allowed.has(route.deepUrl)) {
    throw new Error(`${route.id}: deep URL is not explicitly permitted by evidence`);
  }

  const file = path.join(TOOL_DIR, route.filename);
  let html = fs.readFileSync(file, 'utf8');
  const original = html;

  for (const source of route.sources) {
    const anchorPattern = new RegExp(
      `<a\\b(?=[^>]*data-cta="affiliate")(?=[^>]*data-tool-id="${route.id}")(?=[^>]*data-cta-source="${source}")[^>]*>`,
      'g'
    );
    const matches = [...html.matchAll(anchorPattern)];
    if (matches.length === 0) {
      throw new Error(`${route.id}: missing expected ${source} affiliate CTA in ${route.filename}`);
    }

    for (const match of matches) {
      const anchor = match[0];
      const href = anchor.match(/href="([^"]+)"/)?.[1]?.replaceAll('&amp;', '&');
      if (!href || !allowed.has(href)) {
        throw new Error(`${route.id}: refusing to rewrite unapproved href for ${source} in ${route.filename}: ${href}`);
      }
      if (href === route.deepUrl) continue;
      html = html.replace(anchor, anchor.replace(/href="[^"]+"/, `href="${route.deepUrl}"`));
    }
  }

  if (html !== original) {
    fs.writeFileSync(file, html, 'utf8');
    changed += 1;
  }
}

// Teachable supplied COSHUMA with a separate PartnerStack route specifically for
// the affiliate-only 30-day free trial. Once the normal comparison monetizer has
// converted generated Teachable buttons into attributed affiliate CTAs, prefer
// that lower-friction vendor-issued offer on comparison pages. The authoritative
// default PartnerStack URL remains stored in tools.json and approvedTracking.
let teachableCompareFilesChanged = 0;
let teachableCompareCtasChanged = 0;
const teachable = approvedTracking.get('teachable');
if (teachable) {
  const authoritativeUrl = teachable.exact_tracking_url;
  const trialUrl = teachable.extended_trial_tracking_url;
  const allowed = new Set(teachable.allowed_cta_urls || [authoritativeUrl]);
  if (!authoritativeUrl || !trialUrl) {
    throw new Error('teachable: missing authoritative or 30-day trial tracking URL');
  }
  if (!allowed.has(authoritativeUrl) || !allowed.has(trialUrl)) {
    throw new Error('teachable: 30-day trial URL is not explicitly allowlisted by vendor evidence');
  }

  for (const filename of fs.readdirSync(COMPARE_DIR).filter((name) => name.endsWith('.html'))) {
    const file = path.join(COMPARE_DIR, filename);
    let html = fs.readFileSync(file, 'utf8');
    if (!html.includes('data-tool-id="teachable"') || !html.includes('data-cta="affiliate"')) continue;
    const original = html;

    html = html.replace(/<a\b[^>]*data-cta="affiliate"[^>]*data-tool-id="teachable"[^>]*>[^<]*<\/a>/g, (fullAnchor) => {
      const href = fullAnchor.match(/href="([^"]+)"/)?.[1]?.replaceAll('&amp;', '&');
      if (!href || !allowed.has(href)) {
        throw new Error(`teachable: refusing unapproved comparison CTA in ${filename}: ${href}`);
      }
      let next = fullAnchor.replace(/href="[^"]+"/, `href="${trialUrl}"`);
      if (/data-cta-source="[^"]+"/.test(next)) {
        next = next.replace(/data-cta-source="[^"]+"/, 'data-cta-source="compare-teachable-30day-trial"');
      } else {
        next = next.replace('<a ', '<a data-cta-source="compare-teachable-30day-trial" ');
      }
      next = next.replace(/>Get Teachable →<\/a>$/, '>Start Teachable 30-day trial →</a>');
      next = next.replace(/>Try Teachable →<\/a>$/, '>Start Teachable 30-day trial →</a>');
      teachableCompareCtasChanged += 1;
      return next;
    });

    if (html !== original) {
      if (!html.includes('/affiliate-attribution.js')) {
        throw new Error(`teachable: comparison attribution script missing in ${filename}`);
      }
      if (!/affiliate disclosure/i.test(html)) {
        throw new Error(`teachable: affiliate disclosure missing in ${filename}`);
      }
      fs.writeFileSync(file, html, 'utf8');
      teachableCompareFilesChanged += 1;
    }
  }
}

console.log(
  `apply_verified_buyer_deeplinks: changed=${changed} routes=${routes.length} ` +
  `teachable_compare_files_changed=${teachableCompareFilesChanged} ` +
  `teachable_compare_ctas_changed=${teachableCompareCtasChanged}`
);
