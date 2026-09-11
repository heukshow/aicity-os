import fs from 'node:fs';
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
const queue = JSON.parse(fs.readFileSync('data/browser_required_queue.json', 'utf8'));
const dir = process.argv[2] || 'dist';
const decode = (value) => value.replaceAll('&amp;', '&');

function matchingHtmlPages(subdir, id, allowedCtaUrls) {
  const root = `${dir}/${subdir}`;
  if (!fs.existsSync(root)) return [];
  return fs.readdirSync(root)
    .filter((f) => f.endsWith('.html'))
    .map((f) => [`${subdir}/${f}`, fs.readFileSync(`${root}/${f}`, 'utf8')])
    .filter(([, html]) => html.includes(`data-tool-id="${id}"`) || [...allowedCtaUrls].some((url) => decode(html).includes(url)));
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
    assert.ok(/affiliate disclosure/i.test(html), `${file}: missing affiliate disclosure`);
  }

  console.log(`${id}: ${count} attributed CTAs across ${pages.length} pages (tool + compare + best)`);
}

console.log('PASS: authoritative exact state is preserved; built tool, comparison, and buyer-guide CTAs use only exact or explicitly evidence-backed URLs with attribution.');
