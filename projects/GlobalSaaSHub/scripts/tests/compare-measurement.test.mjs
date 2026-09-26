import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { transformSync } from 'rolldown/experimental';

const read = file => fs.readFileSync(new URL(`../../${file}`, import.meta.url), 'utf8');
function analyticsFixture(search = '', storageFails = false) {
  const store = new Map(), calls = [], listeners = {};
  const storage = { getItem: k => { if (storageFails) throw Error('denied'); return store.get(k) || null; }, setItem: (k,v) => store.set(k,v), removeItem: k => store.delete(k) };
  const window = { location: { search, hostname: 'coshuma.com', pathname: '/', href: `https://coshuma.com/${search}` }, sessionStorage: storage, gtag: (...args) => calls.push(args) };
  const document = { title: 'COSHUMA', referrer: '', querySelector: () => null, querySelectorAll: () => [],
    createElement: () => ({ dataset: {} }), head: { appendChild: node => calls.push(['script', node.src]) }, addEventListener: (k,v) => { listeners[k] = v; } };
  const context = vm.createContext({ window, document, sessionStorage: storage, localStorage: storage, URL, URLSearchParams, Intl, navigator: { language: 'en-US', userAgent: 'test' }, console });
  vm.runInContext(read('src/utils/qa-traffic.js').replaceAll('export ', '') + '\n' + read('src/utils/analytics.js').replace(/^import .*;$/m, '').replaceAll('export ', ''), context);
  return { window, calls, store, context, listeners };
}
test('QA suppresses outbound, comparison, local events and survives internal navigation', () => {
  for (const query of ['?coshuma_qa=1', '?verify=release', '?utm_medium=qa']) {
    const f = analyticsFixture(query);
    vm.runInContext("trackPageView(); trackToolClick('gamma','Gamma','https://try.gamma.app/pu20lusdpn1j',true); trackComparison('compare_open',['gamma'])", f.context);
    f.window.location.search = '';
    vm.runInContext('trackPageView()', f.context);
    assert.equal(f.calls.length, 0);
    assert.equal(f.store.has('coshuma_real_analytics_events_v1'), false);
    f.window.location.search = '?coshuma_qa=0';
    vm.runInContext('trackPageView()', f.context);
    assert.equal(f.calls[0][1], 'page_view');
  }
});
test('customer affiliate versus ordinary outbound classification and source survive analytics failures', () => {
  const f = analyticsFixture();
  vm.runInContext("trackToolClick('gamma','Gamma','https://try.gamma.app/pu20lusdpn1j',true,'home-compare-modal'); trackToolClick('canva','Canva','https://canva.com/',false,'home-compare-modal')", f.context);
  assert.deepEqual(f.calls.map(x => x[1]), ['affiliate_click', 'outbound_click']);
  assert.equal(f.calls[0][2].cta_source, 'home-compare-modal');
  f.window.gtag = () => { throw Error('blocked'); };
  assert.doesNotThrow(() => vm.runInContext("trackToolClick('gamma','Gamma','https://try.gamma.app/pu20lusdpn1j',true);trackComparison('compare_open',['gamma'])", f.context));
});
test('static QA performs no GA loading or events, including storage denial', () => {
  for (const denied of [false, true]) {
    const f = analyticsFixture('?coshuma_qa=1', denied);
    vm.runInContext(read('public/affiliate-attribution.js'), f.context);
    assert.equal(f.calls.length, 0);
    assert.equal(f.window.__coshumaQa, true);
  }
  const customer = analyticsFixture();
  vm.runInContext(read('public/affiliate-attribution.js'), customer.context);
  assert.equal(customer.calls.filter(x => x[1] === 'page_view').length, 1);
});
test('actual modal links retain exact URLs, classify sponsorship, disclose and emit one click', () => {
  const calls = [], tools = [
    { id: 'gamma', name: 'Gamma', is_sponsored: true, url: 'https://try.gamma.app/pu20lusdpn1j' },
    { id: 'canva', name: 'Canva', is_sponsored: false, url: 'https://canva.com/' },
  ];
  const React = { createElement: (type, props, ...children) => ({ type, props: props || {}, children }), useEffect: () => {}, useRef: value => ({ current: value }), useState: value => [value, () => {}] };
  const source = read('src/components/CompareModal.jsx').replace(/^import .*;$/gm, '').replace('export default function', 'function');
  const code = transformSync('CompareModal.jsx', source, { jsx: { runtime: 'classic' } }).code + '\nexports.default = CompareModal;';
  const context = { exports: {}, React, ...React, X: () => {}, ExternalLink: () => {}, Zap: () => {},
    getValidExternalUrl: tool => tool?.url, trackToolClick: (...args) => calls.push(args), trackComparison: () => {} };
  vm.runInNewContext(code, context);
  const tree = context.exports.default({ toolA: tools[0], toolB: tools[1], allTools: tools, onClose: () => {} });
  const nodes = [];
  function walk(node) { if (!node || typeof node !== 'object') return; if (Array.isArray(node)) return node.forEach(walk); nodes.push(node); node.children?.forEach(walk); }
  walk(tree);
  const links = nodes.filter(x => x.type === 'a');
  assert.equal(links.length, 2);
  assert.equal(links[0].props.href, tools[0].url);
  assert.equal(links[0].props.rel, 'sponsored noopener noreferrer');
  assert.equal(links[1].props['data-cta'], 'outbound');
  links[0].props.onClick();
  assert.equal(calls.length, 1);
  assert.equal(calls[0][4], 'home-compare-modal');
  assert.ok(JSON.stringify(tree).includes('Affiliate disclosure:'));
  assert.ok(!JSON.stringify(tree).includes('min-w-[680px]'));
});
