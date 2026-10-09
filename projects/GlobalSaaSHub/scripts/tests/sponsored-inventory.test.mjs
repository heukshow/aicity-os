import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../../public/sponsored-inventory.js', import.meta.url), 'utf8');
const NOW = Date.parse('2026-10-04T12:00:00.000Z');
const routes = {
  '/tool/pipedrive.html': 'tool-primary',
  '/best/claap-sales-follow-up-ai.html': 'buyer-intent-top',
  '/compare/semrush-vs-frase.html': 'compare-decision-premium',
};
const iso = (offset) => new Date(NOW + offset).toISOString();
const creative = (overrides = {}) => ({
  campaignId: 'campaign-one', slot: 'tool-primary', targetPage: '/tool/pipedrive.html',
  title: 'Example sales tool', body: 'An advertiser-provided description.', button: 'Visit advertiser',
  url: 'https://advertiser.example/product?ref=coshuma', startAt: iso(-60000), endAt: iso(3600000),
  environment: 'live', paymentVerified: true, approved: true, status: 'published', ...overrides,
});
const available = (...placements) => ({ ready: true, placements });
const flush = async () => { for (let i = 0; i < 8; i += 1) await Promise.resolve(); };

class Events {
  listeners = new Map();
  addEventListener(name, fn) {
    if (!this.listeners.has(name)) this.listeners.set(name, []);
    this.listeners.get(name).push(fn);
  }
  dispatch(name, event = {}) {
    event.preventDefault ??= () => { event.defaultPrevented = true; };
    for (const fn of this.listeners.get(name) || []) fn(event);
    return event;
  }
}

class Element extends Events {
  hidden = false;
  textContent = '';
  dataset = {};
  attributes = {};
  children = {};
  // Any attempt to introduce HTML from API data is a test failure.
  set innerHTML(value) { throw new Error(`Unsafe HTML assignment: ${value}`); }
  set href(value) { this.attributes.href = value; }
  get href() { return this.attributes.href; }
  set src(value) { this.attributes.src = value; }
  get src() { return this.attributes.src; }
  setAttribute(name, value) { this.attributes[name] = value; }
  removeAttribute(name) { delete this.attributes[name]; }
  querySelector(selector) { return this.children[selector] || null; }
}

function slotElement(slot) {
  const element = new Element();
  element.dataset.sponsoredSlot = slot;
  for (const field of ['label', 'media', 'logo', 'image', 'title', 'body', 'button']) element.children[`[data-sponsored-${field}]`] = new Element();
  element.children['[data-sponsored-media]'].hidden = true;
  return element;
}

function browser({ path = '/tool/pipedrive.html', slots = [routes[path] || 'tool-primary'], payload = available(creative()), visibility = 'visible', readyState = 'complete', intersection = 1, observerSupported = true } = {}) {
  const elements = slots.map(slotElement);
  const document = new Events();
  document.readyState = readyState;
  document.visibilityState = visibility;
  document.querySelectorAll = () => elements;
  const window = new Events();
  window.location = new URL(`https://coshuma.com${path}?utm_source=fixture`);
  const requests = [];
  const events = [];
  const responses = [];
  const timers = new Map();
  const observers = [];
  let clock = NOW;
  let timerId = 0;
  class Clock extends Date { static now() { return clock; } }
  const addTimer = (fn, delay, interval) => {
    const id = ++timerId;
    timers.set(id, { fn, time: clock + delay, interval });
    return id;
  };
  window.setTimeout = (fn, delay) => addTimer(fn, delay, 0);
  window.setInterval = (fn, delay) => addTimer(fn, delay, delay);
  window.clearTimeout = (id) => timers.delete(id);
  if (observerSupported) window.IntersectionObserver = class {
    constructor(callback) { this.callback = callback; this.targets = new Set(); observers.push(this); }
    observe(target) {
      this.targets.add(target);
      this.callback([{ target, isIntersecting: intersection > 0, intersectionRatio: intersection }]);
    }
    disconnect() { this.targets.clear(); }
  };
  window.gtag = (...args) => events.push(JSON.parse(JSON.stringify(args)));
  window.fetch = async (url, options) => {
    requests.push({ url, options });
    const next = responses.length ? responses.shift() : payload;
    if (next instanceof Error) throw next;
    if (typeof next === 'function') return next(options);
    return { ok: true, json: async () => next };
  };
  vm.runInNewContext(source, { window, document, URL, Date: Clock, AbortController }, { filename: 'sponsored-inventory.js' });
  return {
    elements, document, window, requests, events, observers,
    intersection(ratio) {
      intersection = ratio;
      for (const observer of observers) {
        observer.callback([...observer.targets].map((target) => ({ target, isIntersecting: ratio > 0, intersectionRatio: ratio })));
      }
    },
    queue: (...values) => responses.push(...values),
    field: (name, index = 0) => elements[index].querySelector(`[data-sponsored-${name}]`),
    click: () => elements[0].querySelector('[data-sponsored-button]').dispatch('click'),
    async advance(milliseconds) {
      const target = clock + milliseconds;
      for (;;) {
        const next = [...timers].filter(([, timer]) => timer.time <= target).sort((a, b) => a[1].time - b[1].time || a[0] - b[0])[0];
        if (!next) break;
        const [id, timer] = next;
        clock = timer.time;
        if (timer.interval) timer.time += timer.interval;
        else timers.delete(id);
        timer.fn();
        await flush();
      }
      clock = target;
      await flush();
    },
    async visibility(state) { document.visibilityState = state; document.dispatch('visibilitychange'); await flush(); },
  };
}

