// Real-Time Analytics Collector Engine for GlobalSaaSHub (coshuma.com)

const STORAGE_KEY = 'coshuma_real_analytics_events_v1';

// Country mapping helper based on browser TimeZone & Locale
export function detectVisitorCountry() {
  try {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
    const lang = navigator.language || '';

    if (tz.includes('Seoul') || lang.includes('kr') || lang.includes('KO')) {
      return { country: 'South Korea', flag: '🇰🇷', code: 'KR' };
    } else if (tz.includes('America') || lang.includes('en-US')) {
      return { country: 'United States', flag: '🇺🇸', code: 'US' };
    } else if (tz.includes('London') || tz.includes('Europe/London')) {
      return { country: 'United Kingdom', flag: '🇬🇧', code: 'GB' };
    } else if (tz.includes('Berlin') || tz.includes('Europe/Berlin')) {
      return { country: 'Germany', flag: '🇩🇪', code: 'DE' };
    } else if (tz.includes('Tokyo') || lang.includes('ja')) {
      return { country: 'Japan', flag: '🇯🇵', code: 'JP' };
    } else if (tz.includes('Kolkata') || tz.includes('Asia/Calcutta')) {
      return { country: 'India', flag: '🇮🇳', code: 'IN' };
    } else if (tz.includes('Paris') || tz.includes('Europe/Paris')) {
      return { country: 'France', flag: '🇫🇷', code: 'FR' };
    } else if (tz.includes('Toronto') || tz.includes('Vancouver')) {
      return { country: 'Canada', flag: '🇨🇦', code: 'CA' };
    }
    return { country: 'United States', flag: '🇺🇸', code: 'US' };
  } catch (e) {
    return { country: 'United States', flag: '🇺🇸', code: 'US' };
  }
}

// Track a Page Visit Event
export function trackPageView(category = 'all') {
  try {
    const events = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const countryInfo = detectVisitorCountry();
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    const newEvent = {
      type: 'pageview',
      id: Date.now() + '_' + Math.random().toString(36).substr(2, 5),
      timestamp: new Date().toISOString(),
      country: countryInfo.country,
      flag: countryInfo.flag,
      code: countryInfo.code,
      referrer: document.referrer || 'Direct / Bookmark',
      category: category,
      device: isMobile ? 'Mobile' : 'Desktop'
    };

    events.push(newEvent);
    // Keep max 2000 events to manage storage
    if (events.length > 2000) events.shift();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
  } catch (e) {
    console.warn('Analytics tracking error:', e);
  }
}

// Track an Affiliate Tool Click Event
export function trackToolClick(toolId, toolName) {
  try {
    const events = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const countryInfo = detectVisitorCountry();

    const newEvent = {
      type: 'tool_click',
      id: Date.now() + '_' + Math.random().toString(36).substr(2, 5),
      timestamp: new Date().toISOString(),
      toolId: toolId,
      toolName: toolName,
      country: countryInfo.country,
      flag: countryInfo.flag,
      code: countryInfo.code
    };

    events.push(newEvent);
    if (events.length > 2000) events.shift();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
  } catch (e) {
    console.warn('Click tracking error:', e);
  }
}

// Track a Sponsorship Payment Order Event
export function trackSponsorshipOrder(toolName, amount = 49, email = '') {
  try {
    const events = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const countryInfo = detectVisitorCountry();

    const newEvent = {
      type: 'sponsorship_order',
      id: Date.now() + '_' + Math.random().toString(36).substr(2, 5),
      timestamp: new Date().toISOString(),
      toolName: toolName,
      amount: amount,
      email: email,
      country: countryInfo.country,
      flag: countryInfo.flag,
      code: countryInfo.code
    };

    events.push(newEvent);
    if (events.length > 2000) events.shift();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
  } catch (e) {
    console.warn('Sponsorship tracking error:', e);
  }
}



// Get Processed Analytics Stats for Admin Dashboard
export function getRealAnalyticsStats() {
  try {
    const events = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const pageviews = events.filter(e => e.type === 'pageview');
    const clicks = events.filter(e => e.type === 'tool_click');

    // Country Breakdown
    const countryCounts = {};
    pageviews.forEach(e => {
      const key = `${e.flag} ${e.country}`;
      countryCounts[key] = (countryCounts[key] || 0) + 1;
    });

    const totalViews = pageviews.length || 1;
    const countryBreakdown = Object.entries(countryCounts).map(([key, count]) => {
      const [flag, ...nameParts] = key.split(' ');
      const countryName = nameParts.join(' ');
      return {
        country: countryName,
        flag: flag,
        visitors: count,
        share: ((count / totalViews) * 100).toFixed(1) + '%'
      };
    }).sort((a, b) => b.visitors - a.visitors);

    // Tool Clicks Breakdown
    const toolClickCounts = {};
    clicks.forEach(e => {
      toolClickCounts[e.toolName] = (toolClickCounts[e.toolName] || 0) + 1;
    });

    const topClickedTools = Object.entries(toolClickCounts).map(([name, count]) => ({
      name,
      clicks: count
    })).sort((a, b) => b.clicks - a.clicks);

    return {
      totalPageviews: pageviews.length,
      totalClicks: clicks.length,
      ctr: pageviews.length > 0 ? ((clicks.length / pageviews.length) * 100).toFixed(1) + '%' : '0.0%',
      countryBreakdown,
      topClickedTools,
      rawEvents: events
    };
  } catch (e) {
    return { totalPageviews: 0, totalClicks: 0, ctr: '0.0%', countryBreakdown: [], topClickedTools: [], rawEvents: [] };
  }
}
