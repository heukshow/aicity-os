const MEASUREMENT_ID_PATTERN = /^G-[A-Z0-9]{8,14}$/

export function configureGA4() {
  // A GA4 measurement ID is a public site identifier, not a credential.
  // The environment variable remains the deployment override.
  const measurementId = import.meta.env.VITE_GA4_MEASUREMENT_ID || 'G-ZSFMKB7S5C'
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
