(function () {
  'use strict';

  if (!['coshuma.com', 'www.coshuma.com'].includes(window.location.hostname)) return;

  if (window.__coshumaStaticAttributionInitialized) return;
  window.__coshumaStaticAttributionInitialized = true;

  const measurementId = 'G-J7E0J89VCV';
  const sessionKey = 'coshuma_affiliate_campaign_v2';
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
    return {};
  }

  function normalizeCampaign(values) {
    const normalized = {};
    campaignKeys.forEach(function (key) {
      if (values && values[key]) normalized[key] = values[key];
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
    if (/\/best\/[^/.]+\.html$/.test(path)) return 'best';
    if (path === '/' || path === '/index.html') return 'home';
    if (/^\/[^/.]+\.html$/.test(path)) return 'guide';
    return 'other';
  }

  function contentSlugFromPath() {
    const match = window.location.pathname.match(/\/(?:tool|compare|best)\/([^/.]+)\.html$/);
    if (match) return match[1];
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') return 'home';
    const rootGuide = window.location.pathname.match(/^\/([^/.]+)\.html$/);
    return rootGuide ? rootGuide[1] : 'unknown';
  }

  function hostnameFromUrl(url) {
    try {
      return new URL(url, window.location.href).hostname || 'unknown';
    } catch (error) {
      return 'unknown';
    }
  }

  function enhanceVerifiedPartnerOffers() {
    if (/\/tool\/make-com\.html$/.test(window.location.pathname)) {
      if (!document.querySelector('[data-partner-offer="make-pro-welcome"]')) {
        const primaryCta = document.querySelector('a[data-cta="affiliate"][data-tool-id="make-com"]');
        if (primaryCta && primaryCta.href.includes('pc=coshuma')) {
          const offer = document.createElement('div');
          offer.dataset.partnerOffer = 'make-pro-welcome';
          offer.className = 'mt-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-xs leading-relaxed text-emerald-100';
          offer.innerHTML = '<strong>Partner welcome offer:</strong> Make says new users who sign up through this verified partner link automatically receive their first month of Pro (10,000 operations) free. Confirm the offer is shown during signup before relying on it.';
          primaryCta.insertAdjacentElement('afterend', offer);
        }
      }
    }

    if (/\/tool\/unbounce\.html$/.test(window.location.pathname)) {
      if (!document.querySelector('[data-partner-offer="unbounce-conversion-fit"]')) {
        const verifiedUrl = 'https://unbounce.partnerlinks.io/5ubjnt8lluqi';
        const primaryCta = document.querySelector('a[data-cta="affiliate"][data-tool-id="unbounce"]');
        const sections = Array.from(document.querySelectorAll('main > section'));
        const attributionSection = sections.find(function (section) {
          const heading = section.querySelector('h2');
          return heading && /verified link before starting your trial/i.test(heading.textContent || '');
        });

        if (primaryCta && primaryCta.href.startsWith(verifiedUrl) && attributionSection) {
          const guide = document.createElement('section');
          guide.dataset.partnerOffer = 'unbounce-conversion-fit';
          guide.className = 'rounded-3xl border border-cyan-500/20 bg-cyan-500/5 p-6 md:p-8 space-y-5';
          guide.innerHTML = [
            '<div>',
            '<div class="text-xs uppercase tracking-widest text-cyan-300 font-bold">Before you pay</div>',
            '<h2 class="text-3xl font-black text-white mt-1">Test what happens after the form submit</h2>',
            '<p class="text-sm text-slate-300 leading-relaxed mt-2">A fresh Unbounce Affiliate Team message to COSHUMA emphasized lead handoff as a retention use case. That makes integrations a practical buying test: confirm that captured leads can reach the CRM, email or automation stack you already use before choosing a paid plan.</p>',
            '</div>',
            '<div class="grid md:grid-cols-3 gap-3">',
            '<div class="rounded-2xl border border-[#2a2e42] bg-[#0d1018] p-5"><div class="text-xs uppercase tracking-wider text-cyan-300 font-bold">Direct handoff</div><div class="mt-2 text-sm text-slate-300 leading-relaxed">Unbounce lists native connections including Mailchimp, Marketo and Salesforce; its current Build plan also advertises 1000+ integrations.</div></div>',
            '<div class="rounded-2xl border border-[#2a2e42] bg-[#0d1018] p-5"><div class="text-xs uppercase tracking-wider text-cyan-300 font-bold">Automation bridge</div><div class="mt-2 text-sm text-slate-300 leading-relaxed">If your app is not a direct integration, Unbounce supports Zapier and Webhooks for moving captured lead data into other systems.</div></div>',
            '<div class="rounded-2xl border border-[#2a2e42] bg-[#0d1018] p-5"><div class="text-xs uppercase tracking-wider text-cyan-300 font-bold">Optimization fit</div><div class="mt-2 text-sm text-slate-300 leading-relaxed">Smart Traffic routes visitors toward the page variant it predicts is more likely to convert. Unbounce currently positions Smart Traffic on Optimize and higher.</div></div>',
            '</div>',
            '<p class="text-xs text-slate-500 leading-relaxed">These are product-fit checks, not promised results. COSHUMA does not claim a conversion lift, signup or commission unless first-party reporting verifies it.</p>',
            '<div class="flex flex-col sm:flex-row gap-3">',
            '<a data-cta="affiliate" data-tool-id="unbounce" data-cta-source="unbounce-integration-fit" href="' + verifiedUrl + '" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-center">Test Unbounce through the verified partner route →</a>',
            '<a href="https://unbounce.com/product/integrations/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl border border-cyan-500/30 bg-cyan-500/5 text-cyan-100 font-bold text-center hover:bg-cyan-500/10">Check Unbounce integrations →</a>',
            '</div>'
          ].join('');
          attributionSection.insertAdjacentElement('beforebegin', guide);
        }
      }
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
    page_referrer: document.referrer,
    page_path: window.location.pathname + window.location.search,
    page_type: pageTypeFromPath(),
    content_slug: contentSlugFromPath(),
    tool_id: toolIdFromPath(),
    entry_page: attribution.entry_page,
    entry_referrer: attribution.entry_referrer,
    ...campaign
  });

  enhanceVerifiedPartnerOffers();

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
      content_slug: contentSlugFromPath(),
      entry_page: attribution.entry_page,
      entry_referrer: attribution.entry_referrer,
      ...campaign,
      transport_type: 'beacon'
    });
  }, true);
})();