test('only the three exact route/slot pairs fetch and display verified public creative', async () => {
  for (const [path, slot] of Object.entries(routes)) {
    const item = creative({ targetPage: path, slot, label: 'Recommended by COSHUMA', title: '<img src=x onerror=alert(1)>', payerEmail: 'private@example.com' });
    const app = browser({ path, slots: [slot, 'unrelated-slot'], payload: available(item) });
    assert.ok(app.elements.every((element) => element.hidden), 'Slots stay hidden until the lookup completes');
    await flush();
    assert.equal(app.elements[0].hidden, false);
    assert.equal(app.elements[1].hidden, true);
    assert.equal(app.field('label').textContent, 'Sponsored');
    assert.equal(app.field('title').textContent, item.title, 'Creative is plain text, including HTML-like content');
    assert.equal(app.field('button').href, item.url);
    assert.equal(app.field('button').attributes.rel, 'sponsored noopener noreferrer');
    assert.equal(app.field('button').attributes.target, '_blank');
    assert.equal(app.requests[0].url, `https://globalsaashub-payments.qmfforfhem.workers.dev/v1/sponsored/placements?path=${encodeURIComponent(path)}`);
    assert.equal(app.requests[0].options.credentials, 'omit');
    assert.equal(app.requests[0].options.cache, 'no-store');
    assert.equal(app.requests[0].options.referrerPolicy, 'no-referrer');
    assert.equal(app.events.length, 0, 'Rendering alone is not an impression');
    await app.advance(1000);
    assert.equal(app.events[0][1], 'sponsored_impression');
    assert.deepEqual(app.events[0][2], {
      sponsor_campaign_id: item.campaignId, sponsored_slot: slot, sponsor_title: item.title,
      link_url: item.url, outbound_domain: 'advertiser.example', page_path: `${path}?utm_source=fixture`,
      page_location: `https://coshuma.com${path}?utm_source=fixture`, transport_type: 'beacon',
    });
    assert.doesNotMatch(JSON.stringify(app.events), /private@example|payerEmail|paymentVerified/);
  }
});

