(() => {
  'use strict';
  const routes = {
    '/tool/pipedrive.html': ['tool-primary', '/best/index.html'],
    '/best/claap-sales-follow-up-ai.html': ['buyer-intent-top', '/best/claap-sales-follow-up-ai.html#claap-3-call-checklist'],
    '/compare/semrush-vs-frase.html': ['compare-decision-premium', '/compare/']
  };
  function init() {
    const path = window.location.pathname;
    const route = routes[path];
    if (!route) return;
    const cards = document.querySelectorAll('[data-coshuma-promotion]');
    if (cards.length !== 1) { cards.forEach(card => { card.hidden = true; }); return; }
    const card = cards[0];
    const paid = card.previousElementSibling;
    const link = card.querySelector('[data-promotion-link]');
    const image = card.querySelector('.coshuma-promotion__image');
    if (card.dataset.promotionPage !== path || card.dataset.promotionSlot !== route[0]
        || !paid || paid.dataset.sponsoredSlot !== route[0] || !link || !image
        || link.getAttribute('href') !== route[1]) { card.hidden = true; return; }
    const qa = new URLSearchParams(window.location.search).get('coshuma_qa') === '1';
    if (qa) {
      const destination = new URL(route[1], window.location.origin);
      destination.searchParams.set('coshuma_qa', '1');
      link.href = destination.pathname + destination.search + destination.hash;
    }
    const interest = card.querySelector('[data-advertiser-interest]');
    const interestPath = '/advertise.html?placement=' + route[0] + '#inquire';
    if (interest && interest.getAttribute('href') === interestPath) {
      if (qa) interest.href = '/advertise.html?placement=' + route[0] + '&coshuma_qa=1#inquire';
      interest.addEventListener('click', event => {
        if (!available()) { event.preventDefault(); return; }
        if (!qa && typeof window.gtag === 'function') window.gtag('event', 'advertiser_interest_click', { promotion_slot: route[0], page_path: path, destination_path: '/advertise.html', transport_type: 'beacon' });
      });
    }
    let seen = false, timer = null, inView = false;
    function stopTimer() { window.clearTimeout(timer); timer = null; }
    function available() {
      return !card.hidden && paid.hidden && document.visibilityState === 'visible'
        && window.location.pathname === path
        && window.getComputedStyle(card).display !== 'none';
    }
    function measurable() { return available() && image.complete && image.naturalWidth > 0; }
    function emit(name) {
      if (qa || typeof window.gtag !== 'function') return false;
      if (name !== 'coshuma_promo_view' && name !== 'coshuma_promo_click') return false;
      window.gtag('event', name, {
        promotion_id: card.dataset.coshumaPromotion,
        promotion_slot: route[0],
        page_path: path,
        destination_path: route[1],
        transport_type: 'beacon'
      });
      return true;
    }
    function checkView() {
      if (seen || qa || !inView || !measurable()) { stopTimer(); return; }
      if (timer === null) timer = window.setTimeout(() => {
        timer = null;
        if (!seen && inView && measurable()) seen = emit('coshuma_promo_view');
      }, 1000);
    }
    function sync() {
      card.hidden = !paid.hidden || window.location.pathname !== path;
      checkView();
    }
    link.addEventListener('click', (event) => {
      if (!available()) { event.preventDefault(); return; }
      emit('coshuma_promo_click');
    });
    if (typeof window.MutationObserver === 'function') {
      const observer = new window.MutationObserver(sync);
      observer.observe(paid, { attributes: true, attributeFilter: ['hidden'] });
    }
    if (typeof window.IntersectionObserver === 'function' && !qa) {
      const observer = new window.IntersectionObserver(entries => {
        for (const entry of entries) if (entry.target === card) {
          inView = entry.isIntersecting === true && entry.intersectionRatio >= 0.5;
          checkView();
        }
      }, { threshold: [0, 0.5] });
      observer.observe(card);
    }
    image.addEventListener('load', checkView);
    image.addEventListener('error', stopTimer);
    document.addEventListener('visibilitychange', sync);
    window.addEventListener('pagehide', stopTimer);
    window.addEventListener('pageshow', sync);
    sync();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
