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
  },
  {
    id: 'aweber',
    filename: 'aweber.html',
    sources: ['aweber-pricing-hero', 'aweber-pricing-bottom'],
    deepUrl: 'https://www.aweber.com/pricing.htm?id=561868',
  },
];

let changed = 0;
for (const route of routes) {
  const evidence = approvedTracking.get(route.id);
  if (!evidence) throw new Error(`${route.id}: missing approved-tracking evidence`);
  const allowed = new Set(evidence.allowed_cta_urls || [evidence.exact_tracking_url]);
  if (!allowed.has(route.deepUrl)) {
    throw new Error(`${route.id}: deep URL is not explicitly permitted by approved-tracking evidence`);
  }

  const file = path.join(TOOL_DIR, route.filename);
  let html = fs.readFileSync(file, 'utf8');
  const original = html;

  for (const source of route.sources) {
    const anchorPattern = new RegExp(`<a\\b(?=[^>]*data-cta="affiliate")(?=[^>]*data-tool-id="${route.id}")(?=[^>]*data-cta-source="${source}")[^>]*>`, 'g');
    const matches = [...html.matchAll(anchorPattern)];
    if (matches.length !== 1) {
      throw new Error(`${route.id}: expected exactly one ${source} affiliate CTA, found ${matches.length}`);
    }
    const anchor = matches[0][0];
    const href = anchor.match(/href="([^"]+)"/)?.[1]?.replaceAll('&amp;', '&');
    if (href !== evidence.exact_tracking_url && href !== route.deepUrl) {
      throw new Error(`${route.id}: refusing to rewrite unexpected href for ${source}: ${href}`);
    }
    if (href === route.deepUrl) continue;
    const replacement = anchor.replace(/href="[^"]+"/, `href="${route.deepUrl}"`);
    html = html.replace(anchor, replacement);
  }

  if (html !== original) {
    fs.writeFileSync(file, html, 'utf8');
    changed += 1;
  }
}

console.log(`apply_verified_buyer_deeplinks: changed=${changed} routes=${routes.length}`);
