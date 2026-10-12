import fs from 'node:fs';

const expected = new Map([
  ['activepieces','blocked_partnerstack_network_marketplace_limited'],
  ['agorapulse','waiting_vendor_response'],
  ['carv','waiting_vendor_eligibility_clarification'],
  ['chatbot','waiting_vendor_response'],
  ['colossyan','waiting_vendor_response'],
  ['docusign','browser_required_captcha_program_form'],
  ['dub','browser_required_legal_program_consent'],
  ['expandi','waiting_vendor_requirement'],
  ['featureshark','waiting_vendor_response'],
  ['flowgent-ai','program_inactive'],
  ['google-workspace','browser_required_legal_program_consent'],
  ['hide-me','browser_required_legal_program_consent'],
  ['scribe','program_closed_to_new_applicants'],
  ['snov-io','browser_required_legal_program_consent'],
]);

for (const file of ['data/tools.json','data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(new URL(`../${file.replace('data/','data/')}`, import.meta.url), 'utf8'));
  for (const [id, status] of expected) {
    const tool = tools.find((row) => row.id === id);
    if (!tool) throw new Error(`Missing expected tool ${id} in ${file}`);
    if (tool.affiliate_status !== status) {
      throw new Error(`Affiliate gap state regression for ${id}: ${tool.affiliate_status ?? 'unclassified'} !== ${status}`);
    }
    if (tool.affiliate_url !== null) {
      throw new Error(`Unverified affiliate URL must remain null for ${id}`);
    }
  }
}

const outreach = JSON.parse(fs.readFileSync(new URL('../data/affiliate_outreach_state.json', import.meta.url), 'utf8')).programs;
const queue = JSON.parse(fs.readFileSync(new URL('../data/browser_required_queue.json', import.meta.url), 'utf8'));
for (const [id, status] of [['activepieces', 'blocked_partnerstack_network_marketplace_limited'], ['colossyan', 'waiting_vendor_response'], ['hide-me', 'browser_required_legal_program_consent']]) {
  if (outreach[id]?.status !== status || outreach[id]?.tracking_url !== null) {
    throw new Error(`Outreach state regression for ${id}`);
  }
  const item = queue.find((row) => row.tool_id === id);
  if (item?.status !== status || item?.exact_tracking_url !== null) {
    throw new Error(`Browser queue state regression for ${id}`);
  }
}
const chatbot = outreach.chatbot;
if (chatbot?.status !== 'waiting_vendor_response' || chatbot?.tracking_url !== null
    || chatbot?.application_state !== 'follow_up_sent_waiting_exact_customer_link'
    || chatbot?.outbound_message_id !== '1a12f8625bffdd95'
    || chatbot?.do_not_repeat_outreach !== true) {
  throw new Error('ChatBot exact-link follow-up evidence regression');
}

const hideMe = outreach['hide-me'];
const hideMeQueue = queue.find((row) => row.tool_id === 'hide-me');
if (Object.hasOwn(hideMe ?? {}, 'account')) {
  throw new Error('hide.me outreach must not expose an internal mailbox routing label');
}
if (hideMe?.application_state !== 'not_submitted_legal_terms_unaccepted' || hideMe?.user_action_required !== true) {
  throw new Error('hide.me legal consent outreach gate regression');
}
if (hideMeQueue?.application_state !== 'not_submitted_legal_terms_unaccepted' || hideMeQueue?.user_action_required !== true) {
  throw new Error('hide.me legal consent queue gate regression');
}

const activepieces = outreach.activepieces;
const activepiecesQueue = queue.find((row) => row.tool_id === 'activepieces');
if (activepieces?.application_state !== 'not_submitted_program_not_found'
    || activepieces?.inbound_message_id !== '1a1303ac0be8e537'
    || activepieces?.do_not_reapply !== true
    || activepiecesQueue?.inbound_message_id !== '1a1303ac0be8e537'
    || activepiecesQueue?.do_not_reapply !== true) {
  throw new Error('Activepieces PartnerStack limitation evidence regression');
}

const networkProfile = queue.find((row) => row.id === 'partnerstack-network-profile-reapplication-20261012');
if (networkProfile?.status !== 'reviewed_not_approved_marketplace_limited'
    || networkProfile?.application_state !== 'reviewed_not_approved'
    || networkProfile?.inbound_message_id !== '1a1303ac0be8e537'
    || networkProfile?.do_not_reapply !== true
    || networkProfile?.exact_tracking_url !== null
    || !networkProfile?.reason?.includes('existing PartnerStack partnerships are unaffected')) {
  throw new Error('PartnerStack Network Profile decision evidence regression');
}

console.log('PASS: 14 reconciled affiliate gaps and the PartnerStack Marketplace limitation remain fail-closed while existing partnerships are preserved');