test('verified image creative renders only exact COSHUMA worker assets and clears them when revoked', async () => {
  const image = creative({
    creativeMode: 'image',
    imageUrl: 'https://globalsaashub-payments.qmfforfhem.workers.dev/v1/ads/assets/11111111-1111-4111-8111-111111111111/tool-primary',
    logoUrl: 'https://globalsaashub-payments.qmfforfhem.workers.dev/v1/ads/assets/11111111-1111-4111-8111-111111111111/logo',
  });
  const app = browser({ payload: available(image) });
  await flush();
  assert.equal(app.elements[0].hidden, false);
  assert.equal(app.field('media').hidden, false);
  assert.equal(app.field('logo').src, image.logoUrl);
  assert.equal(app.field('image').src, image.imageUrl);
  app.queue(available());
  await app.advance(60000);
  assert.equal(app.elements[0].hidden, true);
  assert.equal(app.field('media').hidden, true);
  assert.equal(app.field('logo').src, undefined);
  assert.equal(app.field('image').src, undefined);

  for (const patch of [
    { imageUrl: 'https://evil.example/v1/ads/assets/11111111-1111-4111-8111-111111111111/tool-primary' },
    { logoUrl: 'https://globalsaashub-payments.qmfforfhem.workers.dev/v1/ads/assets/11111111-1111-4111-8111-111111111111/not-logo' },
    { imageUrl: 'http://globalsaashub-payments.qmfforfhem.workers.dev/v1/ads/assets/11111111-1111-4111-8111-111111111111/tool-primary' },
  ]) {
    const rejected = browser({ payload: available({ ...image, ...patch }) });
    await flush();
    assert.equal(rejected.elements[0].hidden, true, JSON.stringify(patch));
  }
});

test('homepage, Gamma, Chatbase, C02 and noncanonical or wildcard routes never request inventory', async () => {
  for (const path of ['/', '/index.html', '/tool/gamma.html', '/tool/chatbase.html', '/compare/privy-vs-omnisend.html', '/best/ai-presentation-makers.html', '/best/ai-chatbots.html', '/compare/chatbase-vs-customgpt.html', '/compare/frase-vs-semrush.html', '/tool/pipedrive.html/', '/*']) {
    const app = browser({ path });
    await app.advance(120000);
    app.document.dispatch('visibilitychange');
    assert.equal(app.requests.length, 0, path);
    assert.ok(app.elements.every((element) => element.hidden), path);
    assert.equal(app.events.length, 0, path);
    assert.equal(app.observers.length, 0, path);
  }
  for (const slots of [[], ['buyer-intent-top'], ['tool-primary', 'tool-primary']]) {
    const app = browser({ slots });
    await flush();
    assert.equal(app.requests.length, 0, 'Missing, wrong or duplicate containers fail closed');
    assert.ok(app.elements.every((element) => element.hidden));
  }
});

test('payment, approval, environment and publication must all be explicit and exact', async () => {
  for (const key of ['paymentVerified', 'approved']) {
    for (const value of [false, undefined, null, 'true', 1]) {
      const app = browser({ payload: available(creative({ [key]: value })) });
      await flush();
      assert.equal(app.elements[0].hidden, true, `${key}=${value}`);
      assert.equal(app.events.length, 0);
    }
  }
  for (const patch of [{ environment: 'sandbox' }, { environment: undefined }, { status: 'paid' }, { status: 'pending_review' }, { status: 'cancelled' }, { status: undefined }]) {
    const app = browser({ payload: available(creative(patch)) });
    await flush();
    assert.equal(app.elements[0].hidden, true, JSON.stringify(patch));
  }
});

test('missing, malformed, impossible and inactive flight dates never display', async () => {
  for (const patch of [
    { startAt: undefined }, { endAt: undefined }, { startAt: null }, { endAt: '' },
    { startAt: 1 }, { startAt: 'not-a-date' }, { endAt: '2026-13-01T00:00:00Z' },
    { startAt: '2026-02-30T00:00:00Z' }, { startAt: '2026-10-04' },
    { startAt: iso(1000) }, { endAt: iso(0) }, { endAt: iso(-1) },
    { startAt: iso(-60000), endAt: iso(-60000) }, { startAt: iso(1000), endAt: iso(-1000) },
  ]) {
    const app = browser({ payload: available(creative(patch)) });
    await flush();
    assert.equal(app.elements[0].hidden, true, JSON.stringify(patch));
    assert.equal(app.events.length, 0);
  }
  const app = browser({ payload: available(creative({ startAt: '2026-10-04T12:00:00Z' })) });
  await flush();
  assert.equal(app.elements[0].hidden, false, 'The exact start instant is included');
  const scheduled = browser({ payload: available(creative({ startAt: iso(30000) })) });
  await flush();
  assert.equal(scheduled.elements[0].hidden, true);
  await scheduled.advance(60000);
  assert.equal(scheduled.elements[0].hidden, false, 'A scheduled campaign becomes eligible on a fresh lookup after its start');
});

