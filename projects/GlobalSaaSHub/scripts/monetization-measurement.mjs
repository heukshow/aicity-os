import { dateInZone, shiftDate, windowEnding } from './dashboard-series.mjs';

export const EXPERIMENTS = [
  { task_key: 'GAMMA-DECISION-MEASUREMENT-20260927', page: '/compare/gamma-vs-canva.html',
    new_events: ['affiliate_cta_view', 'decision_tool_view', 'decision_tool_use', 'decision_brief_copy'] },
  { task_key: 'REV-CHATBASE-DISCLOSURE-LAYOUT-20260927', page: '/tool/chatbase.html', new_events: [] },
  { task_key: 'REV-COMPARE-MEASUREMENT-20260927', page: '/',
    new_events: ['compare_open', 'compare_tool_select', 'compare_cta_view'] },
];
const BASE_EVENTS = ['page_view', 'affiliate_click'];
const QA_REGEX = '.*[?&](coshuma_qa=1|verify=[^&]*|utm_medium=qa)(&.*)?$';

export function releaseWindows(releasedAt, now, zone, days) {
  const releaseDay = dateInZone(new Date(releasedAt), zone);
  const firstFullDay = shiftDate(releaseDay, 1);
  const end = shiftDate(firstFullDay, days - 1);
  return {
    baseline: windowEnding(shiftDate(releaseDay, -1), days),
    post: { start: firstFullDay, end },
    // Two complete reporting days of latency, excluding the partial release day.
    mature: shiftDate(dateInZone(now, zone), -3) >= end,
    available_on: shiftDate(end, 3),
  };
}

export function reportRequest(page, events, period) {
  return {
    dateRanges: [{ startDate: period.start, endDate: period.end }],
    dimensions: [{ name: 'eventName' }],
    metrics: [{ name: 'eventCount' }, { name: 'activeUsers' }],
    dimensionFilter: { andGroup: { expressions: [
      { filter: { fieldName: 'pagePath', stringFilter: { matchType: 'EXACT', value: page } } },
      { filter: { fieldName: 'eventName', inListFilter: { values: events } } },
      { notExpression: { filter: { fieldName: 'pageLocation', stringFilter: { matchType: 'FULL_REGEXP', value: QA_REGEX, caseSensitive: false } } } },
    ] } },
    limit: 50,
  };
}

function blank(events, status) {
  return Object.fromEntries(events.map(event => [event, { status, events: null, users: null }]));
}

export function normalizeReport(report, events) {
  if (!report || !Array.isArray(report.metricHeaders) || report.metricHeaders[0]?.name !== 'eventCount' ||
      report.metricHeaders[1]?.name !== 'activeUsers' || report.metadata?.subjectToThresholding ||
      report.metadata?.dataLossFromOtherRow || (report.rowCount || 0) > (report.rows?.length || 0) ||
      (report.metadata?.samplingMetadatas || []).some(x => x.samplesReadCount !== x.samplingSpaceSize)) {
    throw new Error('Incomplete monetization report');
  }
  const result = Object.fromEntries(events.map(event => [event, { status: 'current', events: 0, users: 0 }]));
  for (const row of report.rows || []) {
    const event = row.dimensionValues?.[0]?.value;
    if (!events.includes(event)) throw new Error('Unexpected event');
    const values = row.metricValues?.map(v => v.value);
    if (values?.length !== 2 || values.some(v => !/^\d+$/.test(v) || !Number.isSafeInteger(Number(v)))) {
      throw new Error('Unknown event count');
    }
    result[event] = { status: 'current', events: Number(values[0]), users: Number(values[1]) };
  }
  return result;
}

export async function collectMonetization({ registry, now, zone, query }) {
  const experiments = [];
  for (const experiment of EXPERIMENTS) {
    const release = registry.active_queue.find(row => row.task_key === experiment.task_key);
    const events = [...BASE_EVENTS, ...experiment.new_events];
    if (release?.lifecycle !== 'production_verified' || !release.completed_at || !Number.isFinite(Date.parse(release.completed_at))) {
      experiments.push({ ...experiment, status: 'awaiting_production_verification', ranges: null });
      continue;
    }
    const ranges = {};
    for (const days of [7, 30]) {
      const windows = releaseWindows(release.completed_at, now, zone, days);
      const baseline = { period: windows.baseline, metrics: blank(events, 'unavailable') };
      const post = { period: windows.post, available_on: windows.available_on, metrics: blank(events, 'not_matured') };
      // Optional collection failure is isolated to this window; never fabricate 0.
      try { baseline.metrics = { ...normalizeReport(await query(reportRequest(experiment.page, BASE_EVENTS, windows.baseline)), BASE_EVENTS),
        ...blank(experiment.new_events, 'unavailable_before_instrumentation') }; } catch { /* Retain null. */ }
      if (windows.mature) {
        post.metrics = blank(events, 'unavailable');
        try { post.metrics = normalizeReport(await query(reportRequest(experiment.page, events, windows.post)), events); } catch { /* Retain null. */ }
      }
      ranges[`${days}d`] = { baseline, post };
    }
    experiments.push({ ...experiment, status: 'measuring', production_verified_at: release.completed_at,
      ranges, network_funnel: blank(['signup', 'trial', 'paid', 'commission', 'payout'], 'unavailable'),
      caveats: ['Historical unmarked QA visits cannot be separated retrospectively.',
        'GA4 counts are event counts, not deduplicated vendor referrals or causal conversion lift.',
        'Network funnel requires independently verified matching-period vendor evidence.'] });
  }
  return { schema_version: 1, collected_at: now.toISOString(), reporting_timezone: zone,
    qa_exclusion: 'Explicit QA URL filter plus client-side session exclusion; historical unmarked visits remain ambiguous.',
    experiments };
}
