import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const CLAAP = path.join(ROOT, 'public', 'tool', 'claap.html');
const HUB = path.join(ROOT, 'public', 'best', 'index.html');

function sanitizeClaap(html) {
  html = html
    .replaceAll('Partner feedback + official pricing checked Sep 15, 2026', 'Product & pricing checked Sep 15, 2026')
    .replaceAll('Start Claap with verified tracking →', 'Try Claap →')
    .replaceAll('Try Claap with verified tracking →', 'Try Claap →')
    .replaceAll(
      'Affiliate disclosure:</strong> COSHUMA may earn a commission if you purchase through a verified Claap affiliate link, at no extra cost to you. This does not affect our editorial assessment.',
      'Affiliate disclosure:</strong> COSHUMA may earn a commission from eligible purchases through links on this page, at no extra cost to you. This does not affect our editorial assessment.',
    )
    .replaceAll(
      "this review uses Claap's current official product/security pages plus direct feedback from Claap affiliate manager Lamia Karmaly.",
      "this review uses Claap's current official product, pricing and security information.",
    );

  // Remove operations-only affiliate status paragraphs while preserving the
  // exact outbound URL, sponsored rel attributes, CTA analytics and disclosure.
  html = html.replace(
    /\s*<p\b[^>]*>\s*Affiliate status:\s*verified\.[\s\S]*?<\/p>/gi,
    '',
  );

  return html;
}

function sanitizeHub(html) {
  return html
    .replaceAll('Claap Pricing & Verified Partner Guide', 'Claap Pricing & Buyer Guide')
    .replaceAll('Claap Pricing & Verified Partner Route', 'Claap Pricing & Buyer Guide')
    .replaceAll('AI meetings · verified partner route', 'AI meetings · pricing and plan guide')
    .replaceAll(
      "Compare Claap's free/trial entry and plan fit, then continue through COSHUMA's vendor-verified customer tracking route if the workflow fits. Confirm final pricing and any buyer offer on Claap before purchase.",
      "Compare Claap's free entry, current pricing and plan fit before choosing whether to upgrade. Confirm final pricing on Claap before purchase.",
    );
}

if (fs.existsSync(CLAAP)) {
  const before = fs.readFileSync(CLAAP, 'utf8');
  const after = sanitizeClaap(before);
  fs.writeFileSync(CLAAP, after);

  const visibleLeaks = [
    'Affiliate status: verified.',
    'Claap affiliate manager Lamia Karmaly',
    'with verified tracking →',
  ];
  for (const phrase of visibleLeaks) {
    if (after.includes(phrase)) throw new Error(`Claap public-copy leak remains: ${phrase}`);
  }
}

if (fs.existsSync(HUB)) {
  const before = fs.readFileSync(HUB, 'utf8');
  const after = sanitizeHub(before);
  fs.writeFileSync(HUB, after);
}

console.log('claap-final-public-copy-v1');
