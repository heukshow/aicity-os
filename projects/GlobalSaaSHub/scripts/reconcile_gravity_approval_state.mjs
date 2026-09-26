import fs from './affiliate_state_fs.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectDir = path.resolve(__dirname, '..');
const dataDir = path.join(projectDir, 'data');

const approvalEvidencePath = path.join(
  dataDir,
  'browser_required_queue.d',
  'gravity-forms-approved-link-recovery-2026-09-09.json',
);
const approval = JSON.parse(fs.readFileSync(approvalEvidencePath, 'utf8'));

if (
  approval.tool_id !== 'gravity-forms' ||
  !['approved_account', 'approved_tracking'].includes(approval.affiliate_status) ||
  approval.gmail_message_id !== '1a082c784399b2c3'
) {
  throw new Error('Gravity approval evidence is not in the expected verified state; refusing to reconcile.');
}

const tracked = approval.affiliate_status === 'approved_tracking';
if (tracked && (approval.exact_tracking_url !== 'https://try.gravity.com/8bd4r655ttws'
  || approval.verification?.source !== 'authenticated_partnerstack_dashboard'
  || approval.verification?.destination_host !== 'www.gravityforms.com'
  || approval.verification?.http_status !== 200)) {
  throw new Error('Gravity tracking requires independently verified vendor-issued evidence.');
}

const freshMarkers = [
  `Gravity Affiliate welcome email ${approval.gmail_message_id} verifies COSHUMA program acceptance.`,
  'The welcome email states a 30-day attribution window and 20% commission on a qualifying sale.',
  tracked ? 'Authenticated PartnerStack issued the exact customer link; independent HTTP and browser verification reached Gravity Forms.' : 'No exact customer-facing Gravity tracking URL has been issued or verified yet.',
  'Do not reapply, do not reuse a PartnerStack/dashboard/email redirect as a revenue URL, and do not guess tracking parameters.',
];

for (const relativePath of ['tools.json', 'tools.next.json']) {
  const filePath = path.join(dataDir, relativePath);
  const tools = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const tool = tools.find((item) => item.id === 'gravity-forms');
  if (!tool) throw new Error(`gravity-forms missing from data/${relativePath}`);

  Object.assign(tool, {
    affiliate_url: tracked ? approval.exact_tracking_url : null,
    affiliate_final_url: tracked ? approval.verification.destination_origin : null,
    affiliate_verified: true,
    affiliate_status: tracked ? 'approved_tracking' : 'approved',
    affiliate_verified_at: approval.verified_at,
    affiliate_status_checked_at: approval.verified_at,
    affiliate_status_evidence_url: tracked ? approval.verification.portal_url : `gmail:${approval.gmail_message_id}`,
    affiliate_next_action: approval.next_action,
    affiliate_evidence_markers: [...new Set([...(tool.affiliate_evidence_markers || []), ...freshMarkers])],
  });

  fs.writeFileSync(filePath, `${JSON.stringify(tools, null, 2)}\n`, 'utf8');
}

const queuePath = path.join(dataDir, 'browser_required_queue.json');
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const staleId = 'gravity-forms-browser-followup-20260908';
const authoritativeId = approval.id;

const cleaned = queue.filter(
  (item) => item.id !== staleId && item.id !== authoritativeId,
);
cleaned.push(approval);
fs.writeFileSync(queuePath, `${JSON.stringify(cleaned, null, 2)}\n`, 'utf8');

console.log(`Gravity approval reconciled: ${tracked ? 'verified customer tracking preserved' : 'exact tracking URL still required'}.`);
