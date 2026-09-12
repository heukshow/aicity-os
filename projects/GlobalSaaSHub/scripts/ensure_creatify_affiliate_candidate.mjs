import fs from 'node:fs';

const dataDir = new URL('../data/', import.meta.url);
const queuePath = new URL('browser_required_queue.json', dataDir);
const toolsPath = new URL('tools.json', dataDir);

const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const tools = JSON.parse(fs.readFileSync(toolsPath, 'utf8'));

const protectedStatuses = new Set([
  'application_submitted',
  'approved',
  'approved_tracking',
  'rejected',
  'pending',
  'cooldown',
  'closed',
  'excluded_user_request',
  'vendor-paused',
]);

const existingTool = tools.find((tool) => {
  const id = String(tool.id || '').toLowerCase();
  const name = String(tool.name || '').toLowerCase();
  return id.includes('creatify') || name.includes('creatify');
});

const existingQueueItem = queue.find((item) => String(item.id || '').startsWith('creatify-affiliate-'));

if (existingQueueItem) {
  console.log(`Creatify affiliate queue item already exists: ${existingQueueItem.id} (${existingQueueItem.status || 'unknown'})`);
  process.exit(0);
}

if (existingTool && protectedStatuses.has(existingTool.affiliate_status)) {
  console.log(`Creatify affiliate state is already protected: ${existingTool.affiliate_status}; no application task added.`);
  process.exit(0);
}

queue.push({
  id: 'creatify-affiliate-application-20260912',
  priority: 'high',
  status: 'browser_required',
  cost: '0',
  verified_at: '2026-09-12T04:36:00Z',
  affiliate_status: 'candidate',
  reason: 'Creatify official affiliate page was rechecked on 2026-09-12. The program is free to join, advertises 25% recurring commission on qualifying purchases, and states that Creatify uses Rewardful. Repository search found no existing Creatify affiliate state or tracking URL, and support@coshuma.com Gmail search found no prior Creatify relationship. The application and any issued unique link require authenticated browser/dashboard handling.',
  official_program_url: 'https://creatify.ai/affiliate',
  platform: 'Rewardful',
  next_action: 'Open the official Creatify affiliate page in an authenticated browser and use the existing COSHUMA company identity/support@coshuma.com. Before submission, recheck for an existing account/application. If none exists, complete the free application. Stop for CAPTCHA, OTP, legal/terms consent, payment approval, or forced identity verification. After approval, copy only the exact customer-facing unique referral URL issued by Creatify/Rewardful and verify its destination and attribution before changing any COSHUMA CTA.',
  do_not: [
    'Do not submit a duplicate application if an existing Creatify account, pending application, approval, rejection, cooldown, closure, or vendor-paused state is found.',
    'Do not treat https://creatify.ai/affiliate, a Rewardful dashboard, login page, onboarding URL, or generic Creatify homepage as a customer affiliate/revenue link.',
    'Do not guess or construct a Creatify referral parameter or tracking URL.',
    'Do not infer a click, signup, paid customer, commission, payout, or revenue from application submission, approval, link issuance, publication, or test visits.'
  ],
  evidence: {
    official_program: 'https://creatify.ai/affiliate',
    official_terms_observed: 'Free to join; 25% recurring commission for qualifying purchases; Rewardful is the stated affiliate platform.',
    gmail_account_checked: 'support@coshuma.com',
    gmail_existing_relationship_found: false,
    repository_existing_relationship_found: false
  }
});

fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`, 'utf8');
console.log('Creatify free affiliate application candidate added to browser_required_queue.json');
