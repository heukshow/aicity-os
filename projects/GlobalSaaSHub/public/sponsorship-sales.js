(() => {
  'use strict';

  const API_BASE = 'https://globalsaashub-payments.qmfforfhem.workers.dev';
  const SESSION_KEY = 'coshuma-ad-application';
  const PAGE_LABELS = {
    '/tool/pipedrive.html': 'Pipedrive tool guide',
    '/best/claap-sales-follow-up-ai.html': 'Claap sales follow-up buyer guide',
    '/compare/semrush-vs-frase.html': 'Semrush vs Frase comparison'
  };
  const SLOTS = ['tool-primary', 'buyer-intent-top', 'compare-decision-premium'];

  function validDestination(value) {
    try {
      const url = new URL(value);
      const host = url.hostname.toLowerCase();
      return url.protocol === 'https:' && !url.username && !url.password
        && host.includes('.') && !host.endsWith('.local') && !host.endsWith('.localhost')
        && !/^(?:localhost|127\.|10\.|192\.168\.|169\.254\.|0\.|172\.(?:1[6-9]|2\d|3[01])\.)/.test(host)
        && !host.includes(':') && value.length <= 1000;
    } catch (_) { return false; }
  }

  function paymentAvailable(config, application) {
    return config?.paymentReady === true && config?.intakeReady === true
      && typeof config.publicClientId === 'string' && config.publicClientId.length > 0
      && application?.paymentReady === true && application?.paymentVerified !== true
      && application?.status === 'awaiting_payment';
  }

  function validQuote(quote, selected) {
    return quote && quote.currency === 'USD' && /^\d+\.\d{2}$/.test(String(quote.amount))
      && Number(quote.amount) > 0 && quote.slot === selected.slot
      && Number(quote.durationDays) === Number(selected.durationDays)
      && quote.targetPage === selected.targetPage;
  }

  function emailDraft(fields) {
    return [
      'COSHUMA sponsored placement application',
      '',
      'Company name: ' + fields.companyName,
      'Tool or product name: ' + fields.toolName,
      'Contact email: ' + fields.contactEmail,
      'Placement: ' + fields.slot,
      'Duration: ' + fields.durationDays + ' days',
      'Target COSHUMA page: ' + fields.targetPage,
      'Destination URL: ' + fields.destinationUrl,
      'Headline: ' + fields.headline,
      'Description: ' + fields.description,
      'Button text: ' + fields.ctaText,
      'Preferred start date: ' + (fields.desiredStartDate || 'To be agreed'),
      '',
      'I am authorized to promote this product, confirm the accuracy of the copy and destination, and accept the sponsorship and privacy terms at https://coshuma.com/sponsorship.html and https://coshuma.com/privacy.html.',
      'Please confirm availability and issue a unique order reference before requesting payment.',
      'Payment identification: company name / tool name / issued COSHUMA order reference.',
      'This email is an application, not a reservation or proof of payment.'
    ].join('\n');
  }

  function safeAnalyticsLink(href) {
    return /^mailto:/i.test(href) ? 'mailto:support@coshuma.com' : href;
  }

  // Export only pure checks for local regression tests; no credentials or live calls.
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { validDestination, paymentAvailable, validQuote, emailDraft, safeAnalyticsLink, statusText };
  }
  if (typeof document === 'undefined') return;
  // The page controls whether external bookings are open.
  if (!['booking','live'].includes(document.body?.dataset.advertisingMode || '')) return;

  function emit(eventName, link) {
    if (!['coshuma.com', 'www.coshuma.com'].includes(window.location.hostname)) return;
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', eventName, {
      cta_source: link.dataset.ctaSource || 'advertise-page',
      link_url: safeAnalyticsLink(link.href),
      link_text: (link.textContent || '').trim().slice(0, 120),
      page_path: window.location.pathname + window.location.search,
      page_location: window.location.href,
      transport_type: 'beacon'
    });
  }

  document.addEventListener('click', (event) => {
    const link = event.target.closest?.('a[data-cta="sponsorship-checkout"], a[data-cta="sponsorship-inquiry"]');
    if (link) emit(link.dataset.cta === 'sponsorship-checkout' ? 'sponsorship_checkout_click' : 'sponsorship_inquiry_click', link);
  }, true);

  let form = document.getElementById('sponsorship-application');
  if (!form) {
    const template = document.getElementById('legacy-text-ad-application');
    if (template?.content) {
      template.before(template.content.cloneNode(true));
      form = document.getElementById('sponsorship-application');
    }
  }
  if (!form) return;
  const byId = (id) => document.getElementById(id);
  const field = (name) => form.elements.namedItem(name);
  const message = byId('application-message');
  const fieldsRoot = form.querySelector('.fields');
  function addFileField(name, id, labelText, helpText) {
    if (!fieldsRoot || form.elements.namedItem(name)) return;
    const wrap = document.createElement('div');
    wrap.className = 'field full';
    const label = document.createElement('label');
    label.htmlFor = id;
    label.textContent = labelText;
    const input = document.createElement('input');
    input.id = id; input.name = name; input.type = 'file'; input.accept = 'image/png,.png'; input.required = true;
    const help = document.createElement('span');
    help.className = 'help'; help.textContent = helpText;
    wrap.append(label, input, help); fieldsRoot.append(wrap);
  }
  addFileField('logoFile', 'ad-logo-file', 'Transparent PNG logo — 400 × 400, max 100 KB',
    'The logo must contain real transparency.');
  addFileField('mainImageFile', 'ad-main-file', 'Placement image — PNG only',
    'F1: 600 × 600. F2: 1200 × 675. F3: 1200 × 400.');
  let config = null;
  let catalog = [];
  let application = null;
  let access = null;
  let quote = null;
  let quoteRequest = 0;
  let busy = false;
  let paypalApplicationId = null;
  let paypalScript = null;

  try {
    catalog = JSON.parse(byId('sponsorship-public-catalog').textContent).catalog || [];
  } catch (_) { /* Online configuration or the email route can still be used. */ }

  function setMessage(element, text, error = false) {
    element.textContent = text;
    element.classList.toggle('error', error);
  }

  async function api(path, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      const headers = { accept: 'application/json', ...options.headers };
      if (options.body) headers['content-type'] = 'application/json';
      const response = await fetch(API_BASE + path, {
        ...options, headers, signal: controller.signal, cache: 'no-store', credentials: 'omit'
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error('The request could not be confirmed. Please refresh or contact support.');
      return result;
    } finally { clearTimeout(timer); }
  }

  function selected() {
    return { slot: field('slot').value, durationDays: Number(field('durationDays').value), targetPage: field('targetPage').value };
  }

  function updateTargetPages() {
    const item = catalog.find((entry) => entry.slot === field('slot').value);
    const previous = field('targetPage').value;
    const pages = (item?.allowedPages || []).filter((page) => Object.hasOwn(PAGE_LABELS, page));
    field('targetPage').replaceChildren();
    for (const page of pages) {
      const option = document.createElement('option');
      option.value = page;
      option.textContent = PAGE_LABELS[page];
      field('targetPage').append(option);
    }
    if (pages.includes(previous)) field('targetPage').value = previous;
  }

  function updateSubmit() {
    const online = config?.intakeReady === true;
    byId('submit-application').textContent = online ? 'Submit application' : 'Prepare email application';
    byId('submit-application').disabled = busy || (online && !quote);
    byId('prepare-email').disabled = busy;
  }

  async function refreshQuote() {
    const request = ++quoteRequest;
    quote = null;
    updateSubmit();
    const choice = selected();
    const item = catalog.find((entry) => entry.slot === choice.slot);
    const listed = item?.prices?.[choice.durationDays];
    setMessage(byId('application-quote'), listed
      ? 'Listed rate: $' + Number(listed).toFixed(2) + ' USD for ' + choice.durationDays + ' days on one page. Availability and the order are confirmed before payment.'
      : 'A final quote is confirmed before payment. Preparing this application does not incur a charge.');
    if (config?.intakeReady !== true || !choice.targetPage) return;
    try {
      const response = await api('/v1/sponsorship/quote?' + new URLSearchParams(choice));
      const result = response.quote || response;
      if (request !== quoteRequest) return;
      if (!validQuote(result, choice)) throw new Error('Quote mismatch');
      quote = result;
      setMessage(byId('application-quote'), 'Quoted total: $' + result.amount + ' ' + result.currency + ' for ' + result.durationDays + ' days on one page. The period starts when the approved placement goes live.');
    } catch (_) {
      if (request === quoteRequest) setMessage(byId('application-quote'), 'An online quote could not be confirmed. Please retry or prepare an email application.', true);
    }
    if (request === quoteRequest) updateSubmit();
  }

  function readFields() {
    if (!form.reportValidity()) return null;
    const names = ['companyName', 'toolName', 'contactEmail', 'slot', 'targetPage', 'destinationUrl', 'headline', 'description', 'ctaText', 'desiredStartDate'];
    const fields = Object.fromEntries(names.map((name) => [name, field(name).value.trim()]));
    fields.durationDays = Number(field('durationDays').value);
    fields.sellerAttestation = field('sellerAttestation').checked === true;
    if (!validDestination(fields.destinationUrl)) {
      setMessage(message, 'Use a public HTTPS destination without a username or password in the URL.', true);
      field('destinationUrl').focus();
      return null;
    }
    if (!SLOTS.includes(fields.slot) || !Object.hasOwn(PAGE_LABELS, fields.targetPage)) {
      setMessage(message, 'Select one of the available placement pages.', true);
      return null;
    }
    return fields;
  }

  function prepareEmail() {
    const fields = readFields();
    if (!fields) return;
    const draft = emailDraft(fields);
    byId('email-draft').value = draft;
    // Keep application details out of clickable URLs and automatic link analytics.
    byId('email-draft-link').href = 'mailto:support@coshuma.com?subject=COSHUMA%20advertising%20application';
    byId('email-application').hidden = false;
    setMessage(message, 'Your draft is ready below. Send it from your email app; this site has not submitted it or created an order.');
    byId('email-application').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function saveAccess() {
    try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(access)); } catch (_) { /* Status remains available in memory. */ }
  }

  function auth() {
    if (!access?.applicationId || !access?.accessToken) throw new Error('Application access is unavailable');
    return { authorization: 'Bearer ' + access.accessToken };
  }

  function applicationPath(suffix = '') {
    return '/v1/ads/applications/' + encodeURIComponent(access.applicationId) + suffix;
  }

  async function uploadAsset(role, file) {
    if (!(file instanceof File) || file.type !== 'image/png') throw new Error('A PNG file is required');
    const limits = { logo: 100000, 'tool-primary': 300000, 'buyer-intent-top': 500000, 'compare-decision-premium': 400000 };
    if (!limits[role] || file.size < 1 || file.size > limits[role]) throw new Error('The PNG file exceeds the position limit');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch(API_BASE + applicationPath('/assets/' + encodeURIComponent(role)), {
        method: 'PUT', headers: { ...auth(), 'content-type': 'image/png' }, body: file,
        signal: controller.signal, cache: 'no-store', credentials: 'omit'
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.error || 'Image upload was not confirmed');
      return result;
    } finally { clearTimeout(timer); }
  }

  function statusText(record) {
    const labels = {
      payment_reversed: 'Payment reversed or refunded — placement stopped',
      rejected: 'Application not accepted',
      paused: 'Placement paused — contact support',
      ended: 'Placement period ended',
      scheduled: 'Payment and copy confirmed — placement scheduled',
      active: 'Placement active',
      preparing_materials: 'Application saved — upload and submit the required PNG materials',
      awaiting_review: 'Materials submitted — awaiting COSHUMA review',
      reservation_expired: 'Approved placement reservation expired — refresh or contact support',
      awaiting_payment: 'Materials approved and position reserved — awaiting payment',
      payment_review: 'Payment requires review — checkout is unavailable',
      ready_to_publish: 'Payment and copy confirmed — awaiting activation',
      awaiting_ad_approval: 'Payment confirmed — your ad copy is awaiting approval'
    };
    if (['active', 'scheduled', 'ready_to_publish'].includes(record.status)
      && (record.paymentVerified !== true || record.approved !== true)) return 'Activation could not be confirmed — contact support';
    return labels[record.status] || 'Current application status requires confirmation';
  }

  function summaryRow(label, value, className = '') {
    const dt = document.createElement('dt');
    dt.textContent = label;
    const dd = document.createElement('dd');
    dd.textContent = value;
    if (className) dd.className = className;
    byId('receipt-summary').append(dt, dd);
  }

  function showApplication() {
    byId('application-receipt').hidden = false;
    byId('receipt-summary').replaceChildren();
    summaryRow('Order reference', application.reference || application.applicationId, 'reference');
    summaryRow('Status', statusText(application));
    if (application.quote) {
      summaryRow('Quoted total', '$' + application.quote.amount + ' ' + application.quote.currency);
      summaryRow('Placement period', application.quote.durationDays + ' days, from actual activation');
      summaryRow('Page', application.quote.targetPage);
    }
    if (application.companyName) summaryRow('Company', application.companyName);
    if (application.toolName) summaryRow('Tool', application.toolName);
    if (application.startAt && application.endAt) summaryRow('Confirmed dates', application.startAt + ' to ' + application.endAt);
    const ready = paymentAvailable(config, application);
    byId('payment-area').hidden = !ready;
    if (!ready) {
      byId('paypal-buttons').replaceChildren();
      paypalApplicationId = null;
      const detail = {
        ended: 'The agreed period has ended. An extension requires a new confirmed period.',
        active: 'Your placement is active for the confirmed dates shown above.',
        scheduled: 'Your placement is scheduled for the confirmed dates shown above.',
        ready_to_publish: 'Payment and copy are confirmed. The purchased period begins at actual activation.',
        awaiting_ad_approval: 'Payment is confirmed. Copy approval and an available placement are still required.',
        payment_reversed: 'The placement is stopped. Contact support with your order reference about the payment.',
        paused: 'The placement is paused. Contact support with your order reference.',
        rejected: 'The application was not accepted. Contact support about any confirmed payment or cancellation request.',
        payment_review: 'Payment requires review. Do not make another payment; contact support with your order reference.'
      };
      const unconfirmedActivation = ['active', 'scheduled', 'ready_to_publish'].includes(application.status)
        && (application.paymentVerified !== true || application.approved !== true);
      setMessage(byId('receipt-message'), (unconfirmedActivation ? 'Activation could not be confirmed. Contact support with your order reference.' : detail[application.status])
        || 'PayPal checkout is not available for this application now. Do not send a separate payment; use your order reference when contacting support.');
    } else {
      setMessage(byId('receipt-message'), 'Your saved application can continue to PayPal. Confirm the order total before approving payment.');
      renderPayPal().catch(() => setMessage(byId('payment-message'), 'PayPal checkout could not load. Refresh your application before trying again; no payment has been confirmed here.', true));
    }
  }

  async function refreshApplication() {
    if (!access) return;
    byId('refresh-application').disabled = true;
    try {
      const result = await api(applicationPath(), { headers: auth() });
      application = result.application || result;
      if (application.applicationId !== access.applicationId) throw new Error('Application mismatch');
      showApplication();
    } catch (_) {
      byId('payment-area').hidden = true;
      setMessage(byId('receipt-message'), 'Current status could not be confirmed. Keep your order reference and contact support if the problem continues.', true);
    } finally { byId('refresh-application').disabled = false; }
  }

  function loadPayPal() {
    if (window.paypal?.Buttons) return Promise.resolve();
    if (paypalScript) return paypalScript;
    paypalScript = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://www.paypal.com/sdk/js?' + new URLSearchParams({
        'client-id': config.publicClientId, currency: 'USD', intent: 'capture', components: 'buttons'
      });
      script.async = true;
      script.onload = () => window.paypal?.Buttons ? resolve() : reject(new Error('PayPal did not load'));
      script.onerror = () => { paypalScript = null; reject(new Error('PayPal did not load')); };
      document.head.append(script);
    });
    return paypalScript;
  }

  async function renderPayPal() {
    if (!paymentAvailable(config, application) || paypalApplicationId === access.applicationId) return;
    const applicationId = access.applicationId;
    await loadPayPal();
    if (!paymentAvailable(config, application) || access.applicationId !== applicationId) return;
    byId('paypal-buttons').replaceChildren();
    let issuedOrderId = null;
    paypalApplicationId = applicationId;
    try { await window.paypal.Buttons({
      createOrder: async () => {
        if (access.applicationId !== applicationId || !paymentAvailable(config, application)) throw new Error('Checkout is not available');
        const result = await api(applicationPath('/order'), { method: 'POST', headers: auth(), body: '{}' });
        if (typeof result.orderId !== 'string' || !result.orderId) throw new Error('Order was not issued');
        issuedOrderId = result.orderId;
        return issuedOrderId;
      },
      onApprove: async (data) => {
        if (access.applicationId !== applicationId || !issuedOrderId || data.orderID !== issuedOrderId) throw new Error('Order mismatch');
        setMessage(byId('payment-message'), 'Checking payment confirmation. Approval alone does not activate the ad.');
        try {
          await api(applicationPath('/capture'), {
            method: 'POST', headers: auth(), body: JSON.stringify({ orderId: issuedOrderId })
          });
        } finally {
          // A failed capture can place the order under review; immediately refresh
          // so a stale unpaid screen cannot keep offering another payment attempt.
          await refreshApplication();
        }
      },
      onCancel: () => setMessage(byId('payment-message'), 'PayPal approval was cancelled. Your application remains available; payment has not been confirmed here.'),
      onError: () => {
        setMessage(byId('payment-message'), 'Payment could not be confirmed. Checking current status; contact support with the order reference if needed.', true);
        refreshApplication();
      }
    }).render('#paypal-buttons');
    } catch (error) { paypalApplicationId = null; throw error; }
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (busy) return;
    if (config?.intakeReady !== true) return prepareEmail();
    const fields = readFields();
    if (!fields) return;
    if (!validQuote(quote, selected())) {
      setMessage(message, 'Wait for the current quote, then submit again. You can also use the email option.', true);
      return;
    }
    busy = true;
    updateSubmit();
    setMessage(message, 'Saving your application…');
    try {
      const logoFile = field('logoFile')?.files?.[0];
      const mainFile = field('mainImageFile')?.files?.[0];
      if (!logoFile || !mainFile) throw new Error('Select both required PNG files');
      if (!(access && application?.status === 'preparing_materials')) {
        const result = await api('/v1/ads/applications', { method: 'POST', body: JSON.stringify(fields) });
        if (!result.applicationId || typeof result.accessToken !== 'string' || !validQuote(result.quote, fields)) throw new Error('Application was not confirmed');
        access = { applicationId: result.applicationId, accessToken: result.accessToken };
        application = result;
        saveAccess();
      }
      setMessage(message, 'Uploading the logo and placement image…');
      await uploadAsset('logo', logoFile);
      await uploadAsset(fields.slot, mainFile);
      setMessage(message, 'Submitting materials for review…');
      const submitted = await api(applicationPath('/submit'), { method: 'POST', headers: auth(), body: '{}' });
      application = submitted.application || submitted;
      showApplication();
      setMessage(message, 'Your materials were submitted for review. No payment is requested until the position is approved and reserved.');
      byId('application-receipt').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (_) {
      setMessage(message, 'Submission was not confirmed. Please check for an existing order reference before retrying, or prepare an email application for support.', true);
    } finally { busy = false; updateSubmit(); }
  });

  byId('prepare-email').addEventListener('click', prepareEmail);
  byId('copy-email-draft').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(byId('email-draft').value);
      setMessage(byId('email-draft-message'), 'Application text copied. Open your email app, paste it into the message and send it to request review.');
    } catch (_) {
      byId('email-draft').focus();
      byId('email-draft').select();
      setMessage(byId('email-draft-message'), 'Select and copy the draft text, then paste it into your email app. Nothing has been sent.');
    }
  });
  byId('refresh-application').addEventListener('click', refreshApplication);
  field('slot').addEventListener('change', () => { updateTargetPages(); refreshQuote(); });
  field('durationDays').addEventListener('change', refreshQuote);
  field('targetPage').addEventListener('change', refreshQuote);

  async function start() {
    updateTargetPages();
    updateSubmit();
    refreshQuote();
    try {
      const result = await api('/v1/ads/config');
      if (!Array.isArray(result.catalog) || result.currency !== 'USD') throw new Error('Configuration unavailable');
      config = result;
      catalog = result.catalog.filter((item) => SLOTS.includes(item.slot));
      updateTargetPages();
      byId('application-availability').replaceChildren();
      const heading = document.createElement('strong');
      heading.textContent = 'Advertising applications are open.';
      const detail = document.createElement('p');
      detail.className = 'small';
      detail.textContent = config.intakeReady === true
        ? (config.paymentReady === true ? 'Online applications are available. PayPal checkout appears after a saved application and a confirmed quote.' : 'Online applications are available. PayPal checkout is currently unavailable; do not send payment until an order is ready.')
        : 'Online submission is not available yet. Use this form to prepare an email application. Do not send payment with your inquiry.';
      byId('application-availability').append(heading, detail);
    } catch (_) {
      config = null;
      byId('application-availability').textContent = 'Advertising inquiries are open by email. Online submission and payment could not be confirmed; use the form below to prepare your email application.';
    }
    updateSubmit();
    await refreshQuote();
    try {
      const saved = JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null');
      if (saved && typeof saved.applicationId === 'string' && saved.applicationId.length < 150
        && typeof saved.accessToken === 'string' && saved.accessToken.length >= 24 && saved.accessToken.length < 300) {
        access = saved;
        await refreshApplication();
      }
    } catch (_) { /* A fresh application remains available if local storage is inaccessible. */ }
  }
  start();
})();
