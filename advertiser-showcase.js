/* Keep advertisement previews on the advertiser page; article context is explicit. */
(() => {
  if (typeof document === 'undefined' || location.pathname !== '/advertise.html') return;
  const previews = new Map([...document.querySelectorAll('[data-position-preview]')].map(p => [p.dataset.positionPreview, p]));
  const openPreview = key => {
    const selected = previews.get(key);
    if (!selected) return;
    for (const p of previews.values()) p.open = p === selected;
  };
  for (const link of document.querySelectorAll('[data-ad-position],[data-preview-open]')) {
    const key = link.dataset.adPosition || link.dataset.previewOpen;
    if (previews.has(key)) link.addEventListener('click', () => openPreview(key));
  }
  function followHash() {
    const prefix = '#ad-preview-';
    if (location.hash.startsWith(prefix)) openPreview(location.hash.slice(prefix.length));
  }
  window.addEventListener('hashchange', followHash);
  for (const panel of previews.values()) {
    const slides = [...panel.querySelectorAll('[data-preview-slide]')];
    const controls = panel.querySelector('[data-preview-controls]');
    if (!controls || slides.length < 2) continue;
    let index = 0;
    const show = i => {
      index = (i + slides.length) % slides.length;
      slides.forEach((s, n) => { s.hidden = n !== index; });
      panel.querySelector('[data-preview-count]').textContent = `${index + 1} / ${slides.length}`;
    };
    panel.querySelector('[data-preview-prev]').addEventListener('click', () => show(index - 1));
    panel.querySelector('[data-preview-next]').addEventListener('click', () => show(index + 1));
    controls.hidden = false;
    show(0);
  }
  followHash();
})();

/* Historical context tabs and QA links are navigation only. */
(() => {
 const params = new URLSearchParams(location.search);
 const qa = params.get('coshuma_qa') === '1';
 const panels=[...document.querySelectorAll('[data-example-panel]')], tabs=[...document.querySelectorAll('[data-example]')];
 const show = key => {for(const p of panels)p.hidden=p.dataset.examplePanel!==key;for(const t of tabs)t.setAttribute('aria-pressed',String(t.dataset.example===key));};
 for(const t of tabs)t.addEventListener('click',()=>show(t.dataset.example));show('tool-primary');
 if(qa)for(const a of document.querySelectorAll('[data-live-example],[data-reader-nav]')){const u=new URL(a.getAttribute('href'),location.origin);if(u.origin===location.origin){u.searchParams.set('coshuma_qa','1');a.href=u.pathname+u.search+u.hash;}}
})();
