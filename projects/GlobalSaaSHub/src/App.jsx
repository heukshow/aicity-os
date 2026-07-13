import React, { useState, useMemo } from 'react';
import toolsData from '../data/tools.json';
import { 
  Search, 
  Sparkles, 
  Cpu, 
  Layers, 
  ExternalLink, 
  Star, 
  DollarSign, 
  ArrowUpRight, 
  ChevronRight, 
  HelpCircle,
  TrendingUp,
  Award
} from 'lucide-react';

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Categories definition
  const categories = [
    { id: 'all', name: 'All Resources', icon: Layers },
    { id: 'automation', name: 'Workflow Automation', icon: Cpu },
    { id: 'creator', name: 'Creator & Productivity', icon: Sparkles },
    { id: 'developer', name: 'Developer APIs', icon: Layers }
  ];

  // Filter & Search Logic
  const filteredTools = useMemo(() => {
    return toolsData.filter(tool => {
      const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory;
      const matchesSearch = tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.key_features.some(f => f.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesCategory && matchesSearch;
    });
  }, [searchTerm, selectedCategory]);

  // Statistics
  const stats = useMemo(() => {
    const total = toolsData.length;
    const avgCommission = "35%";
    const categoriesCount = new Set(toolsData.map(t => t.category)).size;
    return { total, avgCommission, categoriesCount };
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
            <a 
              href="#submit"
              className="text-xs sm:text-sm font-medium px-4 py-2 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 hover:bg-purple-500/20 transition-all duration-200"
            >
              Submit a Tool
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12 text-center relative z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold mb-6 animate-pulse">
          <Award className="h-3.5 w-3.5" /> Direct Affiliate Engine Built for Passive Income
        </div>
        <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-none mb-6">
          The Curated Directory of <br />
          <span className="bg-gradient-to-r from-purple-400 via-indigo-300 to-blue-400 bg-clip-text text-transparent">
            High-Yield AI & B2B SaaS
          </span>
        </h1>
        <p className="text-slate-400 text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
          Discover high-retention software products that pay lifetime recurring commissions. Fully automated curation.
        </p>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto p-4 rounded-2xl bg-[#131520] border border-[#222538]">
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-extrabold text-white">{stats.total}</div>
            <div className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider mt-1">Monetized Tools</div>
          </div>
          <div className="text-center border-x border-[#222538]">
            <div className="text-2xl sm:text-3xl font-extrabold text-purple-400">{stats.avgCommission}</div>
            <div className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider mt-1">Avg. Recurring</div>
          </div>
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-extrabold text-blue-400">{stats.categoriesCount}</div>
            <div className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider mt-1">Niche Sectors</div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24 relative z-10">
        
        {/* Controls Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10 p-5 rounded-2xl bg-[#131520]/60 border border-[#222538] backdrop-blur-sm">
          
          {/* Category Tabs */}
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

          {/* Search Box */}
          <div className="relative min-w-[280px] md:w-80">
            <Search className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search tools, tags, features..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#181a29]/80 border border-[#222538] hover:border-slate-700 focus:border-purple-500 rounded-xl py-3 pl-11 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-900/50 transition-all duration-300"
            />
          </div>

        </div>

        {/* Directory Grid */}
        {filteredTools.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTools.map((tool) => (
              <div 
                key={tool.id}
                className="group relative rounded-2xl bg-[#131520] border border-[#222538] hover:border-purple-500/40 p-6 flex flex-col justify-between transition-all duration-300 hover:translate-y-[-4px] hover:shadow-xl hover:shadow-purple-950/10"
              >
                <div>
                  {/* Top Info & Badge */}
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div className="flex items-center gap-3">
                      <div className="h-12 w-12 rounded-xl overflow-hidden border border-[#222538] bg-slate-900 flex items-center justify-center">
                        <img 
                          src={tool.logo_url} 
                          alt={tool.name} 
                          className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      </div>
                      <div>
                        <h3 className="font-bold text-lg text-white group-hover:text-purple-400 transition-colors duration-200">
                          {tool.name}
                        </h3>
                        <span className="text-[10px] font-semibold text-purple-400 uppercase tracking-widest bg-purple-500/5 border border-purple-500/20 px-2 py-0.5 rounded-full">
                          {tool.category_display}
                        </span>
                      </div>
                    </div>
                    
                    {/* Star Rating */}
                    <div className="flex items-center gap-1 text-amber-500 bg-amber-500/5 px-2 py-1 rounded-lg text-xs font-bold border border-amber-500/10">
                      <Star className="h-3 w-3 fill-amber-500" />
                      {tool.rating}
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

                {/* Bottom CTA Block */}
                <div className="border-t border-[#222538]/60 pt-4 mt-2">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider">Pricing</div>
                      <div className="text-sm font-bold text-slate-300">{tool.pricing}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-purple-400 uppercase tracking-wider font-semibold">Commission</div>
                      <div className="text-sm font-black text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded-md border border-purple-500/20">
                        {tool.commission}
                      </div>
                    </div>
                  </div>

                  <a
                    href={tool.affiliate_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold py-3 px-4 rounded-xl transition-all duration-300 shadow-lg shadow-purple-950/30 group-hover:shadow-purple-900/20"
                  >
                    <span>Visit & Access Tool</span>
                    <ArrowUpRight className="h-4 w-4 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-200" />
                  </a>
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
                onClick={() => alert("PayPal Sponsorship Flow Integration Demo")}
                className="bg-purple-600 hover:bg-purple-500 text-white font-bold py-3.5 px-6 rounded-xl transition-all duration-300 inline-flex items-center gap-2"
              >
                <span>Submit Product ($49/year)</span>
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-[#222538] bg-[#07080c] py-12 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="h-7 w-7 rounded-md bg-purple-600 flex items-center justify-center">
              <TrendingUp className="h-4 w-4 text-white" />
            </div>
            <span className="font-bold text-sm text-white">GlobalSaaSHub</span>
          </div>
          <p className="text-slate-500 text-xs text-center sm:text-right">
            &copy; {new Date().getFullYear()} GlobalSaaSHub. Programmatic Curation Engine. All rights reserved.
          </p>
        </div>
      </footer>

    </div>
  );
}