test('destinations require an absolute HTTPS external URL without credentials', async () => {
  for (const url of ['javascript:alert(1)', 'data:text/html,test', 'http://advertiser.example', '/relative', '//advertiser.example', 'https://user:password@advertiser.example', 'https://coshuma.com/tool/test.html', 'https://coshuma.com./', 'https://www.coshuma.com/', 'https://assets.coshuma.com/', 'not a URL']) {
    const app = browser({ payload: available(creative({ url })) });
    await flush();
    assert.equal(app.elements[0].hidden, true, url);
    assert.equal(app.field('button').href, undefined);
  }
});

test('wildcards, wrong targets and ambiguous duplicate campaigns cannot take a slot', async () => {
  for (const placements of [
    [creative({ targetPage: '*' })], [creative({ targetPage: '/tool/gamma.html' })],
    [creative({ slot: '*' })], [creative({ slot: 'buyer-intent-top' })],
    [creative(), creative({ campaignId: 'campaign-two' })], [creative(), creative()],
  ]) {
    const app = browser({ payload: available(...placements) });
    await flush();
    assert.equal(app.elements[0].hidden, true);
    assert.equal(app.events.length, 0);
  }
});

test('polling reconciles cancellations and refunds without inflating impressions or click handlers', async () => {
  const app = browser();
  await flush();
  await app.advance(120000);
  assert.equal(app.requests.length, 3);
  assert.equal(app.events.filter((event) => event[1] === 'sponsored_impression').length, 1);
  app.click();
  assert.equal(app.events.filter((event) => event[1] === 'sponsored_click').length, 1);
  assert.deepEqual(app.events.at(-1)[2], app.events[0][2], 'Click attribution keeps the existing event field definitions');
  app.queue(available(creative({ paymentVerified: false })));
  await app.advance(60000);
  assert.equal(app.elements[0].hidden, true, 'A refunded or no-longer-paid campaign disappears');
  assert.equal(app.click().defaultPrevented, true);
  app.queue(available(creative()));
  await app.advance(60000);
  assert.equal(app.events.filter((event) => event[1] === 'sponsored_impression').length, 1, 'Revalidation of the same campaign is not a new page impression');
  app.queue(available(creative({ campaignId: 'campaign-two' })));
  await app.advance(60000);
  await app.advance(1000);
  assert.equal(app.events.filter((event) => event[1] === 'sponsored_impression').length, 2);
  app.queue(available());
  await app.advance(60000);
  assert.equal(app.elements[0].hidden, true, 'Removal from the response also revokes display');
});

test('open-page expiry hides the card exactly at its end without waiting for the next poll', async () => {
  const app = browser({ payload: available(creative({ endAt: iso(1500) })) });
  await flush();
  await app.advance(1499);
  assert.equal(app.elements[0].hidden, false);
  await app.advance(1);
  assert.equal(app.elements[0].hidden, true);
  assert.equal(app.requests.length, 1);
  assert.equal(app.click().defaultPrevented, true);
});

test('lookup errors, malformed responses and not-ready states remove a previously displayed ad', async () => {
  for (const response of [
    new Error('Network unavailable'), null, {}, { ready: 'true', placements: [creative()] },
    { ready: false, placements: [creative()] }, { ready: true, placements: {} },
    () => ({ ok: false, json: async () => available(creative()) }),
    () => ({ ok: true, json: async () => { throw new Error('Invalid JSON'); } }),
  ]) {
    const app = browser();
    await flush();
    assert.equal(app.elements[0].hidden, false);
    app.queue(response);
    await app.advance(60000);
    assert.equal(app.elements[0].hidden, true);
    assert.equal(app.field('button').href, undefined);
  }
});

test('a hung request times out closed and its later response cannot restore an ad', async () => {
  const app = browser();
  await flush();
  let finish;
  app.queue(() => new Promise((resolve) => { finish = resolve; }));
  await app.advance(60000);
  await app.advance(10000);
  assert.equal(app.elements[0].hidden, true);
  assert.equal(app.requests.at(-1).options.signal.aborted, true);
  finish({ ok: true, json: async () => available(creative()) });
  await flush();
  assert.equal(app.elements[0].hidden, true, 'Late success after timeout is ignored');
});

