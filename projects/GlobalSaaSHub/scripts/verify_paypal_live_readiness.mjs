const tokenUrl = new URL(process.env.ACTIONS_ID_TOKEN_REQUEST_URL);
tokenUrl.searchParams.set('audience', 'coshuma-private-analytics');
const tokenResponse = await fetch(tokenUrl, { headers: { Authorization: 'Bearer ' + process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN } });
if (!tokenResponse.ok) throw new Error('OIDC request failed: ' + tokenResponse.status);
const token = (await tokenResponse.json()).value;
const endpoint = 'https://globalsaashub-payments.qmfforfhem.workers.dev/internal/paypal-live-readiness';
const response = await fetch(endpoint, {
  headers: { Authorization: 'Bearer ' + token },
  signal: AbortSignal.timeout(30000),
});
if (!response.ok) throw new Error('PayPal Live readiness endpoint failed: ' + response.status);
const result = await response.json();
const expected = result.providerAuthenticationVerified === true
  && result.webhookUrlVerified === true
  && result.requiredEventsVerified === true
  && result.configurationOnly === true
  && result?.diagnostic?.stage === 'complete'
  && result?.diagnostic?.code === 'complete';
if (!expected) throw new Error('PayPal Live readiness is not verified');
const evidence = {
  checked_at: new Date().toISOString(),
  providerAuthenticationVerified: true,
  webhookUrlVerified: true,
  requiredEventsVerified: true,
  merchantIdentityVerified: result.merchantIdentityVerified === true,
  configurationOnly: true,
  diagnostic: result.diagnostic,
};
console.log('PAYPAL_LIVE_READINESS_VERIFIED ' + JSON.stringify(evidence));
if (process.env.GITHUB_STEP_SUMMARY) {
  const fs = await import('node:fs');
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, '\n## PayPal Live readiness\n\n```json\n' + JSON.stringify(evidence, null, 2) + '\n```\n');
}
