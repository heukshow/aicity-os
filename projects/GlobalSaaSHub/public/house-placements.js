/* First-party house demonstrations only. No paid API, payment state or external ad source. */
(() => {
  'use strict';
  const allowed = {
    'tool-rotation': ['/tool/pipedrive.html'],
    'guide-rotation': ['/best/claap-sales-follow-up-ai.html'],
    'compare-rotation': ['/compare/semrush-vs-frase.html'],
    'buyer-hub-fixed': ['/best/index.html', '/best/'],
    'comparison-hub-fixed': ['/compare/', '/compare/index.html']
  };
  const destinations = new Set(['/best/index.html', '/compare/', '/best/claap-sales-follow-up-ai.html#claap-3-call-checklist']);
  const ids = new Set(['coshuma-guides', 'coshuma-checklist', 'coshuma-comparisons']);
  const imagePaths = new Set(['/promotions/house-wide-guides.webp', '/promotions/house-wide-checklist.webp', '/promotions/house-wide-comparisons.webp']);
  function init() {
    const path = location.pathname;
    const qa = new URLSearchParams(location.search).get('coshuma_qa') === '1';
    const units = [...document.querySelectorAll('[data-house-slot]')];
    for (const unit of units) {
      const slot = unit.dataset.houseSlot;
      const mode = unit.dataset.houseMode;
      const rotating = slot.endsWith('-rotation');
      const slides = [...unit.querySelectorAll('[data-house-slide]')];
      const capacity = rotating ? 3 : 1;
      const valid = allowed[slot]?.includes(path) && mode === (rotating ? 'rotating' : 'fixed') &&
        units.filter(u => u.dataset.houseSlot === slot).length === 1 && slides.length >= 1 && slides.length <= capacity &&
        new Set(slides.map(s => s.dataset.houseSlide)).size === slides.length && slides.every(s => {
          const img = s.querySelector('img'), link = s.querySelector('[data-house-link]');
          return ids.has(s.dataset.houseSlide) && img && link && imagePaths.has(img.getAttribute('src')) &&
            img.getAttribute('width') === '1200' && img.getAttribute('height') === '400' && destinations.has(link.getAttribute('href'));
        });
      if (!valid) { unit.hidden = true; continue; }
      const controls = unit.querySelector('[data-house-controls]');
      const play = unit.querySelector('[data-house-play]');
      const previous = unit.querySelector('[data-house-prev]');
      const next = unit.querySelector('[data-house-next]');
      const count = unit.querySelector('[data-house-count]');
      const content = unit.querySelector('[data-house-slides]');
      if (rotating && (!controls || !play || !previous || !next || !count || !content)) { unit.hidden = true; continue; }
      const multiple = rotating && slides.length > 1;
      const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
      let index = multiple ? Math.floor(Math.random() * slides.length) : 0;
      let paused = motion.matches, hovered = false, inView = false, closed = false;
      let rotationTimer = null, impressionTimer = null, pressWantsStart = null;
      const seen = new Set();
      const visible = () => !closed && !unit.hidden && inView && document.visibilityState === 'visible' &&
        location.pathname === path && getComputedStyle(unit).display !== 'none';
      const emit = (name, slide) => {
        if (qa || !['coshuma.com', 'www.coshuma.com'].includes(location.hostname) || typeof window.gtag !== 'function') return false;
        window.gtag('event', name, { placement_id: slot, creative_id: slide.dataset.houseSlide,
          placement_format: mode, page_path: path, transport_type: 'beacon' });
        return true;
      };
      const stopRotation = () => { clearTimeout(rotationTimer); rotationTimer = null; };
      const stopImpression = () => { clearTimeout(impressionTimer); impressionTimer = null; };
      function sync() {
        if (play) play.textContent = paused ? 'Play rotation' : 'Pause rotation';
        if (content) content.setAttribute('aria-live', paused ? 'polite' : 'off');
        if (!multiple || paused || hovered || !visible()) stopRotation();
        else if (rotationTimer === null) rotationTimer = setTimeout(() => {
          rotationTimer = null;
          if (!paused && !hovered && visible()) show((index + 1) % slides.length);
        }, 8000);
        const slide = slides[index], image = slide.querySelector('img');
        const measurable = visible() && !slide.hidden && image.complete && image.naturalWidth > 0;
        if (!measurable || seen.has(slide.dataset.houseSlide)) stopImpression();
        else if (impressionTimer === null) impressionTimer = setTimeout(() => {
          impressionTimer = null;
          if (visible() && slides[index] === slide && !slide.hidden && image.complete && image.naturalWidth > 0 && !seen.has(slide.dataset.houseSlide)) {
            if (emit('house_placement_impression', slide)) seen.add(slide.dataset.houseSlide);
          }
        }, 1000);
      }
      function show(value) {
        stopRotation(); stopImpression(); index = value;
        slides.forEach((s, i) => { s.hidden = i !== index; });
        if (count) count.textContent = `${index + 1} / ${slides.length}`;
        unit.dataset.activeCreative = slides[index].dataset.houseSlide;
        sync();
      }
      for (const slide of slides) {
        const link = slide.querySelector('[data-house-link]');
        if (qa) { const url = new URL(link.getAttribute('href'), location.origin); url.searchParams.set('coshuma_qa', '1'); link.href = url.pathname + url.search + url.hash; }
        link.addEventListener('click', event => {
          if (slide !== slides[index] || slide.hidden || unit.hidden || location.pathname !== path) { event.preventDefault(); return; }
          emit('house_placement_click', slide);
        });
        slide.querySelector('img').addEventListener('load', sync);
        slide.querySelector('img').addEventListener('error', stopImpression);
      }
      const inquiry = unit.querySelector('[data-house-inquiry]');
      if (inquiry) {
        const expected = '/advertise.html?placement=' + slot + '#inquire';
        if (inquiry.getAttribute('href') !== expected) inquiry.hidden = true;
        else {
          if (qa) inquiry.href = '/advertise.html?placement=' + slot + '&coshuma_qa=1#inquire';
          inquiry.addEventListener('click', () => { emit('house_placement_inquiry', slides[index]); });
        }
      }
      if (multiple) {
        controls.hidden = false;
        unit.addEventListener('mouseenter', () => { hovered = true; sync(); });
        unit.addEventListener('mouseleave', () => { hovered = false; sync(); });
        unit.addEventListener('focusin', () => { paused = true; sync(); });
        play.addEventListener('pointerdown', () => { pressWantsStart = paused; });
        play.addEventListener('click', () => { paused = pressWantsStart === null ? !paused : !pressWantsStart; pressWantsStart = null; sync(); });
        previous.addEventListener('click', () => { paused = true; show((index + slides.length - 1) % slides.length); });
        next.addEventListener('click', () => { paused = true; show((index + 1) % slides.length); });
        // Horizontal touch gestures do not prevent ordinary vertical page scrolling.
        let touch = null;
        content.addEventListener('touchstart', e => { const t = e.touches[0]; touch = t ? [t.clientX, t.clientY] : null; }, { passive: true });
        content.addEventListener('touchend', e => {
          if (!touch || !e.changedTouches[0]) return;
          const t = e.changedTouches[0], dx = t.clientX - touch[0], dy = t.clientY - touch[1]; touch = null;
          if (Math.abs(dx) > 55 && Math.abs(dy) < 35) { paused = true; show((index + (dx < 0 ? 1 : slides.length - 1)) % slides.length); }
        }, { passive: true });
      }
      if (typeof IntersectionObserver === 'function') {
        const observer = new IntersectionObserver(entries => {
          for (const entry of entries) if (entry.target === unit) { inView = entry.isIntersecting && entry.intersectionRatio >= 0.5; sync(); }
        }, { threshold: [0, 0.5] });
        observer.observe(unit);
      }
      motion.addEventListener?.('change', () => { if (motion.matches) paused = true; sync(); });
      document.addEventListener('visibilitychange', sync);
      window.addEventListener('pagehide', () => { closed = true; stopRotation(); stopImpression(); });
      window.addEventListener('pageshow', () => { closed = false; sync(); });
      show(index);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
