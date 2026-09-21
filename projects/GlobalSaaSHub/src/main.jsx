import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { configureGA4 } from './utils/ga4.js'

configureGA4()

if (['coshuma.com', 'www.coshuma.com'].includes(window.location.hostname) && !document.querySelector('script[data-coshuma-revisit-growth]')) {
  const revisitMeasurement = document.createElement('script')
  revisitMeasurement.src = '/revisit-growth-measurement.js'
  revisitMeasurement.defer = true
  revisitMeasurement.dataset.coshumaRevisitGrowth = '1'
  document.head.appendChild(revisitMeasurement)
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
