/* Inquiry-only experience. Entered values are never sent to an API or analytics. */
(() => {
  'use strict';
  if (typeof document === 'undefined' || document.body?.dataset.advertisingMode !== 'inquiry') return;
  const slots = {
    'tool-primary': { label: 'Tool page', page: '/tool/pipedrive.html' },
    'buyer-intent-top': { label: 'Buyer guide', page: '/best/claap-sales-follow-up-ai.html' },
    'compare-decision-premium': { label: 'Comparison', page: '/compare/semrush-vs-frase.html' }
  };
  const params = new URLSearchParams(window.location.search);
  const qa = params.get('coshuma_qa') === '1';
  const field = id => document.getElementById(id);
  const tabs = [...document.querySelectorAll('[data-example]')];
  const panels = [...document.querySelectorAll('[data-example-panel]')];
  function metric(action, slot = 'undecided') {
    if (qa || !['coshuma.com', 'www.coshuma.com'].includes(window.location.hostname) || typeof window.gtag !== 'function') return;
    if (!['example_selected','hero-inquiry','closing-inquiry','direct-email','draft-email','brief_prepared','brief_copied','placement_inquiry'].includes(action)) return;
    window.gtag('event', 'advertiser_interest', { action, placement: Object.hasOwn(slots, slot) ? slot : 'undecided', page_path: '/advertise.html', transport_type: 'beacon' });
  }
  function selectExample(slot) {
    if (!Object.hasOwn(slots, slot)) return;
    for (const panel of panels) panel.hidden = panel.dataset.examplePanel !== slot;
    for (const tab of tabs) tab.setAttribute('aria-pressed', String(tab.dataset.example === slot));
  }
  for (const tab of tabs) tab.addEventListener('click', () => { selectExample(tab.dataset.example); metric('example_selected', tab.dataset.example); });
  const requested = params.get('placement');
  selectExample(Object.hasOwn(slots, requested) ? requested : 'tool-primary');
  if (Object.hasOwn(slots, requested)) field('brief-slot').value = requested;
  for (const link of document.querySelectorAll('[data-choose-placement]')) link.addEventListener('click', () => {
    const slot = link.dataset.choosePlacement;
    if (Object.hasOwn(slots, slot)) { field('brief-slot').value = slot; metric('placement_inquiry', slot); }
  });
  for (const link of document.querySelectorAll('[data-showcase-action]')) link.addEventListener('click', () => metric(link.dataset.showcaseAction, field('brief-slot').value));
  if (qa) for (const link of document.querySelectorAll('[data-live-example]')) {
    const url = new URL(link.getAttribute('href'), window.location.origin);
    if (url.origin === window.location.origin && Object.values(slots).some(slot => slot.page === url.pathname)) {
      url.searchParams.set('coshuma_qa','1'); link.href = url.pathname + url.search + url.hash;
    }
  }
  function publicHttps(value) {
    try {
      const url = new URL(value); const host = url.hostname.toLowerCase();
      return url.protocol === 'https:' && !url.username && !url.password && host.includes('.') && !host.endsWith('.local') && !host.endsWith('.localhost') && !host.includes(':') && !/^\d+(\.\d+){3}$/.test(host) && value.length <= 1000;
    } catch { return false; }
  }
  const form = field('advertiser-brief');
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const name = field('brief-product').value.trim().replace(/[\r\n\u0000-\u001f]/g, ' ');
    const url = field('brief-url').value.trim();
    const slot = field('brief-slot').value;
    const period = field('brief-period').value;
    const goal = field('brief-goal').value.trim();
    const result = field('brief-result');
    if (!name || name.length > 120 || !publicHttps(url) || goal.length > 500 || !['undecided',...Object.keys(slots)].includes(slot) || !['undecided','7','30','90'].includes(period)) {
      result.textContent = 'Check your product name and use a public HTTPS website. No inquiry has been sent.';
      result.classList.add('error'); return;
    }
    const choice = slots[slot];
    const draft = ['Hello COSHUMA,', '', 'I would like to discuss an advertising placement.', '',
      'Product / company: ' + name, 'Product website: ' + url,
      'Preferred placement: ' + (choice ? choice.label : 'Please help me choose'),
      'COSHUMA page: ' + (choice ? 'https://coshuma.com' + choice.page : 'To discuss'),
      'Preferred period: ' + (period === 'undecided' ? 'To discuss' : period + ' days'),
      'Goal / use case / preferred dates: ' + (goal || 'To discuss'), '',
      'Please confirm product fit, future availability, page-specific traffic evidence or its limitations, and the proposed scope and quote.',
      'I understand this is an inquiry, not a reservation or payment.'].join('\n');
    field('brief-draft').value = draft;
    field('brief-draft-box').hidden = false;
    result.classList.remove('error');
    result.textContent = 'Draft prepared on this page. Copy it and send it from your email app; nothing has been submitted.';
    field('brief-copy-status').textContent = '';
    metric('brief_prepared', slot);
    field('brief-draft-box').scrollIntoView({ block:'nearest', behavior:'auto' });
  });
  field('copy-brief').addEventListener('click', async () => {
    if (!field('brief-draft').value) return;
    try {
      await navigator.clipboard.writeText(field('brief-draft').value);
      field('brief-copy-status').textContent = 'Copied. Open your email app, paste the inquiry and send it to support@coshuma.com.';
      metric('brief_copied', field('brief-slot').value);
    } catch {
      field('brief-draft').focus(); field('brief-draft').select();
      field('brief-copy-status').textContent = 'Select and copy the draft, then paste it into your email. Nothing has been sent.';
    }
  });
  field('prepare-brief').disabled = false;
})();
