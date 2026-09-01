(function () {
  'use strict';

  if (window.__coshumaStaticAttributionInitialized) return;
  window.__coshumaStaticAttributionInitialized = true;

  const measurementId = 'G-J7E0J89VCV';
  const params = new URLSearchParams(window.location.search);
  const campaign = {
    utm_source: params.get('utm_source') || 'direct',
    utm_medium: params.get('utm_medium') || 'none',
    utm_campaign: params.get('utm_campaign') || 'none',
    utm_content: params.get('utm_content') || 'none',
    utm_term: params.get('utm_term') || 'none'
  };

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() {
    window.dataLayer.push(arguments);
  };

  if (!document.querySelector('script[data-coshuma-ga4]')) {
    const ga4Script = document.createElement('script');
    ga4Script.async = true;
    ga4Script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
    ga4Script.dataset.coshumaGa4 = 'true';
    document.head.appendChild(ga4Script);
  }

  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    send_page_view: false,
    cookie_domain: 'coshuma.com'
  });

  function toolIdFromPath() {
    const match = window.location.pathname.match(/\/tool\/([^/.]+)\.html$/);
    return match ? match[1] : 'unknown';
  }

  window.gtag('event', 'page_view', {
    page_title: document.title,
    page_location: window.location.href,
    page_path: window.location.pathname + window.location.search,
    tool_id: toolIdFromPath(),
    ...campaign
  });

  document.addEventListener('click', function (event) {
    const link = event.target.closest('a[data-cta="affiliate"]');
    if (!link) return;

    window.gtag('event', 'affiliate_click', {
      tool_id: link.dataset.toolId || toolIdFromPath(),
      link_url: link.href,
      link_text: (link.textContent || '').trim().slice(0, 120),
      page_location: window.location.href,
      page_path: window.location.pathname + window.location.search,
      ...campaign,
      transport_type: 'beacon'
    });
  }, true);
})();
