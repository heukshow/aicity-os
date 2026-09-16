(() => {
  // Keep this false until the Worker/D1 rollout, no-payment verification, and
  // final checkout readiness review are complete. With this switch false the
  // script makes no sponsorship API request and all reserved slots stay hidden.
  const CONFIG = Object.freeze({
    enabled: false,
    apiBaseUrl: 'https://globalsaashub-payments.qmfforfhem.workers.dev'
  });

  const path = window.location.pathname;

  function isActiveFlight(creative) {
    const now = Date.now();
    const start = creative.startAt ? Date.parse(creative.startAt) : null;
    const end = creative.endAt ? Date.parse(creative.endAt) : null;
    if (creative.startAt && Number.isNaN(start)) return false;
    if (creative.endAt && Number.isNaN(end)) return false;
    if (start !== null && now < start) return false;
    if (end !== null && now >= end) return false;
    return true;
  }

  function hostnameFromUrl(url) {
    try {
      return new URL(url, window.location.href).hostname || 'unknown';
    } catch {
      return 'unknown';
    }
  }

  function emitAnalytics(eventName, creative, slot) {
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

  function emitVerifiedEvent(eventName, creative) {
    if (!CONFIG.enabled || !creative.campaignId || !creative.url) return;
    const body = JSON.stringify({
      eventType: eventName,
      campaignId: creative.campaignId,
      page: path,
      destinationUrl: creative.url
    });
    fetch(`${CONFIG.apiBaseUrl}/v1/sponsored/events`, {
      method: 'POST',
      mode: 'cors',
      keepalive: true,
      headers: { 'content-type': 'application/json' },
      body
    }).catch(() => {});
  }

  function emit(eventName, creative, slot) {
    emitAnalytics(eventName, creative, slot);
    emitVerifiedEvent(eventName, creative);
  }

  function render(slotEl, creative) {
    const slot = slotEl.dataset.sponsoredSlot || '';
    const label = slotEl.querySelector('[data-sponsored-label]');
    const title = slotEl.querySelector('[data-sponsored-title]');
    const body = slotEl.querySelector('[data-sponsored-body]');
    const button = slotEl.querySelector('[data-sponsored-button]');

    if (label) label.textContent = creative.label || 'Sponsored';
    if (title) title.textContent = creative.title || '';
    if (body) body.textContent = creative.body || '';
    if (button) {
      button.textContent = creative.button || 'Learn more →';
      button.href = creative.url;
      button.setAttribute('rel', 'sponsored noopener noreferrer');
      button.setAttribute('target', '_blank');
      button.dataset.sponsorCampaignId = creative.campaignId;
      button.addEventListener('click', () => emit('sponsored_click', creative, slot), { capture: true });
    }

    slotEl.hidden = false;
    emit('sponsored_impression', creative, slot);
  }

  async function loadPlacements() {
    if (!CONFIG.enabled) return [];
    try {
      const response = await fetch(`${CONFIG.apiBaseUrl}/v1/sponsored/placements?path=${encodeURIComponent(path)}`, {
        method: 'GET',
        mode: 'cors',
        credentials: 'omit',
        headers: { accept: 'application/json' }
      });
      if (!response.ok) return [];
      const data = await response.json();
      if (!data || data.ready !== true || !Array.isArray(data.placements)) return [];
      return data.placements.filter((creative) =>
        creative
        && typeof creative.slot === 'string'
        && typeof creative.campaignId === 'string'
        && typeof creative.url === 'string'
        && creative.url.startsWith('https://')
        && isActiveFlight(creative)
      );
    } catch {
      return [];
    }
  }

  document.addEventListener('DOMContentLoaded', async () => {
    const slots = Array.from(document.querySelectorAll('[data-sponsored-slot]'));
    slots.forEach((slotEl) => { slotEl.hidden = true; });
    if (!CONFIG.enabled || slots.length === 0) return;

    const placements = await loadPlacements();
    const bySlot = new Map();
    placements.forEach((creative) => {
      if (!bySlot.has(creative.slot)) bySlot.set(creative.slot, creative);
    });
    slots.forEach((slotEl) => {
      const creative = bySlot.get(slotEl.dataset.sponsoredSlot || '');
      if (creative) render(slotEl, creative);
    });
  });
})();
