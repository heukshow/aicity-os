(() => {
  const API_BASE = 'https://globalsaashub-payments.qmfforfhem.workers.dev';
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
    try { return new URL(url, window.location.href).hostname || 'unknown'; }
    catch { return 'unknown'; }
  }

  function emit(eventName, creative, slot) {
    if (typeof window.gtag === 'function') {
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
    if (!creative.campaignId) return;
    fetch(`${API_BASE}/v1/advertiser/events`, {
      method: 'POST',
      mode: 'cors',
      keepalive: true,
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        campaignId: creative.campaignId,
        eventType: eventName,
        page: window.location.pathname,
        placement: creative.placement || slot || '',
        destinationUrl: creative.url || ''
      })
    }).catch(() => {});
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
      button.href = creative.url || '#';
      button.setAttribute('rel', 'sponsored noopener noreferrer');
      button.setAttribute('target', '_blank');
      button.dataset.sponsorCampaignId = creative.campaignId || 'unspecified';
      button.addEventListener('click', () => emit('sponsored_click', creative, slot), { capture: true });
    }
    slotEl.hidden = false;
    emit('sponsored_impression', creative, slot);
  }

  async function loadPlacements() {
    const slots = [...document.querySelectorAll('[data-sponsored-slot]')];
    slots.forEach((slotEl) => { slotEl.hidden = true; });
    if (!slots.length) return;
    try {
      const response = await fetch(`${API_BASE}/v1/sponsored/placements?path=${encodeURIComponent(path)}`, { mode: 'cors' });
      if (!response.ok) return;
      const data = await response.json();
      const placements = Array.isArray(data.placements) ? data.placements : [];
      const bySlot = new Map(placements.filter((creative) => creative && creative.slot && creative.url && isActiveFlight(creative)).map((creative) => [creative.slot, creative]));
      slots.forEach((slotEl) => {
        const creative = bySlot.get(slotEl.dataset.sponsoredSlot || '');
        if (creative) render(slotEl, creative);
      });
    } catch {
      // Fail closed: sponsored inventory stays hidden when campaign API is unavailable.
    }
  }

  document.addEventListener('DOMContentLoaded', loadPlacements);
})();
