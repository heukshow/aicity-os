import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-09-15T04:12:19+09:00';
const supademoCheckedAt = '2026-09-26T16:38:43Z';
const supademoProgramUrl = 'https://supademo.com/affiliates';
const supademoApplicationUrl = 'https://eu.makeforms.io/k1ibmll/';
const supademoEvidenceFile = 'data/supademo-form-route-2026-09-24.md';
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
  affiliate_status: 'temporarily_closed',
  affiliate_source_url: 'https://support.scribehow.com/hc/en-us/articles/34916903648029-Does-Scribe-have-an-affiliate-program',
  affiliate_verified_at: checkedAt,
  affiliate_evidence_markers: [
    '2026-09-14: Scribe Support agent Matt Sanz confirmed that Scribe is not accepting new affiliate applications while its affiliate program is being refreshed and restructured.',
    'The prior COSHUMA inquiry is complete. Do not reapply or send another inquiry unless Scribe itself sends a new human update that applications have reopened.',
    'No COSHUMA approval or account-specific customer tracking URL was issued. Keep affiliate_url null and do not infer clicks, signups, customers, commissions, payouts or revenue.',
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
    supademo.affiliate_status = 'application_submitted';
    supademo.affiliate_source_url = supademoProgramUrl;
    supademo.affiliate_workflow_url = supademoApplicationUrl;
    supademo.affiliate_verified_at = supademoCheckedAt;
    supademo.affiliate_status_checked_at = supademoCheckedAt;
    supademo.application_state = 'application_submitted';
    supademo.review_state = 'pending_review';
    supademo.do_not_reapply = true;
    supademo.affiliate_next_action = 'Await Supademo review of the existing formal application. Do not reapply. Record approval, rejection, or an exact vendor-issued customer tracking URL only from new direct evidence.';
    const supademoMarkers = [
      ...(Array.isArray(supademo.affiliate_evidence_markers) ? supademo.affiliate_evidence_markers.filter((marker) => !/connection reset|Resume this exact official form|not a formal affiliate application submission|Submit the official Supademo Affiliate Request|browser_required_application_form|eu\.makeforms\.co\/xtyzhps/i.test(String(marker))) : []),
      '2026-09-13: COSHUMA affiliate inquiry sent to support@supademo.com (Gmail 1a09b43356bc3947).',
      'Supademo Intercom acknowledged receipt (Gmail 1a09b43b5ba55b97).',
      '2026-09-23: Supademo support agent Mohit replied (Gmail 1a0d02cddb650402) that support does not handle affiliate requests directly and instructed COSHUMA to use the formal request form.',
      `Current official Supademo affiliate page links to the Affiliate Request form at ${supademoApplicationUrl}.`,
      '2026-09-26T16:38:43Z: the official Affiliate Request form confirmed “Thanks for your submission!” and review in 1-2 business days (#292 comment 5847971116). Application is submitted and pending review; no approval or exact customer tracking URL is verified.',
      supademoEvidenceFile,
    ];
    supademo.affiliate_evidence_markers = [...new Set(supademoMarkers)];
  }
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-26';
outreach.programs ||= {};
outreach.programs.scribe = {
  status: 'temporarily_closed',
  application_state: 'vendor_not_accepting_new_affiliate_applications',
  contact: 'support@scribehow.com',
  gmail_message_id: '1a09c7a8e9029ff0',
  vendor_response_message_id: '1a0a155a6b7de938',
  sender: 'support@coshuma.com',
  tracking_url: null,
  official_program_url: 'https://support.scribehow.com/hc/en-us/articles/34916903648029-Does-Scribe-have-an-affiliate-program',
  github_issue: 525,
  checked_at: checkedAt,
  do_not_reapply: true,
  user_action_required: false,
  next_action: 'Wait for a new human message from Scribe explicitly announcing that affiliate applications have reopened. Do not submit or send another inquiry before then.',
  note: 'Scribe Support agent Matt Sanz confirmed on 2026-09-14 that Scribe is not accepting new affiliate applications while the program is being refreshed and restructured. Inquiry is complete; no approval or customer tracking URL was issued. Keep official non-affiliate CTAs and suppress duplicate outreach.',
};
if (outreach.programs.supademo) {
  Object.assign(outreach.programs.supademo, {
    status: 'application_submitted',
    tracking_url: null,
    account: 'support@coshuma.com',
    gmail_message_id: '1a09b43356bc3947',
    acknowledgement_message_id: '1a09b43b5ba55b97',
    vendor_response_message_id: '1a0d02cddb650402',
    checked_at: supademoCheckedAt,
    application_state: 'application_submitted',
    review_state: 'pending_review',
    official_program_url: supademoProgramUrl,
    application_url: supademoApplicationUrl,
    evidence_file: supademoEvidenceFile,
    submission_evidence_comment_id: 5847971116,
    blockers: [],
    user_action_required: false,
    do_not_reapply: true,
    note: 'The official Supademo Affiliate Request form was submitted exactly once and confirmed “Thanks for your submission!” with a 1-2 business day review message (#292 comment 5847971116). No approval or customer tracking URL is verified.',
    next_action: 'Await Supademo review of the existing application. Do not reapply. Record only a new vendor decision or exact vendor-issued customer tracking URL.',
  });
}
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
for (const item of queue) {
  if (item.tool_id === 'supademo' || String(item.id || '').startsWith('supademo-')) {
    item.status = 'application_submitted';
    item.affiliate_status = 'application_submitted';
    item.priority = 'normal';
    item.user_action_required = false;
    item.exact_tracking_url = null;
    item.application_state = 'application_submitted';
    item.review_state = 'pending_review';
    item.do_not_reapply = true;
    item.application_url = supademoApplicationUrl;
    item.reason = 'The official Supademo Affiliate Request form was submitted exactly once and confirmed receipt (#292 comment 5847971116).';
    item.next_action = 'Await Supademo review. Do not reapply. Record only a vendor decision or exact vendor-issued customer tracking URL.';
    item.verified_at = supademoCheckedAt;
    item.evidence_file = supademoEvidenceFile;
    item.submission_evidence_comment_id = 5847971116;
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

console.log('Scribe fast-lane state/pages discoverability and Supademo formal application state ensured');
