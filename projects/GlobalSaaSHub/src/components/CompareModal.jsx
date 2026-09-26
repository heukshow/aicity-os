import React, { useEffect, useRef, useState } from 'react';
import { X, ExternalLink, Zap } from 'lucide-react';
import { getValidExternalUrl } from '../utils/url';

export default function CompareModal({ toolA, toolB, allTools, onClose }) {
  const dialogRef = useRef(null);
  const closeButtonRef = useRef(null);

  // Safe initial toolB selection if not provided by App.jsx
  const sameCategoryTools = allTools ? allTools.filter(
    t => t.id !== toolA?.id && (t.category === toolA?.category || t.category_display === toolA?.category_display)
  ) : [];

  const initialB = toolB || sameCategoryTools[0] || (allTools ? allTools.find(t => t.id !== toolA?.id) : null);

  const [selectedToolB, setSelectedToolB] = useState(initialB);
  const [selectedToolC, setSelectedToolC] = useState(null);

  useEffect(() => {
    const previouslyFocused = document.activeElement;
    const previousOverflow = document.body.style.overflow;

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key !== 'Tab' || !dialogRef.current) return;

      const focusable = Array.from(dialogRef.current.querySelectorAll(
        'a[href], button:not([disabled]), select:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
      ));
      if (!focusable.length) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && (document.activeElement === first || !dialogRef.current.contains(document.activeElement))) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', handleKeyDown);
    closeButtonRef.current?.focus();

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = previousOverflow;
      previouslyFocused?.focus?.();
    };
  }, [onClose]);

  if (!toolA || !selectedToolB) {
    return null;
  }

  const availableTools = allTools ? allTools.filter(
    t => t.id !== toolA.id && t.id !== selectedToolB.id && (!selectedToolC || t.id !== selectedToolC.id)
  ) : [];

  const urlA = getValidExternalUrl(toolA);
  const urlB = getValidExternalUrl(selectedToolB);
  const urlC = getValidExternalUrl(selectedToolC);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="compare-dialog-title"
        className="relative w-full max-w-5xl bg-[#0f111a] border border-[#222538] rounded-3xl p-4 sm:p-6 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto"
      >
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#222538] pb-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">⚔️</span>
            <div><h2 id="compare-dialog-title" className="text-lg font-black text-white">Side-by-Side Tool Comparison</h2><p className="mt-0.5 text-[11px] font-semibold text-slate-500">Compare up to 3 tools</p></div>
          </div>
          <button 
            ref={closeButtonRef}
            type="button"
            onClick={onClose}
            aria-label="Close comparison dialog"
            className="p-2 rounded-xl bg-[#181a29] text-slate-400 hover:text-white hover:bg-[#222538] transition-all"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Comparison Grid */}
        <p className="text-xs leading-5 text-slate-500">Compare up to three tools using the same source-led fields. This view does not rank a winner; verify current vendor terms before purchase.</p>

        <div className="space-y-4 text-sm overflow-x-auto pb-2">
          
          {/* Row 1: Header / Tool Selector */}
          <div className={`grid ${selectedToolC ? 'grid-cols-3' : 'grid-cols-2'} gap-3 min-w-[680px]`}>
            <div className="p-4 rounded-2xl bg-[#181a29] border border-purple-500/30 flex items-center gap-3">
              <img src={toolA.logo_url} alt={toolA.name} className="h-8 w-8 rounded-lg bg-slate-900 object-contain p-1 border border-[#222538]" onError={(e) => e.target.style.display = 'none'} />
              <div>
                <div className="font-extrabold text-white text-base">{toolA.name}</div>
                <div className="text-[10px] text-purple-400 font-bold">{toolA.category_display}</div>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-[#181a29] border border-blue-500/30 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <img src={selectedToolB.logo_url} alt={selectedToolB.name} className="h-8 w-8 rounded-lg bg-slate-900 object-contain p-1 border border-[#222538]" onError={(e) => e.target.style.display = 'none'} />
                <div>
                  <div className="font-extrabold text-white text-base">{selectedToolB.name}</div>
                  <div className="text-[10px] text-blue-400 font-bold">{selectedToolB.category_display}</div>
                </div>
              </div>

              {availableTools.length > 0 && (
                <select
                  aria-label="Choose second tool"
                  value={selectedToolB.id}
                  onChange={(e) => {
                    const found = allTools.find(t => t.id === e.target.value);
                    if (found) setSelectedToolB(found);
                  }}
                  className="bg-[#131520] text-xs text-slate-300 border border-[#222538] rounded-lg px-2 py-1 focus:outline-none focus:border-blue-500"
                >
                  <option value={selectedToolB.id}>Change B...</option>
                  {availableTools.map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              )}
            </div>

            {selectedToolC ? (
              <div className="p-4 rounded-2xl bg-[#181a29] border border-emerald-500/30 flex items-center justify-between gap-3 relative">
                <div className="flex items-center gap-3">
                  <img src={selectedToolC.logo_url} alt={selectedToolC.name} className="h-8 w-8 rounded-lg bg-slate-900 object-contain p-1 border border-[#222538]" onError={(e) => e.target.style.display = 'none'} />
                  <div>
                    <div className="font-extrabold text-white text-base">{selectedToolC.name}</div>
                    <div className="text-[10px] text-emerald-400 font-bold">{selectedToolC.category_display}</div>
                  </div>
                </div>
                <button 
                  type="button"
                  onClick={() => setSelectedToolC(null)}
                  aria-label={`Remove ${selectedToolC.name} from comparison`}
                  className="text-slate-500 hover:text-rose-400 p-1"
                  title="Remove 3rd tool"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ) : (
              availableTools.length > 0 && (
                <div className="p-4 rounded-2xl bg-[#181a29]/40 border border-dashed border-[#222538] flex items-center justify-center">
                  <select
                    aria-label="Add a third tool"
                    onChange={(e) => {
                      const found = allTools.find(t => t.id === e.target.value);
                      if (found) setSelectedToolC(found);
                    }}
                    className="bg-[#131520] text-xs text-purple-300 border border-[#222538] rounded-lg px-3 py-2 focus:outline-none focus:border-purple-500 font-bold cursor-pointer"
                  >
                    <option value="">+ Add 3rd Tool to Compare</option>
                    {availableTools.map(t => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </div>
              )
            )}
          </div>

          {/* Row 2: Ratings & Pricing */}
          <div className={`grid ${selectedToolC ? 'grid-cols-3' : 'grid-cols-2'} gap-3 p-4 rounded-2xl bg-[#131520] border border-[#222538] min-w-[680px]`}>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Pricing Plan</div>
              <div className="text-sm font-black text-emerald-400 mt-0.5">{toolA.pricing}</div>
              <div className="text-[10px] text-slate-500 font-extrabold mt-1">No sourced rating</div>
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Pricing Plan</div>
              <div className="text-sm font-black text-emerald-400 mt-0.5">{selectedToolB.pricing}</div>
              <div className="text-[10px] text-slate-500 font-extrabold mt-1">No sourced rating</div>
            </div>
            {selectedToolC && (
              <div>
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Pricing Plan</div>
                <div className="text-sm font-black text-emerald-400 mt-0.5">{selectedToolC.pricing}</div>
                <div className="text-[10px] text-slate-500 font-extrabold mt-1">No sourced rating</div>
              </div>
            )}
          </div>

          {/* Row 3: Key Features */}
          <div className={`grid ${selectedToolC ? 'grid-cols-3' : 'grid-cols-2'} gap-3 p-4 rounded-2xl bg-[#131520] border border-[#222538] min-w-[680px]`}>
            <div>
              <div className="text-[10px] font-bold text-purple-300 uppercase tracking-wider mb-2">{toolA.name} Features</div>
              <div className="space-y-1.5 text-xs text-slate-300">
                {toolA.key_features?.map((f, i) => (
                  <div key={i} className="flex items-center gap-1.5">
                    <Zap className="h-3 w-3 text-purple-400 shrink-0" />
                    <span className="truncate">{f}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="text-[10px] font-bold text-blue-300 uppercase tracking-wider mb-2">{selectedToolB.name} Features</div>
              <div className="space-y-1.5 text-xs text-slate-300">
                {selectedToolB.key_features?.map((f, i) => (
                  <div key={i} className="flex items-center gap-1.5">
                    <Zap className="h-3 w-3 text-blue-400 shrink-0" />
                    <span className="truncate">{f}</span>
                  </div>
                ))}
              </div>
            </div>

            {selectedToolC && (
              <div>
                <div className="text-[10px] font-bold text-emerald-300 uppercase tracking-wider mb-2">{selectedToolC.name} Features</div>
                <div className="space-y-1.5 text-xs text-slate-300">
                  {selectedToolC.key_features?.map((f, i) => (
                    <div key={i} className="flex items-center gap-1.5">
                      <Zap className="h-3 w-3 text-emerald-400 shrink-0" />
                      <span className="truncate">{f}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Row 4: CTAs */}
          <div className={`grid ${selectedToolC ? 'grid-cols-3' : 'grid-cols-2'} gap-3 pt-2 min-w-[680px]`}>
            {urlA && (
              <a
                href={urlA}
                target="_blank"
                rel={toolA.is_sponsored === true ? 'sponsored noopener noreferrer' : 'noopener noreferrer'}
                className="py-3 px-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 font-extrabold text-xs text-white text-center flex items-center justify-center gap-1 shadow-lg shadow-purple-950/40 hover:brightness-110 transition-all"
              >
                <span>Check {toolA.name}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
            {urlB && (
              <a
                href={urlB}
                target="_blank"
                rel={selectedToolB.is_sponsored === true ? 'sponsored noopener noreferrer' : 'noopener noreferrer'}
                className="py-3 px-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 font-extrabold text-xs text-white text-center flex items-center justify-center gap-1 shadow-lg shadow-blue-950/40 hover:brightness-110 transition-all"
              >
                <span>Check {selectedToolB.name}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
            {selectedToolC && urlC && (
              <a
                href={urlC}
                target="_blank"
                rel={selectedToolC.is_sponsored === true ? 'sponsored noopener noreferrer' : 'noopener noreferrer'}
                className="py-3 px-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 font-extrabold text-xs text-white text-center flex items-center justify-center gap-1 shadow-lg shadow-emerald-950/40 hover:brightness-110 transition-all"
              >
                <span>Check {selectedToolC.name}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
