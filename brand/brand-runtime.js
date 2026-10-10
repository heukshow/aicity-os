(() => {
  const MARK = '/brand/coshuma-mark.svg';

  function makeMark(sizeClass = '') {
    const img = document.createElement('img');
    img.src = MARK;
    img.alt = 'COSHUMA';
    img.className = `coshuma-brand-mark ${sizeClass}`.trim();
    img.style.width = '40px';
    img.style.height = '32px';
    img.style.objectFit = 'contain';
    img.style.flex = '0 0 auto';
    return img;
  }

  function patchHomeBrand() {
    document.querySelectorAll('nav a[href="/"], header a[href="/"]').forEach((anchor) => {
      if (!/COSHUMA/i.test(anchor.textContent || '') || anchor.querySelector('.coshuma-brand-mark')) return;
      const first = anchor.firstElementChild;
      if (first && (first.querySelector('svg') || /^C$/i.test((first.textContent || '').trim()))) {
        first.replaceWith(makeMark());
      } else {
        anchor.prepend(makeMark());
      }
    });
  }

  function patchLegacyBadges() {
    document.querySelectorAll('a[href="/"] > div').forEach((node) => {
      if (!/^C$/i.test((node.textContent || '').trim())) return;
      if (!node.className || !String(node.className).includes('bg-purple')) return;
      node.replaceWith(makeMark());
    });
  }

  function patchToolAlternativeCards() {
    document.querySelectorAll('h2').forEach((heading) => {
      const label = heading.querySelector('span');
      if (!label || !/^Top Alternatives to\b/.test((label.textContent || '').trim())) return;

      const grid = heading.nextElementSibling;
      if (!grid) return;

      grid.querySelectorAll(':scope > a[href^="/tool/"]').forEach((card) => {
        card.classList.remove('items-center', 'justify-between');
        card.classList.add('min-w-0', 'flex-col', 'items-stretch', 'justify-start', 'gap-3');

        const identity = card.firstElementChild;
        if (identity) {
          identity.classList.add('min-w-0');
          const image = identity.querySelector('img');
          const name = identity.querySelector('span');
          if (image) image.classList.add('shrink-0');
          if (name) name.classList.add('min-w-0', 'break-words', 'leading-tight');
        }

        const pricing = Array.from(card.children).find((child) => child.tagName === 'SPAN');
        if (pricing) pricing.classList.add('w-full', 'break-words', 'leading-relaxed');
      });
    });
  }

  function patchAll() {
    patchHomeBrand();
    patchLegacyBadges();
    patchToolAlternativeCards();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', patchAll, { once: true });
  } else {
    patchAll();
  }

  let passes = 0;
  const observer = new MutationObserver(() => {
    patchAll();
    passes += 1;
    if (passes > 30) observer.disconnect();
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });
})();
