(() => {
  const MARK = '/brand/coshuma-mark.svg';
  const BRAND = '/brand/';

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

  function addBrandAssetLinks() {
    document.querySelectorAll('footer').forEach((footer) => {
      if (footer.querySelector(`a[href="${BRAND}"]`)) return;
      const link = document.createElement('a');
      link.href = BRAND;
      link.textContent = 'Brand identity & logo downloads';
      link.style.cssText = 'display:inline-block;margin-left:12px;color:#94a3b8;text-decoration:none;font-size:12px;';
      footer.appendChild(link);
    });
  }

  function patchAll() {
    patchHomeBrand();
    patchLegacyBadges();
    addBrandAssetLinks();
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
