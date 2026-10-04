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

  function enhanceToolDecisionDock() {
    if (!/\/tool\/[^/.]+\.html$/.test(window.location.pathname)) return;
    if (!document.body || document.querySelector('[data-coshuma-decision-dock="1"]')) return;

    const pageToolId = toolIdFromPath();
    if (!pageToolId || pageToolId === 'unknown') return;

    const affiliateLinks = Array.from(document.querySelectorAll('a[data-cta="affiliate"]')).filter(function (link) {
      return typeof link.href === 'string'
        && /^https?:\/\//i.test(link.href)
        && link.dataset.toolId === pageToolId;
    });
    if (!affiliateLinks.length) return;

    const primary = affiliateLinks[0];
    const toolId = pageToolId;

    const dock = document.createElement('aside');
    dock.dataset.coshumaDecisionDock = '1';
    dock.dataset.visible = 'false';
    dock.setAttribute('aria-label', 'Save this tool or continue to the current vendor destination');

    const style = document.createElement('style');
    style.dataset.coshumaDecisionDockStyle = '1';
    style.textContent = [
      '[data-coshuma-decision-dock="1"]{position:fixed;right:18px;bottom:18px;z-index:65;width:min(380px,calc(100vw - 36px));padding:14px;border:1px solid rgba(139,92,246,.35);border-radius:18px;background:rgba(12,14,22,.96);box-shadow:0 20px 55px rgba(0,0,0,.45);backdrop-filter:blur(16px);transform:translateY(130%);opacity:0;pointer-events:none;transition:transform .22s ease,opacity .22s ease;font-family:Inter,system-ui,sans-serif}',
      '[data-coshuma-decision-dock="1"][data-visible="true"]{transform:translateY(0);opacity:1;pointer-events:auto}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:10px}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-kicker{font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#c4b5fd}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-copy{margin-top:3px;font-size:12px;line-height:1.45;color:#aeb7ca}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-close{min-width:44px;min-height:44px;border:1px solid rgba(255,255,255,.12);border-radius:10px;background:rgba(255,255,255,.05);color:#cbd5e1;font-size:20px;line-height:1;cursor:pointer}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-actions{display:grid;grid-template-columns:minmax(0,.72fr) minmax(0,1.28fr);gap:8px}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-save,[data-coshuma-decision-dock="1"] .coshuma-dock-cta{min-height:44px;border-radius:12px;padding:10px 12px;font-size:12px;font-weight:800;text-align:center;display:flex;align-items:center;justify-content:center;text-decoration:none}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-save{border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.06);color:#e2e8f0;cursor:pointer}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-save:disabled{cursor:default;color:#bbf7d0;border-color:rgba(74,222,128,.25);background:rgba(34,197,94,.08)}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-cta{background:#7c3aed;color:#fff}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-saved{display:none;margin-top:9px;font-size:11px;font-weight:700;color:#a7f3d0;text-decoration:none}',
      '[data-coshuma-decision-dock="1"] .coshuma-dock-saved[data-visible="true"]{display:inline-flex}',
      '@media(max-width:899px){[data-coshuma-decision-dock="1"]{left:10px;right:10px;bottom:max(10px,env(safe-area-inset-bottom));width:auto;border-radius:16px;padding:12px}[data-coshuma-decision-dock="1"] .coshuma-dock-copy{font-size:11px}body[data-coshuma-conversion-dock-visible="true"]{padding-bottom:92px}}',
      '@media(prefers-reduced-motion:reduce){[data-coshuma-decision-dock="1"]{transition:none}}'
    ].join('');
    document.head.appendChild(style);

    const top = document.createElement('div');
    top.className = 'coshuma-dock-top';

    const message = document.createElement('div');
    const kicker = document.createElement('div');
    kicker.className = 'coshuma-dock-kicker';
    kicker.textContent = 'Keep your decision moving';
    const copy = document.createElement('div');
    copy.className = 'coshuma-dock-copy';
    copy.textContent = 'Save this tool for later or continue to the same vendor destination already shown on this page.';
    message.appendChild(kicker);
    message.appendChild(copy);

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'coshuma-dock-close';
    close.setAttribute('aria-label', 'Close decision actions');
    close.textContent = '×';

    top.appendChild(message);
    top.appendChild(close);

    const actions = document.createElement('div');
    actions.className = 'coshuma-dock-actions';

    const save = document.createElement('button');
    save.type = 'button';
    save.className = 'coshuma-dock-save';
    save.textContent = 'Save for later';

    const cta = document.createElement('a');
    cta.className = 'coshuma-dock-cta';
    cta.href = primary.href;
    cta.target = primary.target || '_blank';
    cta.rel = primary.rel || 'sponsored noopener noreferrer';
    cta.dataset.cta = 'affiliate';
    cta.dataset.toolId = toolId;
    cta.dataset.ctaSource = 'tool-decision-dock';
    const primaryLabel = String(primary.textContent || '').trim().replace(/\\s+/g, ' ');
    cta.textContent = primaryLabel && primaryLabel.length <= 70 ? primaryLabel : 'Continue to vendor →';

    actions.appendChild(save);
    actions.appendChild(cta);

    const savedLink = document.createElement('a');
    savedLink.className = 'coshuma-dock-saved';
    savedLink.href = '/?saved=1#directory';
    savedLink.textContent = 'View saved tools →';

    dock.appendChild(top);
    dock.appendChild(actions);
    dock.appendChild(savedLink);
    document.body.appendChild(dock);
    document.body.dataset.coshumaConversionDock = '1';
    document.body.dataset.coshumaConversionDockVisible = 'false';

    const bookmarksKey = 'coshuma_bookmarks';
    function readBookmarks() {
      try {
        const parsed = JSON.parse(window.localStorage.getItem(bookmarksKey) || '[]');
        return Array.isArray(parsed) ? parsed.filter(function (id) { return typeof id === 'string'; }) : [];
      } catch (error) {
        return [];
      }
    }
    function syncSavedState() {
      const saved = readBookmarks().includes(toolId);
      save.disabled = saved;
      save.textContent = saved ? 'Saved ✓' : 'Save for later';
      savedLink.dataset.visible = saved ? 'true' : 'false';
    }
    syncSavedState();

    save.addEventListener('click', function () {
      const current = readBookmarks();
      if (!current.includes(toolId)) {
        try {
          window.localStorage.setItem(bookmarksKey, JSON.stringify(current.concat(toolId)));
        } catch (error) {
          return;
        }
      }
      syncSavedState();
      if (!window.__coshumaQa && typeof window.gtag === 'function') {
        window.gtag('event', 'tool_save', {
          tool_id: toolId,
          save_source: 'tool-decision-dock',
          page_location: window.location.href,
          page_path: window.location.pathname + window.location.search,
          page_type: pageTypeFromPath(),
          content_slug: contentSlugFromPath()
        });
      }
    });

    const closedKey = 'coshuma_conversion_dock_closed_v1:' + toolId;
    function isClosed() {
      try {
        return window.sessionStorage.getItem(closedKey) === '1';
      } catch (error) {
        return false;
      }
    }
    close.addEventListener('click', function () {
      dock.dataset.visible = 'false';
      document.body.dataset.coshumaConversionDockVisible = 'false';
      try {
        window.sessionStorage.setItem(closedKey, '1');
      } catch (error) {
        // Closing the dock should still work when storage is unavailable.
      }
    });

    function syncVisibility() {
      if (isClosed()) {
        dock.dataset.visible = 'false';
        document.body.dataset.coshumaConversionDockVisible = 'false';
        return;
      }
      const y = Number(window.scrollY || window.pageYOffset || 0);
      const threshold = Number(window.innerWidth || 1024) < 900 ? 520 : 720;
      const rect = typeof primary.getBoundingClientRect === 'function' ? primary.getBoundingClientRect() : null;
      const passedPrimary = rect ? rect.bottom < 0 : y >= threshold;
      const visible = y >= threshold && passedPrimary;
      dock.dataset.visible = visible ? 'true' : 'false';
      document.body.dataset.coshumaConversionDockVisible = visible ? 'true' : 'false';
    }
    window.addEventListener('scroll', syncVisibility, { passive: true });
    window.addEventListener('resize', syncVisibility);
    syncVisibility();
  }

  function enhanceVerifiedPartnerOffers() {
    if (/\/tool\/unbounce\.html$/.test(window.location.pathname)) {
      if (!document.querySelector('[data-partner-offer="unbounce-conversion-fit"]')) {
        const verifiedUrl = 'https://unbounce.partnerlinks.io/5ubjnt8lluqi';
        const primaryCta = document.querySelector('a[data-cta="affiliate"][data-tool-id="unbounce"]');
        const sections = Array.from(document.querySelectorAll('main > section'));
        const attributionSection = sections.find(function (section) {
          const heading = section.querySelector('h2');
          return heading && /current offer before starting your trial/i.test(heading.textContent || '');
        });

        if (primaryCta && primaryCta.href.startsWith(verifiedUrl) && attributionSection) {
          const guide = document.createElement('section');
          guide.dataset.partnerOffer = 'unbounce-conversion-fit';
          guide.className = 'rounded-3xl border border-cyan-500/20 bg-cyan-500/5 p-6 md:p-8 space-y-5';
          guide.innerHTML = [
            '<div>',
            '<div class="text-xs uppercase tracking-widest text-cyan-300 font-bold">Before you pay</div>',
            '<h2 class="text-3xl font-black text-white mt-1">Test what happens after the form submit</h2>',
            '<p class="text-sm text-slate-300 leading-relaxed mt-2">Integrations are a practical buying test: confirm that captured leads can reach the CRM, email or automation stack you already use before choosing a paid plan.</p>',
            '</div>',
            '<div class="grid md:grid-cols-3 gap-3">',
            '<div class="rounded-2xl border border-[#2a2e42] bg-[#0d1018] p-5"><div class="text-xs uppercase tracking-wider text-cyan-300 font-bold">Direct handoff</div><div class="mt-2 text-sm text-slate-300 leading-relaxed">Unbounce lists native connections including Mailchimp, Marketo and Salesforce; its current Build plan also advertises 1000+ integrations.</div></div>',
            '<div class="rounded-2xl border border-[#2a2e42] bg-[#0d1018] p-5"><div class="text-xs uppercase tracking-wider text-cyan-300 font-bold">Automation bridge</div><div class="mt-2 text-sm text-slate-300 leading-relaxed">If your app is not a direct integration, Unbounce supports Zapier and Webhooks for moving captured lead data into other systems.</div></div>',
            '<div class="rounded-2xl border border-[#2a2e42] bg-[#0d1018] p-5"><div class="text-xs uppercase tracking-wider text-cyan-300 font-bold">Optimization fit</div><div class="mt-2 text-sm text-slate-300 leading-relaxed">Smart Traffic routes visitors toward the page variant it predicts is more likely to convert. Unbounce currently positions Smart Traffic on Optimize and higher.</div></div>',
            '</div>',
            '<p class="text-xs text-slate-500 leading-relaxed">These are product-fit checks, not promised results. Test the workflow with your own traffic and integrations before choosing a paid plan.</p>',
            '<div class="flex flex-col sm:flex-row gap-3">',
            '<a data-cta="affiliate" data-tool-id="unbounce" data-cta-source="unbounce-integration-fit" href="' + verifiedUrl + '" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-center">Try Unbounce →</a>',
            '<a href="https://unbounce.com/product/integrations/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl border border-cyan-500/30 bg-cyan-500/5 text-cyan-100 font-bold text-center hover:bg-cyan-500/10">Check Unbounce integrations →</a>',
            '</div>'
          ].join('');
          attributionSection.insertAdjacentElement('beforebegin', guide);
        }
      }
    }
  }

  // Match the React entry point: QA excludes this tab across navigation.
  const explicitQa = params.get('coshuma_qa');
  let qa = explicitQa === '1' || params.has('verify') || params.get('utm_medium') === 'qa';
  try {
    if (explicitQa === '0') window.sessionStorage.removeItem('coshuma_qa');
    else if (qa) window.sessionStorage.setItem('coshuma_qa', '1');
    else qa = window.sessionStorage.getItem('coshuma_qa') === '1';
  } catch { /* Explicit exclusion still works with storage disabled. */ }
  window.__coshumaQa = qa;
  enhanceVerifiedPartnerOffers();
  enhanceToolDecisionDock();
  if (qa) return;

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

  const interactiveExperiences = Array.from(document.querySelectorAll('[data-interactive-experience]'));
  if (interactiveExperiences.length && typeof window.IntersectionObserver === 'function') {
    const observer = new window.IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting || entry.intersectionRatio < 0.35) return;
        const node = entry.target;
        if (node.dataset.coshumaExperienceSeen === '1') return;
        node.dataset.coshumaExperienceSeen = '1';
        window.gtag('event', 'interactive_demo_view', {
          tool_id: toolIdFromPath(),
          experience_type: node.dataset.interactiveExperience || 'unknown',
          page_location: window.location.href,
          page_path: window.location.pathname + window.location.search,
          page_type: pageTypeFromPath(),
          content_slug: contentSlugFromPath(),
          entry_page: attribution.entry_page,
          entry_referrer: attribution.entry_referrer,
          ...campaign
        });
        observer.unobserve(node);
      });
    }, { threshold: [0.35] });
    interactiveExperiences.forEach(function (node) { observer.observe(node); });
  }

  document.addEventListener('click', function (event) {
    const experienceLink = event.target.closest('a[data-interactive-experience-cta]');
    if (experienceLink) {
      window.gtag('event', 'interactive_demo_cta_click', {
        tool_id: experienceLink.dataset.toolId || toolIdFromPath(),
        experience_action: experienceLink.dataset.interactiveExperienceCta || 'official-exit',
        cta_source: experienceLink.dataset.ctaSource || 'interactive-demo',
        link_url: experienceLink.href,
        outbound_domain: hostnameFromUrl(experienceLink.href),
        link_text: (experienceLink.textContent || '').trim().slice(0, 120),
        page_location: window.location.href,
        page_path: window.location.pathname + window.location.search,
        page_type: pageTypeFromPath(),
        content_slug: contentSlugFromPath(),
        entry_page: attribution.entry_page,
        entry_referrer: attribution.entry_referrer,
        ...campaign,
        transport_type: 'beacon'
      });
    }

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
