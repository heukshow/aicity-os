(() => {
  // Master switch. Keep false until COSHUMA explicitly opens sponsored inventory.
  // Reserved slot markup is injected during the production build and stays hidden while this is false.
  const CONFIG = {
    enabled: false,
    // Placement objects may include:
    // enabled, campaignId, label, title, body, button, url,
    // startAt, endAt (ISO 8601 timestamps, UTC recommended).
    placements: {}
  };

  const path = window.location.pathname;

  function placementFor(slot) {
    return CONFIG.placements[`${path}::${slot}`] || CONFIG.placements[`*::${slot}`] || null;
  }

  function isActiveFlight(creative) {
    const now = Date.now();
    const start = creative.startAt ? Date.parse(creative.startAt) : null;
    const end = creative.endAt ? Date.parse(creative.endAt) : null;

    // Invalid dates fail closed so a malformed campaign never shows indefinitely.
    if (creative.startAt && Number.isNaN(start)) return false;
    if (creative.endAt && Number.isNaN(end)) return false;
    if (start !== null && now < start) return false;
    if (end !== null && now >= end) return false;
    return true;
  }

  function hostnameFromUrl(url) {
    try {
      return new URL(url, window.location.href).hostname || 'unknown';
    } catch (error) {
      return 'unknown';
    }
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

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-sponsored-slot]').forEach((slotEl) => {
      slotEl.hidden = true;
      if (!CONFIG.enabled) return;
      const creative = placementFor(slotEl.dataset.sponsoredSlot || '');
      if (!creative || creative.enabled !== true || !creative.url || !isActiveFlight(creative)) return;
      render(slotEl, creative);
    });
  });
})();
