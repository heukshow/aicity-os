(() => {
  'use strict';

  if (!['coshuma.com', 'www.coshuma.com'].includes(window.location.hostname)) return;

  function emit(eventName, link) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', eventName, {
      cta_source: link.dataset.ctaSource || 'advertise-page',
      link_url: link.href,
      link_text: (link.textContent || '').trim().slice(0, 120),
      page_path: window.location.pathname + window.location.search,
      page_location: window.location.href,
      transport_type: 'beacon'
    });
  }

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-cta="sponsorship-inquiry"]');
    if (!link) return;
    emit('sponsorship_inquiry_click', link);
  }, true);
})();
