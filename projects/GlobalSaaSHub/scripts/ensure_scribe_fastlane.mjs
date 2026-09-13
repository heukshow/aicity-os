import fs from 'node:fs';

const checkedAt = '2026-09-14T05:40:00+09:00';
const scribe = {
  id: 'scribe',
  name: 'Scribe',
  category: 'workflow_auto',
  category_display: 'Workflow Automation',
  description: 'Process documentation software that captures workflows and turns them into step-by-step visual guides with screenshots and text.',
  affiliate_url: null,
  pricing: 'Free plan available; Pro Personal, Pro Team and Enterprise plans available',
  key_features: [
    'Automatic step-by-step workflow capture',
    'Browser capture on all plans',
    'Desktop capture on Pro',
    'Screenshot editing and redaction',
    'Link sharing, embeds and exports',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=scribehow.com&sz=128',
  primary_category: 'workflow_auto',
  comparison_group: 'process_documentation',
  official_url: 'https://scribehow.com/',
  pricing_source_url: 'https://scribehow.com/pricing',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly or annual depending on plan',
  evidence_source_type: 'official_product_and_support_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://support.scribehow.com/hc/en-us/articles/34916903648029-Does-Scribe-have-an-affiliate-program',
  affiliate_verified: false,
  affiliate_status: 'outreach_sent',
  affiliate_source_url: 'https://support.scribehow.com/hc/en-us/articles/34916903648029-Does-Scribe-have-an-affiliate-program',
  affiliate_verified_at: checkedAt,
  affiliate_evidence_markers: [
    'Official Scribe Support Portal confirms an affiliate program exists and is open to everyone.',
    'Gmail all-mail search found no prior COSHUMA Scribe application, approval, rejection or issued customer tracking URL before outreach.',
    'COSHUMA sent one verification inquiry to support@scribehow.com on 2026-09-14; Gmail message id 1a09c7a8e9029ff0.',
    'Exact affiliate application destination and account-specific customer tracking URL remain unverified; do not publish a guessed Rewardful or generic signup URL.',
  ],
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === scribe.id);
  if (existing) Object.assign(existing, scribe);
  else tools.push(scribe);

  const supademo = tools.find((tool) => tool.id === 'supademo');
  if (supademo) {
    supademo.affiliate_url = null;
    supademo.affiliate_verified = false;
    supademo.affiliate_status = 'outreach_sent';
    supademo.affiliate_verified_at = checkedAt;
    supademo.affiliate_evidence_markers = [
      ...(Array.isArray(supademo.affiliate_evidence_markers) ? supademo.affiliate_evidence_markers : []),
      '2026-09-13: COSHUMA affiliate inquiry sent to support@supademo.com (Gmail 1a09b43356bc3947).',
      'Supademo Intercom acknowledged receipt (Gmail 1a09b43b5ba55b97); human vendor response remains pending.',
      'No exact customer tracking URL, approval, signup, paid customer, commission or revenue is verified.',
    ];
  }
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-14';
outreach.programs ||= {};
outreach.programs.scribe = {
  status: 'outreach_sent',
  contact: 'support@scribehow.com',
  gmail_message_id: '1a09c7a8e9029ff0',
  sender: 'support@coshuma.com',
  tracking_url: null,
  official_program_url: 'https://support.scribehow.com/hc/en-us/articles/34916903648029-Does-Scribe-have-an-affiliate-program',
  checked_at: checkedAt,
  note: 'Official Scribe support confirms an affiliate program, but the exact signup destination is still being vendor-verified because unrelated products share the Scribe name. One verification inquiry was sent; do not duplicate outreach. No customer tracking URL is verified.',
};
if (outreach.programs.supademo) {
  Object.assign(outreach.programs.supademo, {
    status: 'outreach_sent',
    tracking_url: null,
    account: 'support@coshuma.com',
    gmail_message_id: '1a09b43356bc3947',
    acknowledgement_message_id: '1a09b43b5ba55b97',
    checked_at: checkedAt,
    note: 'Supademo received the 2026-09-13 COSHUMA affiliate inquiry and acknowledged receipt via Intercom. Human vendor response is pending. Do not resend or infer formal approval/tracking/revenue.',
  });
}
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
for (const item of queue) {
  if (item.tool_id === 'supademo' || String(item.id || '').startsWith('supademo-')) {
    item.status = 'waiting_vendor_response';
    item.priority = 'normal';
    item.user_action_required = false;
    item.reason = 'Supademo received COSHUMA affiliate outreach and acknowledged receipt. The old embedded-form technical failure is superseded; the next dependency is a human vendor response, not browser/user action.';
    item.next_action = 'Wait for a human Supademo reply, then re-check the full Gmail thread, sent mail, spam and repository state before any follow-up.';
    item.verified_at = checkedAt;
  }
}
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/scribe.html',
  'https://coshuma.com/best/scribe-for-sop-documentation.html',
  'https://coshuma.com/compare/scribe-vs-supademo.html',
];
const sitemapPath = 'public/sitemap.xml';
let sitemap = fs.readFileSync(sitemapPath, 'utf8');
for (const url of urls) {
  if (!sitemap.includes(`<loc>${url}</loc>`)) {
    sitemap = sitemap.replace('</urlset>', `  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n</urlset>`);
  }
}
fs.writeFileSync(sitemapPath, sitemap);

const llmsPath = 'public/llms.txt';
let llms = fs.readFileSync(llmsPath, 'utf8');
if (!llms.includes('https://coshuma.com/tool/scribe.html')) {
  llms += '\n## Process documentation\n\n- https://coshuma.com/tool/scribe.html — Scribe pricing, process-capture and plan buyer guide\n- https://coshuma.com/best/scribe-for-sop-documentation.html — Scribe for SOP documentation decision guide\n- https://coshuma.com/compare/scribe-vs-supademo.html — Scribe vs Supademo process-docs vs interactive-demo comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-scribe-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-purple-500/25 bg-purple-500/5 p-5"><div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Process documentation</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-purple-300" href="/best/scribe-for-sop-documentation.html">Scribe for SOP documentation</a> · <a class="font-bold text-white hover:text-purple-300" href="/tool/scribe.html">Scribe pricing & review</a> · <a class="font-bold text-white hover:text-purple-300" href="/compare/scribe-vs-supademo.html">Scribe vs Supademo</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'index.html']) {
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-scribe-fastlane="2026-09-14"')) {
    html = html.includes('</main>') ? html.replace('</main>', `${hubBlock}</main>`) : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

console.log('Scribe fast-lane state/pages discoverability and Supademo waiting state ensured');