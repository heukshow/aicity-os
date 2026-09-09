import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { approvedTracking } from './approved_tracking_evidence.mjs';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = path.resolve(SCRIPT_DIR, '..');
const TOOL_DIR = path.join(PROJECT_DIR, 'public', 'tool');

const routes = [
  {
    id: 'typedesk',
    filename: 'typedesk.html',
    sources: ['typedesk-pricing-deeplink'],
    deepUrl: 'https://www.typedesk.com/pricing?via=sangkwon',
    evidenceFile: 'data/typedesk-approved-tracking-2026-09-09.md',
  },
  {
    id: 'aweber',
    filename: 'aweber.html',
    sources: ['aweber-pricing-hero', 'aweber-pricing-bottom'],
    authoritativeUrl: 'https://www.aweber.com/easy-email.htm?id=561868',
    allowedCtaUrls: [
      'https://www.aweber.com/easy-email.htm?id=561868',
      'https://www.aweber.com/pricing.htm?id=561868',
    ],
    deepUrl: 'https://www.aweber.com/pricing.htm?id=561868',
    evidenceFile: 'data/aweber-buyer-deeplink-evidence-2026-09-09.md',
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
      throw new Error(`${route.id}: missing expected ${source} affiliate CTA`);
    }

    for (const match of matches) {
      const anchor = match[0];
      const href = anchor.match(/href="([^"]+)"/)?.[1]?.replaceAll('&amp;', '&');
      if (!href || !allowed.has(href)) {
        throw new Error(`${route.id}: refusing to rewrite unapproved href for ${source}: ${href}`);
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

console.log(`apply_verified_buyer_deeplinks: changed=${changed} routes=${routes.length}`);