test('returning to a hidden or cached page requires current verification and ignores stale lookup results', async () => {
  const app = browser({ visibility: 'hidden', readyState: 'loading' });
  app.document.dispatch('DOMContentLoaded');
  await app.advance(120000);
  assert.equal(app.requests.length, 0, 'Hidden pages do not fetch or record impressions');
  await app.visibility('visible');
  assert.equal(app.elements[0].hidden, false);
  let finish;
  app.queue(() => new Promise((resolve) => { finish = resolve; }));
  await app.advance(60000);
  await app.visibility('hidden');
  assert.equal(app.elements[0].hidden, true);
  app.queue(available());
  await app.visibility('visible');
  finish({ ok: true, json: async () => available(creative()) });
  await flush();
  assert.equal(app.elements[0].hidden, true, 'A stale paid response cannot override newer cancellation');
  app.queue(available(creative()));
  app.window.dispatch('pageshow', { persisted: true });
  await flush();
  assert.equal(app.elements[0].hidden, false);
  assert.equal(app.events.filter((event) => event[1] === 'sponsored_impression').length, 1);
  app.window.dispatch('offline');
  assert.equal(app.elements[0].hidden, true);
  app.window.location = new URL('https://coshuma.com/tool/gamma.html');
  const previousRequests = app.requests.length;
  await app.advance(60000);
  assert.equal(app.requests.length, previousRequests, 'A changed protected route never reuses the original allowlist entry');
});

test('impressions require 50% visibility for one uninterrupted second, with no rendering fallback', async () => {
  const unsupported = browser({ observerSupported: false });
  await flush();
  await unsupported.advance(120000);
  assert.equal(unsupported.elements[0].hidden, false);
  assert.equal(unsupported.events.length, 0, 'Without IntersectionObserver, impressions remain unmeasured');
  unsupported.click();
  assert.equal(unsupported.events[0][1], 'sponsored_click', 'Clicks still record without viewability support');

  const app = browser({ intersection: 0 });
  await flush();
  await app.advance(60000);
  assert.equal(app.events.length, 0, 'A card below the viewport is not an impression');
  app.intersection(0.5);
  await app.advance(999);
  assert.equal(app.events.length, 0);
  app.intersection(0.49);
  await app.advance(2000);
  assert.equal(app.events.length, 0, 'Dropping below 50% cancels the partial viewing time');
  app.intersection(0.5);
  await app.advance(999);
  assert.equal(app.events.length, 0);
  await app.advance(1);
  assert.equal(app.events.filter((event) => event[1] === 'sponsored_impression').length, 1);
  app.intersection(0);
  app.intersection(1);
  await app.advance(120000);
  assert.equal(app.events.filter((event) => event[1] === 'sponsored_impression').length, 1, 'Scrolling and polling cannot recount the campaign');
});

test('same-campaign refresh preserves viewing time while revocation, expiry and tab hiding cancel it', async () => {
  const refreshed = browser();
  await flush();
  await refreshed.advance(500);
  refreshed.window.dispatch('online');
  await flush();
  await refreshed.advance(499);
  assert.equal(refreshed.events.length, 0);
  await refreshed.advance(1);
  assert.equal(refreshed.events.filter((event) => event[1] === 'sponsored_impression').length, 1, 'Same-campaign revalidation does not reset the one-second timer');

  for (const reason of ['refund', 'expiry', 'hidden']) {
    const app = browser({ payload: available(creative(reason === 'expiry' ? { endAt: iso(750) } : {})) });
    await flush();
    await app.advance(500);
    if (reason === 'refund') {
      app.queue(available(creative({ paymentVerified: false })));
      app.window.dispatch('online');
      await flush();
    } else if (reason === 'hidden') await app.visibility('hidden');
    await app.advance(1000);
    assert.equal(app.events.length, 0, `${reason} cancels a pending impression`);
    assert.equal(app.elements[0].hidden, true);
    if (reason === 'hidden') {
      await app.visibility('visible');
      await app.advance(999);
      assert.equal(app.events.length, 0, 'Returning to the tab starts a fresh continuous viewing period');
      await app.advance(1);
      assert.equal(app.events.filter((event) => event[1] === 'sponsored_impression').length, 1);
    }
  }
});
