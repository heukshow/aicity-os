export const RANGE_LENGTHS = { today: 1, '7d': 7, '30d': 30, '90d': 90 };
export function dateInZone(instant, timeZone) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone, year:'numeric', month:'2-digit', day:'2-digit' }).formatToParts(instant).map(p=>[p.type,p.value]));
  return `${parts.year}-${parts.month}-${parts.day}`;
}
export function shiftDate(date, days) {
  return new Date(Date.parse(`${date}T00:00:00Z`) + days * 86400000).toISOString().slice(0,10);
}
export function windowEnding(end, days) { return { start:shiftDate(end, 1-days), end }; }
export function dateSeries(rows, window, fields, confirmedThrough = window.end) {
  const byDate = new Map(rows.map(row=>[row.date,row]));
  const result = [];
  for(let date=window.start; date<=window.end; date=shiftDate(date,1)) {
    const found=byDate.get(date);
    result.push({date,...Object.fromEntries(fields.map(key=>[key, found ? (Number.isFinite(found[key]) ? found[key] : null) : date<=confirmedThrough ? 0 : null]))});
  }
  return result;
}
