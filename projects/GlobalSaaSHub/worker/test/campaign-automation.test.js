import assert from 'node:assert/strict';
import test from 'node:test';
import { validateCampaignAssets } from '../src/campaign-automation.js';

function validAsset(overrides = {}) {
  return {
    companyName: 'Example Co',
    productName: 'Example App',
    contactEmail: 'ads@example.com',
    destinationUrl: 'https://example.com/product',
    logoUrl: 'https://example.com/logo.png',
    headline: 'A clearer workflow for project teams',
    description: 'Organize work, documents, and team updates in one place.',
    ctaText: 'Learn more',
    targetPage: '/tool/example.html',
    sellerAttestation: true,
    ...overrides,
  };
}

test('truthful HTTPS campaign assets pass automatic validation', () => {
  assert.deepEqual(validateCampaignAssets(validAsset()), { status: 'valid', notes: null });
});

test('missing seller attestation fails closed', () => {
  const result = validateCampaignAssets(validAsset({ sellerAttestation: false }));
  assert.equal(result.status, 'invalid');
});

test('unsafe target page fails closed', () => {
  assert.equal(validateCampaignAssets(validAsset({ targetPage: '//evil.example' })).status, 'invalid');
});

test('non-HTTPS URLs require review rather than automatic publication', () => {
  assert.equal(validateCampaignAssets(validAsset({ destinationUrl: 'http://example.com' })).status, 'needs_review');
});

test('unsupported superiority or guarantee claims require review', () => {
  assert.equal(validateCampaignAssets(validAsset({ headline: '#1 guaranteed return platform' })).status, 'needs_review');
});

test('overlong creative requires review', () => {
  assert.equal(validateCampaignAssets(validAsset({ description: 'x'.repeat(501) })).status, 'needs_review');
});
