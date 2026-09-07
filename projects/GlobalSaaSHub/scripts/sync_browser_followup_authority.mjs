import fs from 'node:fs';

const evidencePath = 'data/affiliate-browser-followup-wave3-2026-09-08.json';
const statePath = 'data/affiliate_outreach_state.json';
const queuePath = 'data/browser_required_queue.json';

const evidence = JSON.parse(fs.readFileSync(evidencePath, 'utf8'));
const stateDoc = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));

for (const item of evidence.results) {
  const current = stateDoc.programs[item.id] || {};
  stateDoc.programs[item.id] = {
    ...current,
    status: item.status,
    tracking_url: item.affiliate_url ?? null,
    ...(item.application_state ? { application_state: item.application_state } : {}),
    note: `${item.evidence} ${item.next_action}`,
    evidence_file: evidencePath,
    checked_date_kst: evidence.checked_date_kst,
    do_not_reapply: true,
    workflow_url: item.workflow_url || current.workflow_url || null,
  };

  const matches = queue.filter((row) => row.tool_id === item.id);
  if (matches.length !== 1) {
    throw new Error(`Expected exactly one browser queue row for ${item.id}, got ${matches.length}`);
  }
  const row = matches[0];
  row.affiliate_status = item.status;
  row.exact_tracking_url = item.affiliate_url ?? null;
  row.status = item.affiliate_url ? 'browser_required_otp' : item.status;
  row.reason = item.blocker || item.evidence;
  row.next_action = item.next_action;
  row.evidence_file = evidencePath;
  if (item.application_state) row.application_state = item.application_state;
  if (item.gmail_confirmation_message_id) row.gmail_confirmation_message_id = item.gmail_confirmation_message_id;
}

stateDoc.updated_at = evidence.checked_date_kst;
fs.writeFileSync(statePath, JSON.stringify(stateDoc, null, 2) + '\n');
fs.writeFileSync(queuePath, JSON.stringify(queue, null, 2) + '\n');

console.log(`sync_browser_followup_authority: synced=${evidence.results.length}`);
