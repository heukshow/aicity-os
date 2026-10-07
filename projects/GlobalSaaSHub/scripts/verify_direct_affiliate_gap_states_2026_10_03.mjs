import fs from 'node:fs';

const expected = new Map([
  ['activepieces','browser_required_sales_inquiry'],
  ['agorapulse','waiting_vendor_response'],
  ['carv','waiting_vendor_eligibility_clarification'],
  ['chatbot','referral_link_requested'],
  ['docusign','browser_required_captcha_program_form'],
  ['dub','browser_required_legal_program_consent'],
  ['expandi','waiting_vendor_requirement'],
  ['featureshark','waiting_vendor_response'],
  ['flowgent-ai','program_inactive'],
  ['google-workspace','application_available_account_required'],
  ['hide-me','browser_required_application_form'],
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

console.log('PASS: 13 reconciled affiliate gaps remain in evidence-backed hold/browser/terminal states');
