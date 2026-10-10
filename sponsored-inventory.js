(() => {
  const API = 'https://globalsaashub-payments.qmfforfhem.workers.dev/v1/sponsored/placements';
  const CONFIG = Object.freeze({ enabled: false });
  // These are the only pages opened for sponsored inventory. Never use wildcard placements.
  const ALLOWED_SLOTS = {
    '/tool/pipedrive.html': 'tool-primary',
    '/best/claap-sales-follow-up-ai.html': 'buyer-intent-top',
    '/compare/semrush-vs-frase.html': 'compare-decision-premium'
  };
  const REFRESH_MS = 60000;
  const REQUEST_TIMEOUT_MS = 10000;

  function timestamp(value) {
    if (typeof value !== 'string') return NaN;
    const match = /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,3}))?Z$/.exec(value);
    const time = Date.parse(value);
    // Require real UTC dates; Date.parse alone can normalize invalid calendar days.
    if (!match || !Number.isFinite(time)) return NaN;
    return new Date(time).toISOString() === `${match[1]}.${(match[2] || '').padEnd(3, '0')}Z` ? time : NaN;
  }

  function hostnameFromUrl(url) {
    try {
      return new URL(url).hostname || 'unknown';
    } catch (error) {
      return 'unknown';
    }
  }

  function validCreative(creative) {
    if (creative.environment !== 'live' || creative.paymentVerified !== true ||
        creative.approved !== true || creative.status !== 'published') return null;
    for (const key of ['campaignId', 'title', 'body', 'button', 'url']) {
      if (typeof creative[key] !== 'string' || !creative[key].trim()) return null;
    }
    const start = timestamp(creative.startAt);
    const end = timestamp(creative.endAt);
    if (!Number.isFinite(start) || !Number.isFinite(end) || start >= end || Date.now() < start || Date.now() >= end) return null;
    try {
      const url = new URL(creative.url);
      const hostname = url.hostname.replace(/\.$/, '');
      if (url.protocol !== 'https:' || !hostname || url.username || url.password ||
          hostname === window.location.hostname.replace(/\.$/, '') || /(^|\.)coshuma\.com$/i.test(hostname)) return null;
    } catch (error) {
      return null;
    }
    // Only public creative fields are retained. Payment and applicant records never enter the DOM or analytics.
    return { campaignId: creative.campaignId, title: creative.title, body: creative.body,
      button: creative.button, url: creative.url, start, end };
  }

  function emit(eventName, creative, slot) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', eventName, {
      sponsor_campaign_id: creative.campaignId || 'unspecified',
      sponsored_slot: slot || 'unspecified',
      sponsor_title: creative.title || '',
      link_url: creative.url || '',
      outbound_domain: hostnameFromUrl(creative.url || ''),
      page_path: window.location.pathname + window.location.search,
      page_location: window.location.href,
      transport_type: 'beacon'
    });
  }

  function init() {
    const slots = Array.from(document.querySelectorAll('[data-sponsored-slot]'));
    slots.forEach((slotEl) => { slotEl.hidden = true; });
    if (!CONFIG.enabled) return;
    const path = window.location.pathname;
    const slot = ALLOWED_SLOTS[path];
    const matchingSlots = slots.filter((slotEl) => slotEl.dataset.sponsoredSlot === slot);
    if (!slot || matchingSlots.length !== 1) return;
    const slotEl = matchingSlots[0];
    const label = slotEl.querySelector('[data-sponsored-label]');
    const title = slotEl.querySelector('[data-sponsored-title]');
    const body = slotEl.querySelector('[data-sponsored-body]');
    const button = slotEl.querySelector('[data-sponsored-button]');
    if (!label || !title || !body || !button) return;

    let active = null;
    let expiryTimer = null;
    let pending = null;
    let requestSequence = 0;
    const impressions = new Set();
    let impressionTimer = null;
    let observer = null;
    let observationGeneration = 0;
    let inView = false;

    function stopMeasurement() {
      observationGeneration += 1;
      window.clearTimeout(impressionTimer);
      impressionTimer = null;
      inView = false;
      if (observer) observer.disconnect();
      observer = null;
    }

    function measurable() {
      return active && !slotEl.hidden && inView && document.visibilityState === 'visible' &&
        window.location.pathname === path && Date.now() >= active.start && Date.now() < active.end;
    }

    function observeImpression() {
      // Unsupported browsers leave impressions unmeasured; rendering is not evidence of viewing.
      if (typeof window.IntersectionObserver !== 'function' || impressions.has(active.campaignId)) return;
      const generation = observationGeneration;
      const campaignId = active.campaignId;
      observer = new window.IntersectionObserver((entries) => {
        if (generation !== observationGeneration) return;
        for (const entry of entries) {
          if (entry.target !== slotEl) continue;
          inView = entry.isIntersecting === true && entry.intersectionRatio >= 0.5;
          if (!measurable()) {
            window.clearTimeout(impressionTimer);
            impressionTimer = null;
          } else if (impressionTimer === null && !impressions.has(campaignId)) {
            impressionTimer = window.setTimeout(() => {
              impressionTimer = null;
              if (generation !== observationGeneration || !measurable() ||
                  active.campaignId !== campaignId || impressions.has(campaignId)) return;
              impressions.add(campaignId);
              emit('sponsored_impression', active, slot);
            }, 1000);
          }
        }
      }, { threshold: [0, 0.5] });
      observer.observe(slotEl);
    }

    function hide() {
      stopMeasurement();
      slots.forEach((element) => { element.hidden = true; });
      active = null;
      window.clearTimeout(expiryTimer);
      expiryTimer = null;
      button.removeAttribute('href');
      delete button.dataset.sponsorCampaignId;
    }

    function cancel() {
      requestSequence += 1;
      if (pending) pending.abort();
      pending = null;
      hide();
    }

    function scheduleExpiry() {
      window.clearTimeout(expiryTimer);
      if (!active) return;
      if (Date.now() >= active.end) { hide(); return; }
      expiryTimer = window.setTimeout(scheduleExpiry, Math.min(active.end - Date.now(), REFRESH_MS));
    }

    function render(creative) {
      const sameCampaign = active?.campaignId === creative.campaignId && !slotEl.hidden;
      if (!sameCampaign) stopMeasurement();
      active = creative;
      label.textContent = 'Sponsored';
      title.textContent = creative.title;
      body.textContent = creative.body;
      button.textContent = creative.button;
      button.href = creative.url;
      button.setAttribute('rel', 'sponsored noopener noreferrer');
      button.setAttribute('target', '_blank');
      button.dataset.sponsorCampaignId = creative.campaignId;
      slotEl.hidden = false;
      scheduleExpiry();
      if (active && !sameCampaign) observeImpression();
    }

    button.addEventListener('click', (event) => {
      if (!active || slotEl.hidden || window.location.pathname !== path || Date.now() < active.start || Date.now() >= active.end) {
        event.preventDefault();
        hide();
        return;
      }
      emit('sponsored_click', active, slot);
    }, { capture: true });

    async function refresh() {
      if (window.location.pathname !== path || document.visibilityState === 'hidden') { cancel(); return; }
      if (active && (Date.now() < active.start || Date.now() >= active.end)) hide();
      const sequence = ++requestSequence;
      if (pending) pending.abort();
      const controller = new AbortController();
      pending = controller;
      const timeout = window.setTimeout(() => {
        if (sequence === requestSequence) cancel();
      }, REQUEST_TIMEOUT_MS);

      try {
        const response = await window.fetch(`${API}?path=${encodeURIComponent(path)}`, {
          mode: 'cors', credentials: 'omit', cache: 'no-store', redirect: 'error',
          referrerPolicy: 'no-referrer', signal: controller.signal
        });
        if (!response.ok) throw new Error('Placement lookup failed');
        const payload = await response.json();
        if (sequence !== requestSequence) return;
        if (window.location.pathname !== path || document.visibilityState === 'hidden') { cancel(); return; }
        if (payload?.ready !== true || !Array.isArray(payload.placements)) { hide(); return; }
        const matches = payload.placements.filter((creative) =>
          creative && creative.targetPage === path && creative.slot === slot);
        // An ambiguous response must not choose an advertiser by array order.
        const creative = matches.length === 1 ? validCreative(matches[0]) : null;
        if (creative) render(creative);
        else hide();
      } catch (error) {
        if (sequence === requestSequence) hide();
      } finally {
        window.clearTimeout(timeout);
        if (sequence === requestSequence) pending = null;
      }
    }

    document.addEventListener('visibilitychange', refresh);
    window.addEventListener('pagehide', cancel);
    window.addEventListener('pageshow', (event) => { if (event.persisted) refresh(); });
    window.addEventListener('offline', cancel);
    window.addEventListener('online', refresh);
    window.setInterval(refresh, REFRESH_MS);
    hide();
    refresh();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
