import fs from 'node:fs';

const invideo = {
  id: 'invideo-ai',
  name: 'InVideo AI',
  category: 'video_gen',
  category_display: 'Video & Shorts Gen',
  description: 'A browser-based AI video creation platform that can turn prompts into scripts, scenes, voiceovers, captions and edited videos, with a limited free plan and paid credit-based plans.',
  affiliate_url: null,
  pricing: 'Free plan available; paid plans use monthly credits',
  key_features: [
    'Prompt-to-video generation',
    'AI-assisted browser video editing',
    'Image and video generation models',
    'Voiceover, captions and social-video workflows',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=invideo.io&sz=128',
  primary_category: 'video_gen',
  comparison_group: 'ai_avatar_video',
  official_url: 'https://invideo.io/',
  pricing_source_url: 'https://invideo.io/pricing/',
  pricing_verified_at: '2026-09-11T00:00:00+09:00',
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly or annual depending on plan',
  evidence_source_type: 'official_pricing_and_help_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: '2026-09-11T00:00:00+09:00',
  official_evidence_url: 'https://invideo.io/',
  affiliate_verified: true,
  affiliate_status: 'application_available_impact',
  affiliate_source_url: 'https://invideo.io/make/affiliate-program/',
  affiliate_verified_at: '2026-09-11T05:26:00Z',
  affiliate_evidence_markers: [
    'Official InVideo affiliate program is free to join and open to everyone',
    'Official terms: 50% commission on monthly plans and 25% on annual plans for the first billing cycle',
    'Program is managed by Impact.com and uses the Impact account used to enroll for payouts',
    'Referral click window is 120 days; free signups themselves earn no commission',
    'support@coshuma.com Gmail search found no prior InVideo application, approval, rejection, tracking-link, commission, or payout mail in the last 180 days as of 2026-09-11',
    'No COSHUMA-specific customer-facing InVideo tracking URL is verified yet; do not publish a generic or guessed affiliate URL',
    'GitHub issue #391 holds the browser-only existing-Impact-account check and enrollment guard',
  ],
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === invideo.id);
  if (existing) Object.assign(existing, invideo);
  else tools.push(invideo);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

console.log('InVideo AI canonical tool record ensured in tools.json and tools.next.json');
