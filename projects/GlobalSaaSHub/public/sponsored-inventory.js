(() => {
  // Master switch. Keep false until COSHUMA explicitly opens sponsored inventory.
  // Reserved slot markup is injected during the production build and stays hidden while this is false.
  const CONFIG = {
    enabled: false,
    // Placement objects may include:
    // enabled, label, title, body, button, url,
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

  function render(slotEl, creative) {
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
    }

    slotEl.hidden = false;
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
