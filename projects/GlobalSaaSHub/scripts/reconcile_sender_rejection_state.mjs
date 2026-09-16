import fs from 'node:fs';

const checkedAt = '2026-09-16T00:57:42Z';
const issue = 513;
const officialProgramUrl = 'https://www.sender.net/affiliate-program/';
const workflowUrl = 'https://dash.partnerstack.com/application?company=sendernet&gref=page';

const authoritative = {
  affiliate_url: null,
  affiliate_verified: true,
  affiliate_status: 'rejected',
  affiliate_source_url: officialProgramUrl,
  affiliate_workflow_url: workflowUrl,
  affiliate_verified_at: checkedAt,
  affiliate_status_checked_at: checkedAt,
  application_state: 'submitted_then_declined',
  affiliate_evidence_markers: [
    'Existing COSHUMA PartnerStack identity was reused for the Sender.net application; no duplicate network account was created.',
    'PartnerStack email received at support@coshuma.com on 2026-09-16 explicitly states that Sender declined the application (Gmail message 1a0a7b83dfb8ecda).',
    'The decline supersedes the earlier submitted/waiting state.',
    'No account-specific Sender customer tracking URL was issued or verified.',
    'Do not reapply or send rejection follow-up unless Sender explicitly invites a new application later.',
    'Clicks, signups/referrals, trials, paid customers, commission, payout and revenue remain unknown without separate first-party evidence.',
  ],
  affiliate_next_action: 'No automatic action. Keep Sender in rejected/do-not-reapply state unless Sender explicitly invites a new application with newer first-party evidence.',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  if (!fs.existsSync(file)) continue;
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const tool = tools.find((item) => item.id === 'sender-net');
  if (!tool) continue;
  Object.assign(tool, authoritative);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
if (fs.existsSync(outreachPath)) {
  const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
  outreach.updated_at = '2026-09-16';
  outreach.programs ||= {};
  outreach.programs['sender-net'] = {
    status: 'rejected',
    tracking_url: null,
    application_state: 'submitted_then_declined',
    account: 'support@coshuma.com',
    official_program_url: officialProgramUrl,
    workflow_url: workflowUrl,
    github_issue: issue,
    checked_at: checkedAt,
    do_not_reapply: true,
    note: 'PartnerStack explicitly declined the Sender.net application on 2026-09-16. Preserve the existing PartnerStack identity, do not reapply or send rejection follow-up unless Sender explicitly invites a new application, and keep the exact customer tracking URL/KPIs unknown.',
  };
  fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);
}

const queuePath = 'data/browser_required_queue.json';
if (fs.existsSync(queuePath)) {
  const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
  const item = queue.find((entry) => entry.tool_id === 'sender-net' || String(entry.id || '').startsWith('sender-net-'));
  if (item) {
    Object.assign(item, {
      priority: 'resolved',
      status: 'blocked_rejected_do_not_reapply',
      affiliate_status: 'rejected',
      application_state: 'submitted_then_declined',
      cost: 0,
      exact_tracking_url: null,
      user_action_required: false,
      blocker: null,
      reason: 'PartnerStack explicitly declined the Sender.net application on 2026-09-16; no account-specific tracking URL is verified.',
      next_action: 'No automatic action. Do not reapply or create another PartnerStack/Sender account unless Sender explicitly invites a new application later.',
      do_not_reapply: true,
      verified_at: checkedAt,
      github_issue: issue,
    });
  }
  fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);
}

// Public buyer pages intentionally omit COSHUMA's internal application, rejection,\n// tracking-verification and revenue-operations state. Keep that truth in data files only.

console.log('Sender.net rejection truth reconciled');
