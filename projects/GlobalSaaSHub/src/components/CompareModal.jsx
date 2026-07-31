import React, { useState } from 'react';
import { X, Scale, Star, ExternalLink, CheckCircle2, ArrowRight } from 'lucide-react';

export default function CompareModal({ toolA, toolB, allTools, onClose }) {
  const sameCategoryTools = allTools.filter(t => t.id !== toolA.id && (t.category === toolA.category || t.category_display === toolA.category_display));
  const otherTools = allTools.filter(t => t.id !== toolA.id && t.category !== toolA.category && t.category_display !== toolA.category_display);
  
  const initialB = toolB || (sameCategoryTools.length > 0 ? sameCategoryTools[0] : allTools.find(t => t.id !== toolA.id));
  const [selectedToolB, setSelectedToolB] = useState(initialB);
  const [selectedToolC, setSelectedToolC] = useState(null);

  if (!toolA) return null;


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-[#131520] border border-[#222538] rounded-3xl max-w-3xl w-full p-6 sm:p-8 relative shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full bg-[#181a29] border border-[#222538] text-slate-400 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Title */}
        <div className="flex items-center gap-3 mb-6">
          <div className="h-10 w-10 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <Scale className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-white">Side-by-Side Tool Comparison</h2>
            <p className="text-xs text-slate-400">Comparing <span className="text-purple-300 font-bold">{toolA.name}</span> with same-category competitor tools</p>
          </div>
        </div>

        {/* Tool Selectors Grid (2 or 3 Tools) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 mb-6">
          <div className="p-3 rounded-2xl bg-[#181a29] border border-purple-500/40 text-center font-bold text-xs text-purple-300">
            {toolA.name} ({toolA.category_display})
          </div>
          <div>
            <select
              value={selectedToolB.id}
              onChange={(e) => {
                const found = allTools.find(t => t.id === e.target.value);
                if (found) setSelectedToolB(found);
              }}
              className="w-full p-3 rounded-2xl bg-[#181a29] border border-[#222538] font-bold text-xs text-white focus:outline-none focus:border-purple-500"
            >
              {sameCategoryTools.length > 0 && (
                <optgroup label={`🎯 Competitor 1 (${toolA.category_display})`}>
                  {sameCategoryTools.map(t => (
                    <option key={t.id} value={t.id} className="bg-[#131520] text-white">
                      VS {t.name}
                    </option>
                  ))}
                </optgroup>
              )}
              {otherTools.length > 0 && (
                <optgroup label="🌐 Other Tools">
                  {otherTools.map(t => (
                    <option key={t.id} value={t.id} className="bg-[#131520] text-slate-300">
                      VS {t.name} ({t.category_display})
                    </option>
                  ))}
                </optgroup>
              )}
            </select>
          </div>
          <div>
            <select
              value={selectedToolC ? selectedToolC.id : ''}
              onChange={(e) => {
                const found = allTools.find(t => t.id === e.target.value);
                setSelectedToolC(found || null);
              }}
              className="w-full p-3 rounded-2xl bg-[#181a29] border border-[#222538] font-bold text-xs text-purple-300 focus:outline-none focus:border-purple-500"
            >
              <option value="">+ Add 3rd Tool (Same Category)</option>
              {sameCategoryTools.filter(t => t.id !== selectedToolB.id).map(t => (
                <option key={t.id} value={t.id} className="bg-[#131520] text-white">
                  VS {t.name}
                </option>
              ))}

            </select>
          </div>
        </div>



        {/* Comparison Table */}
        <div className="space-y-4">
          
          {/* Row 1: Rating */}
          <div className={`grid ${selectedToolC ? 'grid-cols-3' : 'grid-cols-2'} gap-3 p-4 rounded-xl bg-[#181a29]/60 border border-[#222538] text-center`}>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">{toolA.name} Rating</div>
              <div className="text-sm sm:text-base font-black text-amber-400 flex items-center justify-center gap-1">
                <Star className="h-4 w-4 fill-amber-400" />
                {toolA.rating} / 5.0
              </div>
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">{selectedToolB.name} Rating</div>
              <div className="text-sm sm:text-base font-black text-amber-400 flex items-center justify-center gap-1">
                <Star className="h-4 w-4 fill-amber-400" />
                {selectedToolB.rating} / 5.0
              </div>
            </div>
            {selectedToolC && (
              <div>
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">{selectedToolC.name} Rating</div>
                <div className="text-sm sm:text-base font-black text-amber-400 flex items-center justify-center gap-1">
                  <Star className="h-4 w-4 fill-amber-400" />
                  {selectedToolC.rating} / 5.0
                </div>
              </div>
            )}
          </div>

          {/* Row 2: Pricing */}
          <div className={`grid ${selectedToolC ? 'grid-cols-3' : 'grid-cols-2'} gap-3 p-4 rounded-xl bg-[#181a29]/60 border border-[#222538] text-center`}>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Pricing</div>
              <div className="text-xs sm:text-sm font-extrabold text-emerald-400">{toolA.pricing}</div>
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Pricing</div>
              <div className="text-xs sm:text-sm font-extrabold text-emerald-400">{selectedToolB.pricing}</div>
            </div>
            {selectedToolC && (
              <div>
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Pricing</div>
                <div className="text-xs sm:text-sm font-extrabold text-emerald-400">{selectedToolC.pricing}</div>
              </div>
            )}
          </div>

          {/* Row 3: Key Features */}
          <div className={`grid ${selectedToolC ? 'grid-cols-3' : 'grid-cols-2'} gap-3 p-4 rounded-xl bg-[#181a29]/60 border border-[#222538]`}>
            <div>
              <div className="text-[10px] font-bold text-purple-300 uppercase tracking-wider mb-2 text-center">{toolA.name} Features</div>
              <div className="space-y-1.5">
                {toolA.key_features.map((f, i) => (
                  <div key={i} className="text-[11px] text-slate-300 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-purple-400 shrink-0" />
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="text-[10px] font-bold text-blue-300 uppercase tracking-wider mb-2 text-center">{selectedToolB.name} Features</div>
              <div className="space-y-1.5">
                {selectedToolB.key_features.map((f, i) => (
                  <div key={i} className="text-[11px] text-slate-300 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-blue-400 shrink-0" />
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>
            {selectedToolC && (
              <div>
                <div className="text-[10px] font-bold text-emerald-300 uppercase tracking-wider mb-2 text-center">{selectedToolC.name} Features</div>
                <div className="space-y-1.5">
                  {selectedToolC.key_features.map((f, i) => (
                    <div key={i} className="text-[11px] text-slate-300 flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Row 4: CTAs */}
          <div className={`grid ${selectedToolC ? 'grid-cols-3' : 'grid-cols-2'} gap-3 pt-2`}>
            {(toolA.affiliate_url || toolA.official_url) && (
              <a
                href={toolA.affiliate_url || toolA.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="py-3 px-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 font-extrabold text-xs text-white text-center flex items-center justify-center gap-1 shadow-lg shadow-purple-950/40 hover:brightness-110 transition-all"
              >
                <span>Get {toolA.name}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
            {(selectedToolB.affiliate_url || selectedToolB.official_url) && (
              <a
                href={selectedToolB.affiliate_url || selectedToolB.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="py-3 px-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 font-extrabold text-xs text-white text-center flex items-center justify-center gap-1 shadow-lg shadow-blue-950/40 hover:brightness-110 transition-all"
              >
                <span>Get {selectedToolB.name}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
            {selectedToolC && (selectedToolC.affiliate_url || selectedToolC.official_url) && (
              <a
                href={selectedToolC.affiliate_url || selectedToolC.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="py-3 px-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 font-extrabold text-xs text-white text-center flex items-center justify-center gap-1 shadow-lg shadow-emerald-950/40 hover:brightness-110 transition-all"
              >
                <span>Get {selectedToolC.name}</span>
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>

        </div>


      </div>
    </div>
  );
}
