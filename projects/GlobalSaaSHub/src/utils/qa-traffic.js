// Explicit QA sessions stay excluded across internal navigation in this tab.
export function isQaTraffic() {
  const params = new URLSearchParams(window.location.search);
  const explicit = params.get('coshuma_qa');
  let excluded = explicit === '1' || params.has('verify') || params.get('utm_medium') === 'qa';
  try {
    if (explicit === '0') sessionStorage.removeItem('coshuma_qa');
    else if (excluded) sessionStorage.setItem('coshuma_qa', '1');
    else excluded = sessionStorage.getItem('coshuma_qa') === '1';
  } catch { /* Storage denial must not break the page or explicit exclusion. */ }
  window.__coshumaQa = excluded;
  return excluded;
}
