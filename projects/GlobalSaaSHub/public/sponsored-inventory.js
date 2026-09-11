(() => {
  // Master switch. Keep false until COSHUMA explicitly opens sponsored inventory.
  const CONFIG = {
    enabled: false,
    placements: {}
  };

  const path = window.location.pathname;

  function placementFor(slot) {
    return CONFIG.placements[`${path}::${slot}`] || CONFIG.placements[`*::${slot}`] || null;
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
      if (!creative || creative.enabled !== true || !creative.url) return;
      render(slotEl, creative);
    });
  });
})();
