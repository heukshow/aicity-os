import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectDir = path.resolve(__dirname, '..');
const dataDir = path.join(projectDir, 'data');
const publicDir = path.join(projectDir, 'public');

const evidencePath = path.join(dataDir, 'claap-approved-2026-09-08.json');
const queueEvidencePath = path.join(
  dataDir,
  'browser_required_queue.d',
  'claap-approved-link-recovery-2026-09-09.json',
);
const evidence = JSON.parse(fs.readFileSync(evidencePath, 'utf8'));
const queueEvidence = JSON.parse(fs.readFileSync(queueEvidencePath, 'utf8'));

if (
  evidence.tool_id !== 'claap' ||
  evidence.status !== 'approved' ||
  evidence.tracking_url !== null ||
  evidence.gmail_message_id !== '1a08009379826dfd' ||
  evidence.latest_manager_feedback?.gmail_message_id !== '1a0854b42ac1cc9a' ||
  queueEvidence.exact_tracking_url !== null
) {
  throw new Error('Claap evidence is not in the expected verified state; refusing to patch.');
}

const officialUrl = 'https://www.claap.io/';
const checkedAt = evidence.latest_manager_feedback.received_at_utc;
const evidenceMarkers = [
  'Claap PartnerStack welcome email 1a08009379826dfd verifies COSHUMA program acceptance.',
  'Claap manager Lamia Karmaly reviewed the COSHUMA page in message 1a0854b42ac1cc9a.',
  'The manager explicitly confirmed the current COSHUMA Claap buttons are not affiliate-tracked yet and instructed COSHUMA to recover the issued PartnerStack link.',
  'Exact customer-facing Claap tracking URL is still unverified; do not guess or construct a referral parameter.',
  'Official product domain is claap.io, not claap.ai.',
];

for (const relativePath of ['tools.json', 'tools.next.json']) {
  const filePath = path.join(dataDir, relativePath);
  const tools = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const tool = tools.find((item) => item.id === 'claap');
  if (!tool) throw new Error(`claap missing from data/${relativePath}`);

  Object.assign(tool, {
    official_url: officialUrl,
    official_evidence_url: officialUrl,
    affiliate_url: null,
    affiliate_final_url: null,
    affiliate_verified: true,
    affiliate_status: 'approved',
    affiliate_verified_at: evidence.received_at_utc,
    affiliate_status_checked_at: checkedAt,
    affiliate_status_evidence_url: `gmail:${evidence.gmail_message_id}`,
    affiliate_next_action: evidence.next_action,
    affiliate_dashboard_status: 'Approved; exact customer-facing tracking link not yet verified',
    affiliate_tracking_attribution_currently_verified: false,
    affiliate_evidence_markers: evidenceMarkers,
  });

  fs.writeFileSync(filePath, `${JSON.stringify(tools, null, 2)}\n`, 'utf8');
}

