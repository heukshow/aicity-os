(function () {
  'use strict';

  if (window.__coshumaStaticAttributionInitialized) return;
  window.__coshumaStaticAttributionInitialized = true;

  const measurementId = 'G-J7E0J89VCV';
  const sessionKey = 'coshuma_affiliate_campaign_v1';
  const params = new URLSearchParams(window.location.search);
  const campaignKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];

  function campaignFromUrl() {
    const values = {};
    let hasCampaignParam = false;

    campaignKeys.forEach(function (key) {
      const value = params.get(key);
      if (value) hasCampaignParam = true;
      values[key] = value || null;
    });

    return { values: values, hasCampaignParam: hasCampaignParam };
  }

  function directCampaign() {
    return {
      utm_source: 'direct',
      utm_medium: 'none',
      utm_campaign: 'none',
      utm_content: 'none',
      utm_term: 'none'
    };
  }

  function normalizeCampaign(values) {
    const normalized = {};
    campaignKeys.forEach(function (key) {
      normalized[key] = values && values[key] ? values[key] : (key === 'utm_source' ? 'direct' : 'none');
    });
    return normalized;
  }

  function sessionAttribution() {
    const current = campaignFromUrl();
    const currentEntry = {
      campaign: normalizeCampaign(current.values),
      entry_page: window.location.pathname + window.location.search,
      entry_referrer: document.referrer || 'direct'
    };

    try {
      if (current.hasCampaignParam) {
        window.sessionStorage.setItem(sessionKey, JSON.stringify(currentEntry));
        return currentEntry;
      }

      const stored = window.sessionStorage.getItem(sessionKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && parsed.campaign) {
          return {
            campaign: normalizeCampaign(parsed.campaign),
            entry_page: parsed.entry_page || currentEntry.entry_page,
            entry_referrer: parsed.entry_referrer || currentEntry.entry_referrer
          };
        }
      }

      window.sessionStorage.setItem(sessionKey, JSON.stringify(currentEntry));
    } catch (error) {
      // Analytics must never block navigation when storage is unavailable.
    }

    return currentEntry;
  }

  function toolIdFromPath() {
    const match = window.location.pathname.match(/\/tool\/([^/.]+)\.html$/);
    return match ? match[1] : 'unknown';
  }

  function pageTypeFromPath() {
    const path = window.location.pathname;
    if (/\/tool\/[^/.]+\.html$/.test(path)) return 'tool';
    if (/\/compare\/[^/.]+\.html$/.test(path)) return 'compare';
    if (path === '/' || path === '/index.html') return 'home';
    return 'other';
  }

  function hostnameFromUrl(url) {
    try {
      return new URL(url, window.location.href).hostname || 'unknown';
    } catch (error) {
      return 'unknown';
    }
  }

  const attribution = sessionAttribution();
  const campaign = attribution.campaign || directCampaign();

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

  window.gtag('event', 'page_view', {
    page_title: document.title,
    page_location: window.location.href,
    page_path: window.location.pathname + window.location.search,
    page_type: pageTypeFromPath(),
    tool_id: toolIdFromPath(),
    entry_page: attribution.entry_page,
    entry_referrer: attribution.entry_referrer,
    ...campaign
  });

  document.addEventListener('click', function (event) {
    const link = event.target.closest('a[data-cta="affiliate"]');
    if (!link) return;

    window.gtag('event', 'affiliate_click', {
      tool_id: link.dataset.toolId || toolIdFromPath(),
      cta_source: link.dataset.ctaSource || 'unspecified',
      link_url: link.href,
      outbound_domain: hostnameFromUrl(link.href),
      link_text: (link.textContent || '').trim().slice(0, 120),
      page_location: window.location.href,
      page_path: window.location.pathname + window.location.search,
      page_type: pageTypeFromPath(),
      entry_page: attribution.entry_page,
      entry_referrer: attribution.entry_referrer,
      ...campaign,
      transport_type: 'beacon'
    });
  }, true);
})();
