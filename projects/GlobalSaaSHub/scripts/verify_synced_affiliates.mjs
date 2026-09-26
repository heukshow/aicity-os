import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import {approvedTracking} from './approved_tracking_evidence.mjs';

// One strict contract for PR preparation and production preparation.
export function verifySyncedAffiliates(tools) {
  const expected = new Map([
    ['murf-ai', 'https://get.murf.ai/fqac0vixj0qs'],
    ['unbounce', 'https://unbounce.partnerlinks.io/5ubjnt8lluqi'],
    ['helpdesk', 'https://www.helpdesk.com/?a=8IetMhQvR&utm_campaign=pp_helpdesk-default&utm_source=PP&d=14'],
    ['voibe', 'https://www.getvoibe.com/?aff=G5Yr5D'],
    ['time2book', 'https://time2book.me?aff=9TzesqKi'],
    ['taskip', 'https://taskip.net/?atp=qnV3mw'],
    ['clickfunnels', 'https://www.clickfunnels.com/signup-flow?aff=b57f3056884d05b842f607e32347df542821875bbe3209a214141aa32a210532'],
    ['tagshop-ai', 'https://tagshop.ai?via=coshuma-22501e'],
  ]);
  const gravity = approvedTracking.get('gravity-forms');
  if (gravity) expected.set('gravity-forms', gravity.exact_tracking_url);
  for (const [id, url] of expected) {
    const tool = tools.find((item) => item.id === id);
    if (!tool || tool.affiliate_verified !== true || tool.affiliate_status !== 'approved_tracking' || tool.affiliate_url !== url) {
      throw new Error(`Verified affiliate sync failed for ${id}`);
    }
  }
  const expectedStates = new Map([
    ['gravity-forms', approvedTracking.has('gravity-forms') ? 'approved_tracking' : 'approved'],
    ['sendcloud', 'approved_tracking'],
    ['apollo', 'rejected'],
    ['ai-video-cut', 'application_submitted'],
    ['fillout', 'approved_tracking'],
    ['beefree', 'approved_tracking'],
    ['gumloop', 'application_submitted'],
    ['pipedrive', 'pending'],
    ['monday-com', 'pending'],
    ['kittl', 'approved_tracking'],
  ]);
  for (const [id, status] of expectedStates) {
    const tool = tools.find((item) => item.id === id);
    if (tool && tool.affiliate_status !== status) {
      throw new Error(`Affiliate state sync failed for ${id}: ${tool.affiliate_status} !== ${status}`);
    }
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  verifySyncedAffiliates(JSON.parse(fs.readFileSync(new URL('../data/tools.json', import.meta.url), 'utf8')));
  console.log('PASS shared PR/production affiliate state and exact-URL contract');
}
