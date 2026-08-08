import React, { useState, useMemo, useEffect } from 'react';
import toolsData from '../data/tools.json';
import CompareModal from './components/CompareModal';
import { getValidExternalUrl } from './utils/url';
import { 
  Search, 
  Sparkles, 
  Cpu, 
  Layers, 
  ExternalLink, 
  Star, 
  DollarSign, 
  ArrowUpRight, 
  HelpCircle,
  TrendingUp,
  Award,
  BarChart3,
  Heart,
  Scale,
  Video,
  Mic,
  Image as ImageIcon,
  Code,
  FileText,
  Briefcase,
  Wand2,
  MessageSquare,
  Mail,
  SearchCode,
  Database,
  Bot,
  CreditCard
} from 'lucide-react';


import { trackPageView, trackToolClick } from './utils/analytics';



function ToolLogo({ tool }) {
  const [error, setError] = useState(false);

  if (error || !tool.logo_url) {
    const firstChar = tool.name ? tool.name.charAt(0).toUpperCase() : 'A';
    return (
      <div className="h-full w-full bg-gradient-to-br from-purple-600/30 to-indigo-600/30 border border-purple-500/20 flex items-center justify-center font-extrabold text-lg text-purple-300">
        {firstChar}
      </div>
    );
  }

  return (
    <img 
      src={tool.logo_url} 
      alt={tool.name} 
      onError={() => setError(true)}
      className="h-full w-full object-contain p-1.5 group-hover:scale-105 transition-transform duration-300 bg-[#181a29]"
    />
  );
}

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [compareToolA, setCompareToolA] = useState(null);
  const [showBookmarksOnly, setShowBookmarksOnly] = useState(false);
  const [bookmarkedIds, setBookmarkedIds] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('coshuma_bookmarks') || '[]');
    } catch (e) {
      return [];
    }
  });

  const toggleBookmark = (id) => {
    setBookmarkedIds(prev => {
      const next = prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id];
      localStorage.setItem('coshuma_bookmarks', JSON.stringify(next));
      return next;
    });
  };

  useEffect(() => {
    trackPageView(selectedCategory);
  }, [selectedCategory]);



  const [selectedPricing, setSelectedPricing] = useState('all');

  // 15 Hyper-Targeted Micro Categories Definition
  const categories = [
    { id: 'all', name: 'All Categories', icon: Layers },
    { id: 'workflow_auto', name: 'Workflow Automation', icon: Cpu },
    { id: 'sales_crm', name: 'Sales & CRM', icon: Briefcase },
    { id: 'chatbots_support', name: 'Chatbots & Support', icon: MessageSquare },
    { id: 'video_gen', name: 'Video & Shorts Gen', icon: Video },
    { id: 'voice_cloning', name: 'Voice & Speech AI', icon: Mic },
    { id: 'email_outreach', name: 'Email & Outreach', icon: Mail },
    { id: 'copywriting', name: 'AI Copywriting', icon: Sparkles },
    { id: 'seo_tools', name: 'SEO & Optimization', icon: SearchCode },
    { id: 'design_art', name: 'Design & Graphics', icon: ImageIcon },
    { id: 'image_gen', name: 'Image & Photo AI', icon: Wand2 },
    { id: 'dev_coding', name: 'Coding & Dev Tools', icon: Code },
    { id: 'scraping_data', name: 'Data & Scraping APIs', icon: Database },
    { id: 'ai_agents', name: 'Autonomous AI Agents', icon: Bot },
    { id: 'finance_billing', name: 'Finance & Billing', icon: CreditCard },
    { id: 'productivity', name: 'Productivity & SaaS', icon: Layers }
  ];



  // Detailed Price Range Filters Definition
  const pricingOptions = [
    { id: 'all', name: 'All Pricing' },
    { id: 'free', name: '🎁 Free / Free Trial' },
    { id: 'under20', name: '⚡ Under $20/mo' },
    { id: 'under50', name: '💵 $20 - $50/mo' },
    { id: 'over50', name: '🚀 $50+/mo' }
  ];

  // Auto-complete suggestions for search term
  const autocompleteSuggestions = useMemo(() => {
    if (!searchTerm.trim() || searchTerm.length < 1) return [];
    const term = searchTerm.toLowerCase();
    return toolsData.filter(t => 
      t.name.toLowerCase().includes(term) || 
      t.category_display.toLowerCase().includes(term)
    ).slice(0, 5);
  }, [searchTerm]);

  // Filter & Search Logic
  const filteredTools = useMemo(() => {
    return toolsData.filter(tool => {
      const matchesBookmark = !showBookmarksOnly || bookmarkedIds.includes(tool.id);
      const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory;
      
      const pricingLower = (tool.pricing || '').toLowerCase();
      let matchesPricing = true;
      
      // Extract numeric price dollar amount
      const priceMatch = (tool.pricing || '').match(/\$(\d+)/);
      const numericPrice = priceMatch ? parseInt(priceMatch[1], 10) : (pricingLower.includes('free') ? 0 : 25);

      if (selectedPricing === 'free') {
        matchesPricing = pricingLower.includes('free');
      } else if (selectedPricing === 'under20') {
        matchesPricing = numericPrice <= 20 || pricingLower.includes('free');
      } else if (selectedPricing === 'under50') {
        matchesPricing = numericPrice >= 20 && numericPrice <= 50;
      } else if (selectedPricing === 'over50') {
        matchesPricing = numericPrice > 50;
      }

      const matchesSearch = tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.key_features.some(f => f.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesBookmark && matchesCategory && matchesPricing && matchesSearch;
    });
  }, [searchTerm, selectedCategory, selectedPricing, showBookmarksOnly, bookmarkedIds]);




  // Statistics
  const stats = useMemo(() => {
    const total = toolsData.length;
    const categoriesCount = new Set(toolsData.map(t => t.category)).size;
    return { total, categoriesCount };
  }, []);


  return (
    <div className="min-h-screen bg-[#090a0f] text-slate-100 selection:bg-purple-500 selection:text-white relative overflow-hidden">
      
      {/* Decorative Background Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-purple-900/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[20%] right-[-10%] w-[45%] h-[45%] rounded-full bg-blue-900/10 blur-[120px] pointer-events-none" />

      {/* Navigation */}
      <nav className="border-b border-[#222538] backdrop-blur-md sticky top-0 z-50 bg-[#090a0f]/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-950/50">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-purple-400 bg-clip-text text-transparent">
              GlobalSaaSHub
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button
              type="button"
              disabled
              title="Sponsorship submissions temporarily unavailable while secure checkout is being configured"
              className="text-xs sm:text-sm font-medium px-4 py-2 rounded-full border border-slate-700 bg-slate-800/60 text-slate-500 cursor-not-allowed"
            >
              Sponsorship submissions temporarily unavailable
            </button>
          </div>


        </div>
      </nav>


      {/* Hero Section */}
      <header className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12 text-center relative z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold mb-6 animate-pulse">
          <Award className="h-3.5 w-3.5" /> Curated AI & SaaS Directory for Professionals & Teams
        </div>
        <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-none mb-6">
          The Curated Directory of <br />
          <span className="bg-gradient-to-r from-purple-400 via-indigo-300 to-blue-400 bg-clip-text text-transparent">
            Next-Gen AI & B2B SaaS
          </span>
        </h1>
        <p className="text-slate-400 text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
          Discover top-tier AI software, productivity tools, and APIs to scale your workflow and business.
        </p>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto p-4 rounded-2xl bg-[#131520] border border-[#222538]">
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-extrabold text-white">{stats.total}</div>
            <div className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider mt-1">Curated SaaS Profiles</div>
          </div>
          <div className="text-center border-x border-[#222538]">
            <div className="text-2xl sm:text-3xl font-extrabold text-purple-400">Source-led</div>
            <div className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider mt-1">Pricing Details</div>
          </div>
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-extrabold text-blue-400">{stats.categoriesCount}</div>
            <div className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider mt-1">Categories</div>
          </div>
        </div>
      </header>


      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24 relative z-10">
        
        {/* Controls Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10 p-5 rounded-2xl bg-[#131520]/60 border border-[#222538] backdrop-blur-sm">
          
          {/* Category Tabs & Pricing Filter */}
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => {
                const Icon = cat.icon;
                const isActive = selectedCategory === cat.id;
                return (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                      isActive 
                        ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/40 translate-y-[-1px]' 
                        : 'bg-[#181a29]/80 text-slate-400 hover:text-white border border-[#222538] hover:border-purple-500/30'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {cat.name}
                  </button>
                );
              })}
            </div>

            {/* Pricing Options Sub-Filter & Bookmarks */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mr-1">Filter Price:</span>
              {pricingOptions.map((opt) => {
                const isActive = selectedPricing === opt.id;
                return (
                  <button
                    key={opt.id}
                    onClick={() => setSelectedPricing(opt.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                      isActive 
                        ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md' 
                        : 'bg-[#181a29] text-slate-400 hover:text-white border border-[#222538]'
                    }`}
                  >
                    {opt.name}
                  </button>
                );
              })}

              {/* Bookmarks Toggle Button */}
              <button
                onClick={() => setShowBookmarksOnly(!showBookmarksOnly)}
                className={`ml-auto sm:ml-4 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                  showBookmarksOnly 
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-md' 
                    : 'bg-[#181a29] text-slate-400 hover:text-white border-[#222538]'
                }`}
              >
                <Heart className={`h-3.5 w-3.5 ${showBookmarksOnly ? 'fill-rose-500 text-rose-500' : ''}`} />
                <span>Saved ({bookmarkedIds.length})</span>
              </button>
            </div>
          </div>


          {/* Search Box with Real-time Auto-complete */}
          <div className="relative min-w-[280px] md:w-80">
            <Search className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search tools, tags, features..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#181a29]/80 border border-[#222538] hover:border-slate-700 focus:border-purple-500 rounded-xl py-3 pl-11 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-900/50 transition-all duration-300"
            />

            {/* Auto-complete Dropdown */}
            {autocompleteSuggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-[#131520] border border-purple-500/30 rounded-2xl shadow-2xl z-50 overflow-hidden divide-y divide-[#222538]">
                {autocompleteSuggestions.map((sug) => (
                  <div
                    key={sug.id}
                    onClick={() => {
                      setSearchTerm(sug.name);
                    }}
                    className="p-3 hover:bg-[#181a29] cursor-pointer flex items-center justify-between transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <div className="h-6 w-6 rounded bg-[#181a29] p-0.5 overflow-hidden border border-[#222538]">
                        <img src={sug.logo_url} alt={sug.name} className="h-full w-full object-contain" />
                      </div>
                      <span className="text-xs font-bold text-white">{sug.name}</span>
                    </div>
                    <span className="text-[10px] text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                      {sug.category_display}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>


        </div>

        {/* Directory Grid */}
        {filteredTools.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTools.map((tool) => (
              <div 
                key={tool.id}
                className="group relative rounded-2xl bg-[#131520] border border-[#222538] hover:border-purple-500/40 p-6 flex flex-col justify-between transition-all duration-300 hover:translate-y-[-4px] hover:shadow-xl hover:shadow-purple-950/10 overflow-hidden"
              >
                {/* Badge Determination */}
                {(() => {
                  let badge = null;
                  if (tool.id === 'gohighlevel' || tool.id === 'elevenlabs' || tool.id === 'notion-ai' || tool.isSponsored) {
                    badge = { text: '🔥 HOT', bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' };
                  } else if (tool.rating >= 4.8) {
                    badge = { text: '👑 BEST', bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400' };
                  } else if (tool.id.includes('kit') || tool.id.includes('ai') || tool.id.includes('bot')) {
                    badge = { text: '⚡ NEW', bg: 'bg-purple-500/10 border-purple-500/30 text-purple-300' };
                  }
                  
                  if (!badge) return null;

                  return (
                    <div className="absolute top-3 right-3 z-10">
                      <span className={`text-[10px] font-black px-2.5 py-1 rounded-full border shadow-sm ${badge.bg}`}>
                        {badge.text}
                      </span>
                    </div>
                  );
                })()}

                <div>
                  {/* Top Info & Badge & Bookmark Button */}
                  <div className="flex items-start justify-between gap-4 mb-4 pr-12">
                    <div className="flex items-center gap-3">
                      <div className="h-12 w-12 rounded-xl overflow-hidden border border-[#222538] bg-slate-900 flex items-center justify-center shrink-0">
                        <ToolLogo tool={tool} />
                      </div>

                      <div>
                        <a 
                          href={`/tool/${tool.id}.html`}
                          className="font-bold text-lg text-white hover:text-purple-400 transition-colors duration-200 block"
                        >
                          {tool.name}
                        </a>
                        <span className="text-[10px] font-semibold text-purple-400 uppercase tracking-widest bg-purple-500/5 border border-purple-500/20 px-2 py-0.5 rounded-full inline-block mt-0.5">
                          {tool.category_display}
                        </span>
                      </div>

                    </div>
                    
                    {/* Star Rating & Bookmark Button */}
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => toggleBookmark(tool.id)}
                        className={`p-1.5 rounded-lg border transition-all ${
                          bookmarkedIds.includes(tool.id) 
                            ? 'bg-rose-500/20 border-rose-500/40 text-rose-500' 
                            : 'bg-[#181a29] border-[#222538] text-slate-500 hover:text-slate-300'
                        }`}
                        title="Save to bookmarks"
                      >
                        <Heart className={`h-4 w-4 ${bookmarkedIds.includes(tool.id) ? 'fill-rose-500' : ''}`} />
                      </button>

                      {tool.rating != null && tool.rating_source_url && (
                        <div className="flex items-center gap-1 text-amber-500 bg-amber-500/5 px-2 py-1 rounded-lg text-xs font-bold border border-amber-500/10">
                          <Star className="h-3 w-3 fill-amber-500" />
                          {tool.rating}
                        </div>
                      )}
                    </div>
                  </div>


                  {/* Description */}
                  <p className="text-slate-400 text-sm leading-relaxed mb-6">
                    {tool.description}
                  </p>

                  {/* Key Features */}
                  <div className="flex flex-wrap gap-1.5 mb-6">
                    {tool.key_features.map((feature, idx) => (
                      <span 
                        key={idx} 
                        className="text-xs bg-[#181a29] text-slate-300 px-2.5 py-1 rounded-lg border border-[#222538]"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Bottom CTA & Compare Block */}
                <div className="border-t border-[#222538]/60 pt-4 mt-2">
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Pricing</div>
                      <div className="text-sm font-bold text-slate-200">{tool.pricing}</div>
                    </div>

                    <button
                      onClick={() => setCompareToolA(tool)}
                      className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#181a29] border border-[#222538] hover:border-purple-500/40 text-xs font-bold text-purple-300 hover:text-white transition-all"
                      title="Compare side-by-side"
                    >
                      <Scale className="h-3.5 w-3.5 text-purple-400" />
                      <span>VS Compare</span>
                    </button>
                  </div>


                  {(() => {
                    const validUrl = getValidExternalUrl(tool);
                    return validUrl ? (
                      <a
                        href={validUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={() => trackToolClick(tool.id, tool.name)}
                        className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold py-3 px-4 rounded-xl transition-all duration-300 shadow-lg shadow-purple-950/30 group-hover:shadow-purple-900/20"
                      >
                        <span>Visit & Access Tool</span>
                        <ArrowUpRight className="h-4 w-4 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-200" />
                      </a>
                    ) : (
                      <div className="w-full py-3 px-4 rounded-xl bg-slate-800 text-slate-500 font-bold text-xs text-center border border-slate-700/50">
                        Official Link Unavailable
                      </div>
                    );
                  })()}
                </div>


              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-[#131520]/30 rounded-3xl border border-[#222538] backdrop-blur-sm max-w-2xl mx-auto">
            <HelpCircle className="h-12 w-12 text-slate-600 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">No tools match your query</h3>
            <p className="text-slate-400 text-sm">
              Try searching with different keywords or choosing another category.
            </p>
          </div>
        )}

        {/* Affiliate Promotion Banner */}
        <section id="submit" className="mt-24 p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-[#12131e] to-[#0d0e17] border border-[#222538] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-purple-600/5 rounded-full blur-[80px]" />
          
          <div className="max-w-2xl relative z-10">
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white mb-4">
              Submit Your Product to GlobalSaaSHub
            </h2>
            <p className="text-slate-400 mb-8 leading-relaxed">
              Are you a founder? Get listed in front of thousands of digital creators, automators, and developers. Custom sponsorship positions available.
            </p>
            <div className="flex flex-wrap gap-4">
              <button
                type="button"
                disabled
                className="bg-slate-800 text-slate-500 font-bold py-3.5 px-6 rounded-xl inline-flex items-center gap-2 border border-slate-700 cursor-not-allowed"
              >
                <span>Sponsorship submissions temporarily unavailable while secure checkout is being configured</span>
              </button>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-[#222538] bg-[#07080c] py-12 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-8 border-b border-[#222538]/50">
            <div className="flex items-center gap-3">
              <div className="h-7 w-7 rounded-md bg-purple-600 flex items-center justify-center">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
              <span className="font-bold text-sm text-white">GlobalSaaSHub</span>
            </div>
            <div className="flex items-center gap-6 text-xs">
              <a href="/privacy.html" className="text-slate-400 hover:text-white transition-colors">Privacy Policy</a>
              <a href="/terms.html" className="text-slate-400 hover:text-white transition-colors">Terms of Service</a>
            </div>


          </div>
          
          <div className="pt-8 flex flex-col lg:flex-row items-center justify-between gap-6">
            <p className="text-slate-500 text-[11px] max-w-2xl leading-relaxed text-center lg:text-left">
              <strong>About:</strong> GlobalSaaSHub is an independent software directory. We curate top-rated AI & B2B SaaS tools to help professionals and teams find the best software solutions.
            </p>

            <p className="text-slate-500 text-xs text-center lg:text-right whitespace-nowrap">
              &copy; {new Date().getFullYear()} GlobalSaaSHub. Programmatic Curation Engine. All rights reserved.
            </p>
          </div>
        </div>
      </footer>

      {/* Side-by-Side 1:1 Tool Compare Modal */}
      {compareToolA && (
        <CompareModal 
          toolA={compareToolA} 
          allTools={toolsData} 
          onClose={() => setCompareToolA(null)} 
        />
      )}

    </div>
  );
}


