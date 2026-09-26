import './reconcile_sanebox_approved_tracking.mjs';
import fs from './affiliate_state_fs.mjs';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { approvedTracking } from './approved_tracking_evidence.mjs';

const files = ['data/tools.json', 'data/tools.next.json'];
const originals = files.map((f) => fs.readFileSync(f, 'utf8'));

function checkStoredState() {
  for (const f of files) {
    const tools = JSON.parse(fs.readFileSync(f, 'utf8'));
    for (const [id, evidence] of approvedTracking) {
      const tool = tools.find((item) => item.id === id);
      assert.equal(tool?.affiliate_url, evidence.exact_tracking_url, id);
      assert.equal(tool.affiliate_status, 'approved_tracking', id);
      assert.equal(tool.affiliate_verified, true, id);
      assert.ok(tool.affiliate_verified_at, id);
      assert.ok(tool.affiliate_evidence_markers?.length, id);
    }
  }
}

checkStoredState();
try {
  for (let n = 0; n < 2; n += 1) {
    execFileSync(process.execPath, ['scripts/sync_verified_affiliates.mjs']);
    execFileSync(process.execPath, ['scripts/sync_latest_affiliate_states.mjs']);
    execFileSync(process.execPath, ['scripts/reconcile_sanebox_approved_tracking.mjs']);
    checkStoredState();
    for (let j = 0; j < files.length; j += 1) {
      const before = JSON.parse(originals[j]);
      const after = JSON.parse(fs.readFileSync(files[j], 'utf8'));
      for (const id of approvedTracking.keys()) {
        assert.deepEqual(after.find((tool) => tool.id === id), before.find((tool) => tool.id === id), `sync must preserve ${id}`);
      }
    }
  }
} finally {
  files.forEach((f, j) => fs.writeFileSync(f, originals[j]));
}

const outreach = JSON.parse(fs.readFileSync('data/affiliate_outreach_state.json', 'utf8')).programs;
const saneboxCredit = outreach.sanebox;
assert.equal(saneboxCredit.optional_trial_credit_status, 'vendor_confirmed');
assert.equal(saneboxCredit.optional_trial_credit_amount_usd, 25);
assert.equal(saneboxCredit.optional_trial_credit_confirmation_message_id, '1a0c4afff48e68ce');
assert.equal(saneboxCredit.optional_trial_credit_promo_url, 'https://try.sanebox.com/coshuma');
assert.equal(saneboxCredit.tracking_url, 'https://try.sanebox.com/s1ooqjj73rpz');
const queue = JSON.parse(fs.readFileSync('data/browser_required_queue.json', 'utf8'));
const dir = process.argv[2] || 'dist';
const decode = (value) => value.replaceAll('&amp;', '&');

function matchingHtmlPages(subdir, id, allowedCtaUrls) {
  const root = `${dir}/${subdir}`;
  if (!fs.existsSync(root)) return [];
  return fs.readdirSync(root)
    .filter((f) => f.endsWith('.html'))
    .map((f) => [`${subdir}/${f}`, fs.readFileSync(`${root}/${f}`, 'utf8')])
    .filter(([, html]) => {
      const hasAffiliateAnchor = [...html.matchAll(/<a\b[^>]*>/g)].some((match) => {
        const anchor = match[0];
        return anchor.includes(`data-tool-id="${id}"`) && anchor.includes('data-cta="affiliate"');
      });
      const hasAllowedUrl = [...allowedCtaUrls].some((url) => decode(html).includes(url));
      return hasAffiliateAnchor || hasAllowedUrl;
    });
}

for (const [id, evidence] of approvedTracking) {
  assert.equal(outreach[id].status, 'approved_tracking');
  assert.equal(outreach[id].tracking_url, evidence.exact_tracking_url);
  assert.ok(queue.some((item) => item.affiliate_status === 'approved_tracking' && item.exact_tracking_url === evidence.exact_tracking_url));

  const allowedCtaUrls = new Set(
    Array.isArray(evidence.allowed_cta_urls) && evidence.allowed_cta_urls.length
      ? evidence.allowed_cta_urls
      : [evidence.exact_tracking_url]
  );
  assert.ok(allowedCtaUrls.has(evidence.exact_tracking_url), `${id}: allowed CTA URLs must retain authoritative exact URL`);

  const toolPage = fs.readFileSync(`${dir}/tool/${id}.html`, 'utf8');
  const pages = [
    [`tool/${id}.html`, toolPage],
    ...matchingHtmlPages('compare', id, allowedCtaUrls),
    ...matchingHtmlPages('best', id, allowedCtaUrls),
  ];

  let count = 0;
  for (const [file, html] of pages) {
    const anchors = [...html.matchAll(/<a\b[^>]*>/g)]
      .map((match) => match[0])
      .filter((anchor) => {
        const decoded = decode(anchor);
        const href = decoded.match(/href="([^"]+)"/)?.[1];
        return (
          (anchor.includes(`data-tool-id="${id}"`) && anchor.includes('data-cta="affiliate"')) ||
          (href && allowedCtaUrls.has(href))
        );
      });

    assert.ok(anchors.length, `${id}: no CTA on ${file}`);
    for (const anchor of anchors) {
      const decoded = decode(anchor);
      const href = decoded.match(/href="([^"]+)"/)?.[1];
      assert.ok(href && allowedCtaUrls.has(href), `${file}: unapproved affiliate CTA URL ${href}`);
      assert.ok(anchor.includes('data-cta="affiliate"'), file);
      assert.ok(anchor.includes('data-cta-source='), file);
      assert.ok(anchor.includes('sponsored'), file);
      count += 1;
    }
    assert.ok(html.includes('/affiliate-attribution.js'), `${file}: missing affiliate attribution collector`);
    const pageDisclosureMarkers = html.match(/data-affiliate-disclosure="page"/g) || [];
    const pageDisclosureText = html.match(/Affiliate\s+disclosure\s*:/gi) || [];
    assert.equal(pageDisclosureMarkers.length, 1, `${file}: affiliate page must contain exactly one page-level disclosure marker`);
    assert.equal(pageDisclosureText.length, 1, `${file}: affiliate page must contain exactly one visible affiliate disclosure`);
    const firstDisclosure = html.indexOf('data-affiliate-disclosure="page"');
    const firstAffiliateCta = html.search(/<a\b[^>]*data-cta="affiliate"/i);
    assert.ok(firstDisclosure >= 0 && firstAffiliateCta >= 0 && firstDisclosure < firstAffiliateCta, `${file}: disclosure must appear before the first affiliate CTA`);
  }

  console.log(`${id}: ${count} attributed CTAs across ${pages.length} pages (tool + compare + best)`);
}

const home = fs.readFileSync(`${dir}/index.html`, 'utf8');
assert.equal((home.match(/data-site-affiliate-disclosure="global"/g) || []).length, 1, 'homepage must contain exactly one global affiliate disclosure marker');
assert.equal((home.match(/Affiliate\s+disclosure\s*:/gi) || []).length, 1, 'homepage must contain exactly one general affiliate disclosure');
assert.ok(fs.existsSync(`${dir}/affiliate-disclosure.html`), 'dedicated affiliate disclosure policy page must remain available');

console.log('PASS: authoritative exact state is preserved; built affiliate CTAs use only exact or explicitly evidence-backed URLs with attribution; homepage has one global disclosure and every affiliate page has one disclosure before its first affiliate CTA.');
