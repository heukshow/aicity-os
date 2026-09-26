(() => {
  const BOOKMARKS_KEY = 'coshuma_bookmarks';
  const LAST_VISIT_KEY = 'coshuma_last_visit_at_v1';
  const SESSION_MARK = 'coshuma_revisit_measurement_session_v1';
  const SESSION_GAP_MS = 30 * 60 * 1000;

  const readBookmarks = () => {
    try {
      const parsed = JSON.parse(localStorage.getItem(BOOKMARKS_KEY) || '[]');
      return Array.isArray(parsed) ? parsed.filter((id) => typeof id === 'string') : [];
    } catch {
      return [];
    }
  };

  const send = (eventName, params = {}) => {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', eventName, {
      page_path: window.location.pathname,
      page_location: window.location.href,
      measurement_area: 'revisit_growth',
      ...params,
    });
  };

  const measureReturnVisit = () => {
    try {
      if (sessionStorage.getItem(SESSION_MARK)) return;
      sessionStorage.setItem(SESSION_MARK, '1');

      const now = Date.now();
      const lastVisit = Number(localStorage.getItem(LAST_VISIT_KEY));
      const savedCount = readBookmarks().length;

      if (Number.isFinite(lastVisit) && lastVisit > 0 && now - lastVisit >= SESSION_GAP_MS) {
        send('return_visit', {
          hours_since_last_visit: Math.round(((now - lastVisit) / 3600000) * 10) / 10,
          saved_count: savedCount,
          has_saved_tools: savedCount > 0,
        });
      }

      localStorage.setItem(LAST_VISIT_KEY, String(now));
    } catch {
      // Measurement must never block the buyer experience when storage is unavailable.
    }
  };

  const toolIdFromSaveButton = (button) => {
    const article = button.closest('article');
    const buyerGuide = article?.querySelector('a[href^="/tool/"]');
    const href = buyerGuide?.getAttribute('href') || '';
    const match = href.match(/^\/tool\/([^/?#]+)\.html/);
    return match ? match[1] : null;
  };

  const classifyIntentClick = (target) => {
    const affiliate = target.closest('a[data-cta="affiliate"]');
    if (affiliate) {
      send('buyer_intent_stage', {
        stage: 'affiliate_click',
        tool_id: affiliate.getAttribute('data-tool-id') || null,
        source: affiliate.getAttribute('data-cta-source') || 'unknown',
      });
      return true;
    }

    const buyerGuide = target.closest('a[href^="/tool/"]');
    if (buyerGuide) {
      const href = buyerGuide.getAttribute('href') || '';
      const match = href.match(/^\/tool\/([^/?#]+)\.html/);
      send('buyer_intent_stage', {
        stage: 'product_view_intent',
        tool_id: match ? match[1] : null,
      });
      return true;
    }

    const compareButton = target.closest('button[title="Compare side-by-side"]');
    if (compareButton) {
      send('buyer_intent_stage', { stage: 'compare_intent' });
      return true;
    }

    return false;
  };

  document.addEventListener('click', (event) => {
    const target = event.target instanceof Element ? event.target : null;
    if (!target) return;

    classifyIntentClick(target);

    const saveButton = target.closest('button[title="Save tool"]');
    if (saveButton) {
      const toolId = toolIdFromSaveButton(saveButton);
      if (!toolId) return;
      setTimeout(() => {
        const saved = readBookmarks();
        send('saved_tool_change', {
          tool_id: toolId,
          action: saved.includes(toolId) ? 'save' : 'remove',
          saved_count: saved.length,
        });
      }, 0);
      return;
    }

    const button = target.closest('button');
    if (button && /^Saved \(\d+\)/.test((button.textContent || '').trim())) {
      send('saved_tools_view', { saved_count: readBookmarks().length });
    }
  });

  window.addEventListener('load', () => {
    setTimeout(measureReturnVisit, 500);
  }, { once: true });
})();
