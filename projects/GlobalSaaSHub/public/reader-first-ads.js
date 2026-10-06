/* Reserve only the tallest responsive slide, keeping adjacent article content stable. */
(() => {
  'use strict';
  function init() {
    for (const unit of document.querySelectorAll('[data-house-mode="rotating"]')) {
      const track = unit.querySelector('[data-house-slides]');
      const slides = [...unit.querySelectorAll('[data-house-slide]')];
      if (!track || slides.length < 2) continue;
      let width = 0;
      function measure() {
        const available = track.getBoundingClientRect().width;
        if (!available || unit.hidden) return;
        let tallest = 0;
        for (const slide of slides) {
          const copy = slide.cloneNode(true);
          copy.hidden = false;
          copy.removeAttribute('id');
          copy.setAttribute('aria-hidden', 'true');
          for (const node of copy.querySelectorAll('[id]')) node.removeAttribute('id');
          Object.assign(copy.style, { position: 'absolute', visibility: 'hidden', pointerEvents: 'none', width: available + 'px', top: '0', left: '0' });
          track.appendChild(copy);
          tallest = Math.max(tallest, copy.getBoundingClientRect().height);
          copy.remove();
        }
        track.style.minHeight = Math.ceil(tallest) + 'px';
        width = available;
      }
      measure();
      document.fonts?.ready.then(measure);
      if (typeof ResizeObserver === 'function') {
        new ResizeObserver(() => {
          if (Math.abs(track.getBoundingClientRect().width - width) > 0.5) measure();
        }).observe(track);
      } else window.addEventListener('resize', measure, { passive: true });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
