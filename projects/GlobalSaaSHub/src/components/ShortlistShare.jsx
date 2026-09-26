import React, { useEffect, useMemo, useState } from 'react'
import { Check, Link2 } from 'lucide-react'
import allToolsData from '../generated/public-tools.json'

const publicToolIds = new Set(
  allToolsData
    .filter((tool) => !['convertkit', 'merlin-ai'].includes(tool.id))
    .map((tool) => tool.id),
)

const normalizeToolIds = (value) => [
  ...new Set(
    String(value || '')
      .split(',')
      .map((id) => id.trim())
      .filter((id) => publicToolIds.has(id)),
  ),
].slice(0, 20)

const readSavedIds = () => {
  try {
    const parsed = JSON.parse(localStorage.getItem('coshuma_bookmarks') || '[]')
    if (!Array.isArray(parsed)) return []
    return [...new Set(parsed.filter((id) => publicToolIds.has(id)))].slice(0, 20)
  } catch {
    return []
  }
}

export function applySharedShortlistFromUrl() {
  if (typeof window === 'undefined') return

  const sharedIds = normalizeToolIds(new URLSearchParams(window.location.search).get('shortlist'))
  if (!sharedIds.length) return

  const mergedIds = [...new Set([...readSavedIds(), ...sharedIds])].slice(0, 20)
  localStorage.setItem('coshuma_bookmarks', JSON.stringify(mergedIds))
}

const fallbackCopy = (text) => {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.setAttribute('readonly', '')
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  const copied = document.execCommand('copy')
  textarea.remove()
  return copied
}

const measureShortlistShare = (savedCount) => {
  if (window.__coshumaQa || typeof window.gtag !== 'function') return
  try { window.gtag('event', 'saved_shortlist_share', {
    page_path: window.location.pathname,
    page_location: window.location.href,
    measurement_area: 'revisit_growth',
    saved_count: savedCount,
    share_method: 'copy_link',
  }) } catch { /* A successful copy remains successful if analytics is blocked. */ }
}

export default function ShortlistShare() {
  const [savedIds, setSavedIds] = useState(readSavedIds)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const syncSavedIds = () => {
      window.setTimeout(() => setSavedIds(readSavedIds()), 0)
    }

    document.addEventListener('click', syncSavedIds)
    window.addEventListener('storage', syncSavedIds)
    return () => {
      document.removeEventListener('click', syncSavedIds)
      window.removeEventListener('storage', syncSavedIds)
    }
  }, [])

  const shareUrl = useMemo(() => {
    if (!savedIds.length || typeof window === 'undefined') return ''
    const url = new URL('/', window.location.origin)
    url.searchParams.set('shortlist', savedIds.join(','))
    url.hash = 'directory'
    return url.toString()
  }, [savedIds])

  const copyShortlistLink = async () => {
    if (!shareUrl) return

    let didCopy = false
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareUrl)
        didCopy = true
      } else {
        didCopy = fallbackCopy(shareUrl)
      }
    } catch {
      didCopy = fallbackCopy(shareUrl)
    }

    if (!didCopy) return
    measureShortlistShare(savedIds.length)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1800)
  }

  if (!savedIds.length) return null

  return (
    <div className="fixed bottom-4 right-4 z-[60] max-w-[calc(100vw-2rem)]">
      <button
        type="button"
        onClick={copyShortlistLink}
        aria-label={`Share ${savedIds.length} saved tools`}
        aria-live="polite"
        className="inline-flex items-center gap-2 rounded-xl border border-violet-400/30 bg-[#11131a]/95 px-4 py-3 text-xs font-bold text-violet-100 shadow-2xl shadow-black/40 backdrop-blur hover:border-violet-300/50 hover:bg-[#181a29] focus:outline-none focus:ring-2 focus:ring-violet-400/60"
      >
        {copied ? <Check className="h-4 w-4" /> : <Link2 className="h-4 w-4" />}
        {copied ? 'Shortlist link copied' : `Share saved (${savedIds.length})`}
      </button>
    </div>
  )
}
