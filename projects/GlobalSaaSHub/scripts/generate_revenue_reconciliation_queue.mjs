import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const audit = JSON.parse(fs.readFileSync(path.join(root, 'data/revenue-leakage-audit.json'), 'utf8'));

const rank = {P0_UNCHECKED:0, P1_STALE:1, P1_PARTIAL:2};
const groups = (audit.account_groups || []).map(group => {
  const priorities = group.tools.map(t => t.priority).sort((a,b) => rank[a]-rank[b]);
  const primaryPriority = priorities[0] || 'P1_PARTIAL';
  const portalKnown = typeof group.portal_url === 'string' && group.portal_url.startsWith('https://');
  return {
    account_id: group.account_id,
    network: group.network,
    portal_url: group.portal_url || null,
    priority: primaryPriority,
    tool_count: group.tools.length,
    tools: group.tools,
    execution: portalKnown ? 'browser_read_only' : 'locate_existing_account_or_vendor_dashboard_first',
    objective: 'Read only evidence-backed affiliate metrics for the existing approved/tracked relationship. Capture clicks, signups/referrals, trials, paid customers, revenue if explicitly shown, commission earned/approved/pending, paid payout, pending payout, currency, reporting period, and timestamp. Preserve unknown when a metric is not shown.',
    safety: [
      'Do not create a new account or reapply.',
      'Do not change any customer tracking URL.',
      'Do not start a paid plan or authorize payment.',
      'Do not infer signup, trial, paid customer, commission, or payout from clicks.',
      'Stop for CAPTCHA, OTP, legal agreement acceptance, identity verification, or payment authorization.',
      'Never expose this internal revenue audit on public COSHUMA pages.'
    ],
    done_when: 'A new evidence-backed revenue-truth record is stored for each checked tool/account scope, or the metric is explicitly marked unavailable/unknown with source and timestamp.'
  };
});

groups.sort((a,b) => rank[a.priority]-rank[b.priority] || b.tool_count-a.tool_count || (a.network||'').localeCompare(b.network||''));

const output = {
  generated_at: new Date().toISOString(),
  source: 'data/revenue-leakage-audit.json',
  scope: 'Internal COSHUMA revenue reconciliation only',
  queue_status: 'active',
  task_count: groups.length,
  priority_order: ['P0_UNCHECKED','P1_STALE','P1_PARTIAL'],
  tasks: groups
};

fs.writeFileSync(path.join(root, 'data/revenue-reconciliation-queue.json'), JSON.stringify(output, null, 2) + '\n');
console.log(`Revenue reconciliation queue: ${groups.length} account-group tasks; ${groups.reduce((n,g)=>n+g.tool_count,0)} tool checks.`);
