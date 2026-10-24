import { isQaTraffic } from './qa-traffic';

const MEASUREMENT_ID_PATTERN = /^G-[A-Z0-9]{8,14}$/

export function configureGA4() {
  if (isQaTraffic()) return false
  if (!['coshuma.com', 'www.coshuma.com'].includes(window.location.hostname)) return false
  // Match the public ID already used by /affiliate-attribution.js.
  // The hostname and QA guards above prevent local or test traffic from loading it.
  // A missing build-time variable must not silently disable analytics in production.
  const knownProductionId = 'G-J7E0J89VCV'
  const measurementId = import.meta.env.VITE_GA4_MEASUREMENT_ID || knownProductionId
  if (!MEASUREMENT_ID_PATTERN.test(measurementId || '')) return false

  window.dataLayer = window.dataLayer || []
  window.gtag = window.gtag || function gtag() {
    window.dataLayer.push(arguments)
  }

  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`
  document.head.appendChild(script)
  window.gtag('js', new Date())
  window.gtag('config', measurementId, {
    send_page_view: false,
    cookie_domain: 'coshuma.com',
  })
  return true
}