const outreachPath = path.join(dataDir, 'affiliate_outreach_state.json');
if (fs.existsSync(outreachPath)) {
  const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
  if (outreach.claap) {
    Object.assign(outreach.claap, {
      status: 'approved',
      tracking_url: null,
      updated_at: checkedAt,
      note: 'Approved via PartnerStack welcome email. Latest manager review confirms COSHUMA CTAs are still non-affiliate until the exact issued PartnerStack customer-facing link is recovered. Do not reapply or send duplicate outreach.',
    });
    fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`, 'utf8');
  }
}

const queuePath = path.join(dataDir, 'browser_required_queue.json');
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const staleIds = new Set([
  'claap-affiliate-batch-20260908-0650',
  queueEvidence.id,
]);
const cleaned = queue.filter((item) => !staleIds.has(item.id));
cleaned.push(queueEvidence);
fs.writeFileSync(queuePath, `${JSON.stringify(cleaned, null, 2)}\n`, 'utf8');

function walkHtml(dir) {
  const results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) results.push(...walkHtml(full));
    else if (entry.isFile() && entry.name.endsWith('.html')) results.push(full);
  }
  return results;
}

for (const filePath of walkHtml(publicDir)) {
  const before = fs.readFileSync(filePath, 'utf8');
  const after = before.replaceAll('https://www.claap.ai/', officialUrl);
  if (after !== before) fs.writeFileSync(filePath, after, 'utf8');
}

const claapPagePath = path.join(publicDir, 'tool', 'claap.html');
let html = fs.readFileSync(claapPagePath, 'utf8');

const oldOverkill = '<li>You need a simple asynchronous video creator rather than meeting and deal intelligence.</li>';
const newOverkill = '<li>Your workflow rarely involves sales calls, CRM updates, coaching, or collaborative async video review.</li>';
if (html.includes(oldOverkill)) html = html.replace(oldOverkill, newOverkill);
else if (!html.includes(newOverkill)) throw new Error('Claap overkill copy changed unexpectedly.');

const oldPricingParagraph = `<p class="text-sm text-slate-300 leading-relaxed">Claap's official pricing pages currently separate lighter contributor/team use from revenue-team features such as CRM auto-complete, AI-generated emails, coaching, deal insights, Smart Tables and administrative controls. The site also shows annual billing discounts and free or trial entry paths. Because Claap is actively iterating its pricing pages, COSHUMA does not hard-code a checkout price here; confirm the live amount, currency, seat minimums and included AI credits on Claap before purchase.</p>`;
const newPricingParagraph = `<p class="text-sm text-slate-300 leading-relaxed">Claap's current plan family is Free / Pro / Business / Enterprise. Claap's affiliate manager supplied current US-facing list prices of Pro at $40/license/month ($32 with annual billing) and Business at $75/license/month ($60 annual), with Enterprise custom. Claap's own site may display localized pricing in another currency, so confirm the live currency, billing cadence, seat rules and included usage at checkout.</p>`;
if (html.includes(oldPricingParagraph)) html = html.replace(oldPricingParagraph, newPricingParagraph);
else if (!html.includes(newPricingParagraph)) throw new Error('Claap pricing paragraph changed unexpectedly.');

html = html.replace(
  '<h3 class="font-bold text-white">Basic / entry</h3><p class="text-xs text-slate-400 mt-2">Useful for contributors who mainly need recording, transcription, summaries and collaboration.</p>',
  '<h3 class="font-bold text-white">Free</h3><p class="text-xs text-slate-400 mt-2">Entry plan for contributors and lighter recording, transcription, summaries and collaboration needs.</p>',
);
html = html.replace(
  '<h3 class="font-bold text-purple-300">Pro / Business</h3><p class="text-xs text-slate-300 mt-2">The practical comparison point for teams that need heavier recording, AI actions, integrations, coaching and CRM automation.</p>',
  '<h3 class="font-bold text-purple-300">Pro / Business</h3><p class="text-xs text-slate-300 mt-2">US-facing published pricing: Pro $40 monthly / $32 annual; Business $75 monthly / $60 annual per license. Verify locale at checkout.</p>',
);

const integrationsSection = `\n  <section class="p-6 rounded-3xl bg-[#131520] border border-[#222538] space-y-5">\n    <h2 class="text-2xl font-black text-white">Integrations and security buyers should check</h2>\n    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">\n      <div class="p-5 rounded-2xl bg-[#181a29] border border-[#222538]"><h3 class="font-bold text-white">Revenue-stack integrations</h3><p class="text-xs text-slate-400 mt-2 leading-relaxed">Claap's current official integrations include HubSpot, Salesforce, Pipedrive, Slack, Notion and Zapier, plus meeting and calendar tools. This matters if you want call context to flow into CRM, collaboration and automation workflows instead of living in a standalone transcript.</p></div>\n      <div class="p-5 rounded-2xl bg-[#181a29] border border-[#222538]"><h3 class="font-bold text-white">Security controls</h3><p class="text-xs text-slate-400 mt-2 leading-relaxed">Claap's official security material lists SOC 2 Type II, SSO, role-based access controls, audit logs and encryption controls. Enterprise buyers should still confirm the exact controls, data residency and procurement requirements that apply to their plan.</p></div>\n    </div>\n  </section>\n`;
const verdictMarker = '\n  <section class="p-6 rounded-3xl bg-[#131520] border border-purple-500/30 space-y-4">\n    <h2 class="text-2xl font-black text-white">COSHUMA verdict</h2>';
if (!html.includes('Integrations and security buyers should check')) {
  if (!html.includes(verdictMarker)) throw new Error('Claap verdict marker missing.');
  html = html.replace(verdictMarker, `${integrationsSection}${verdictMarker}`);
}

if (html.includes('claap.ai')) throw new Error('Stale claap.ai domain remains in Claap page.');
if (!html.includes('Pro $40 monthly / $32 annual')) throw new Error('Claap pricing patch missing.');
if (!html.includes('SOC 2 Type II')) throw new Error('Claap security patch missing.');
fs.writeFileSync(claapPagePath, html, 'utf8');

console.log('Claap reconciled: approved, exact tracking link pending, official domain and buyer facts corrected.');
