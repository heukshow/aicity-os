import React, { useEffect, useMemo, useState } from 'react';
import toolsData from '../data/tools.json';
import CompareModal from './components/CompareModal';
import SponsorshipCheckout from './components/SponsorshipCheckout';
import { paymentConfig } from './config/payment.js';
import { getValidExternalUrl } from './utils/url';
import {
  ArrowRight,
  ArrowUpRight,
  Award,
  Bot,
  Briefcase,
  CheckCircle2,
  Code,
  Cpu,
  CreditCard,
  Database,
  Heart,
  Image as ImageIcon,
  Layers,
  Mail,
  MessageSquare,
  Mic,
  Scale,
  Search,
  SearchCode,
  ShieldCheck,
  Sparkles,
  Star,
  TrendingUp,
  Video,
  Wand2
} from 'lucide-react';
import { trackPageView, trackToolClick } from './utils/analytics';

function ToolLogo({ tool }) {
  const [error, setError] = useState(false);
  if (error || !tool.logo_url) {
    const firstChar = tool.name ? tool.name.charAt(0).toUpperCase() : 'A';
    return (
      <div className="h-full w-full bg-gradient-to-br from-violet-500/20 to-cyan-500/20 flex items-center justify-center font-black text-lg text-violet-200">
        {firstChar}
      </div>
    );
  }

  return (
    <img
      src={tool.logo_url}
      alt={tool.name}
      onError={() => setError(true)}
      className="h-full w-full object-contain p-1.5 bg-white/95"
    />
  );
}

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPricing, setSelectedPricing] = useState('all');
  const [compareToolA, setCompareToolA] = useState(null);
  const [showBookmarksOnly, setShowBookmarksOnly] = useState(false);
  const [bookmarkedIds, setBookmarkedIds] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('coshuma_bookmarks') || '[]');
    } catch {
      return [];
    }
  });

  const categories = [
    { id: 'all', name: 'All', icon: Layers },
    { id: 'workflow_auto', name: 'Automation', icon: Cpu },
    { id: 'sales_crm', name: 'Sales & CRM', icon: Briefcase },
    { id: 'chatbots_support', name: 'Support', icon: MessageSquare },
    { id: 'video_gen', name: 'Video', icon: Video },
    { id: 'voice_cloning', name: 'Voice', icon: Mic },
    { id: 'email_outreach', name: 'Email', icon: Mail },
    { id: 'copywriting', name: 'Writing', icon: Sparkles },
    { id: 'seo_tools', name: 'SEO', icon: SearchCode },
    { id: 'design_art', name: 'Design', icon: ImageIcon },
    { id: 'image_gen', name: 'Image AI', icon: Wand2 },
    { id: 'dev_coding', name: 'Developer', icon: Code },
    { id: 'scraping_data', name: 'Data', icon: Database },
    { id: 'ai_agents', name: 'AI Agents', icon: Bot },
    { id: 'finance_billing', name: 'Finance', icon: CreditCard },
    { id: 'productivity', name: 'Productivity', icon: Layers }
  ];

  const pricingOptions = [
    { id: 'all', name: 'All pricing' },
    { id: 'free', name: 'Free / trial' },
    { id: 'under20', name: 'Under $20' },
    { id: 'under50', name: '$20–$50' },
    { id: 'over50', name: '$50+' }
  ];

  useEffect(() => {
    trackPageView(selectedCategory);
  }, [selectedCategory]);

  const toggleBookmark = (id) => {
    setBookmarkedIds((prev) => {
      const next = prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id];
      localStorage.setItem('coshuma_bookmarks', JSON.stringify(next));
      return next;
    });
  };

  const stats = useMemo(() => {
    const total = toolsData.length;
    const categoriesCount = new Set(toolsData.map((t) => t.category)).size;
    const verified = toolsData.filter((t) => t.affiliate_verified === true).length;
    return { total, categoriesCount, verified };
  }, []);

  const featuredTools = useMemo(() => {
    const preferred = ['gohighlevel', 'elevenlabs', 'make-com', 'descript', 'pictory', 'brand24'];
    return preferred.map((id) => toolsData.find((t) => t.id === id)).filter(Boolean).slice(0, 6);
  }, []);

  const autocompleteSuggestions = useMemo(() => {
    if (!searchTerm.trim()) return [];
    const term = searchTerm.toLowerCase();
    return toolsData
      .filter((t) =>
        (t.name || '').toLowerCase().includes(term) ||
        (t.category_display || '').toLowerCase().includes(term)
      )
      .slice(0, 6);
  }, [searchTerm]);

  const filteredTools = useMemo(() => {
    const term = searchTerm.toLowerCase();
    return toolsData.filter((tool) => {
      const matchesBookmark = !showBookmarksOnly || bookmarkedIds.includes(tool.id);
      const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory;
      const pricingLower = (tool.pricing || '').toLowerCase();
      const priceMatch = (tool.pricing || '').match(/\$(\d+)/);
      const numericPrice = priceMatch ? parseInt(priceMatch[1], 10) : pricingLower.includes('free') ? 0 : 25;
      let matchesPricing = true;
      if (selectedPricing === 'free') matchesPricing = pricingLower.includes('free') || pricingLower.includes('trial');
      if (selectedPricing === 'under20') matchesPricing = numericPrice < 20 || pricingLower.includes('free');
      if (selectedPricing === 'under50') matchesPricing = numericPrice >= 20 && numericPrice <= 50;
      if (selectedPricing === 'over50') matchesPricing = numericPrice > 50;

      const matchesSearch =
        !term ||
        (tool.name || '').toLowerCase().includes(term) ||
        (tool.description || '').toLowerCase().includes(term) ||
        (tool.category_display || '').toLowerCase().includes(term) ||
        (tool.key_features || []).some((f) => f.toLowerCase().includes(term));

      return matchesBookmark && matchesCategory && matchesPricing && matchesSearch;
    });
  }, [searchTerm, selectedCategory, selectedPricing, showBookmarksOnly, bookmarkedIds]);

  const chooseCategory = (id) => {
    setSelectedCategory(id);
    document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="min-h-screen bg-[#08090d] text-slate-100 selection:bg-violet-500 selection:text-white">
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 left-1/4 h-[34rem] w-[34rem] rounded-full bg-violet-700/10 blur-[140px]" />
        <div className="absolute top-1/3 -right-32 h-[28rem] w-[28rem] rounded-full bg-cyan-600/10 blur-[130px]" />
      </div>

      <nav className="sticky top-0 z-50 border-b border-white/10 bg-[#08090d]/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <a href="/" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 shadow-lg shadow-violet-950/40">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="text-lg font-black tracking-tight">COSHUMA</div>
              <div className="-mt-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">AI & SaaS decision guides</div>
            </div>
          </a>
          <div className="flex items-center gap-2">
            <a href="#directory" className="hidden rounded-full px-4 py-2 text-sm font-semibold text-slate-300 hover:bg-white/5 sm:inline-flex">Explore tools</a>
            {paymentConfig.checkoutEnabled && (
              <a href="#submit" className="rounded-full border border-violet-400/30 bg-violet-500/10 px-4 py-2 text-xs font-bold text-violet-200 hover:bg-violet-500/20 sm:text-sm">
                Sponsor a listing
              </a>
            )}
          </div>
        </div>
      </nav>

      <header className="relative z-10 mx-auto max-w-7xl px-4 pb-14 pt-14 sm:px-6 sm:pt-20 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-bold text-emerald-200">
            <ShieldCheck className="h-3.5 w-3.5" /> Independent buyer guides · pricing and links checked from public sources
          </div>
          <h1 className="text-4xl font-black tracking-[-0.04em] text-white sm:text-6xl lg:text-7xl">
            Find the right AI & SaaS tool
            <span className="block bg-gradient-to-r from-violet-300 via-white to-cyan-300 bg-clip-text text-transparent">without wasting money.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg">
            Compare pricing, use cases, strengths and verified public information before you subscribe. Start with what you need, not a giant software list.
          </p>

          <div className="relative mx-auto mt-8 max-w-3xl">
            <Search className="absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onFocus={() => document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'center' })}
              placeholder="Search a tool, task or feature — e.g. video, CRM, voice, SEO…"
              className="w-full rounded-2xl border border-white/10 bg-white/[0.06] py-4 pl-14 pr-5 text-base text-white shadow-2xl shadow-black/30 outline-none transition focus:border-violet-400/50 focus:bg-white/[0.08] focus:ring-4 focus:ring-violet-500/10"
            />
            {autocompleteSuggestions.length > 0 && (
              <div className="absolute left-0 right-0 top-full z-40 mt-2 overflow-hidden rounded-2xl border border-white/10 bg-[#11131a] text-left shadow-2xl">
                {autocompleteSuggestions.map((tool) => (
                  <a key={tool.id} href={`/tool/${tool.id}.html`} className="flex items-center justify-between border-b border-white/5 px-4 py-3 last:border-0 hover:bg-white/5">
                    <span className="font-semibold text-white">{tool.name}</span>
                    <span className="text-xs text-slate-500">{tool.category_display}</span>
                  </a>
                ))}
              </div>
            )}
          </div>

          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {categories.slice(1, 7).map((cat) => {
              const Icon = cat.icon;
              return (
                <button key={cat.id} onClick={() => chooseCategory(cat.id)} className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs font-semibold text-slate-300 hover:border-violet-400/30 hover:bg-violet-400/10 hover:text-white">
                  <Icon className="h-3.5 w-3.5" /> {cat.name}
                </button>
              );
            })}
          </div>
        </div>

        <div className="mx-auto mt-10 grid max-w-4xl grid-cols-3 gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-3 sm:p-4">
          <div className="rounded-xl bg-white/[0.03] p-4 text-center"><div className="text-2xl font-black text-white">{stats.total}</div><div className="mt-1 text-[10px] uppercase tracking-widest text-slate-500">Tool profiles</div></div>
          <div className="rounded-xl bg-white/[0.03] p-4 text-center"><div className="text-2xl font-black text-violet-300">{stats.categoriesCount}</div><div className="mt-1 text-[10px] uppercase tracking-widest text-slate-500">Categories</div></div>
          <div className="rounded-xl bg-white/[0.03] p-4 text-center"><div className="text-2xl font-black text-cyan-300">{stats.verified}</div><div className="mt-1 text-[10px] uppercase tracking-widest text-slate-500">Verified affiliate paths</div></div>
        </div>
      </header>

      {featuredTools.length > 0 && (
        <section className="relative z-10 mx-auto max-w-7xl px-4 pb-14 sm:px-6 lg:px-8">
          <div className="mb-5 flex items-end justify-between gap-4">
            <div><div className="text-xs font-bold uppercase tracking-[0.2em] text-violet-300">Popular starting points</div><h2 className="mt-2 text-2xl font-black text-white sm:text-3xl">Start with tools buyers compare often</h2></div>
            <a href="#directory" className="hidden items-center gap-1 text-sm font-semibold text-slate-400 hover:text-white sm:flex">View all <ArrowRight className="h-4 w-4" /></a>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {featuredTools.map((tool) => (
              <a key={tool.id} href={`/tool/${tool.id}.html`} className="group flex items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.035] p-4 transition hover:-translate-y-0.5 hover:border-violet-400/30 hover:bg-white/[0.055]">
                <div className="h-12 w-12 overflow-hidden rounded-xl border border-white/10"><ToolLogo tool={tool} /></div>
                <div className="min-w-0 flex-1"><div className="font-bold text-white group-hover:text-violet-200">{tool.name}</div><div className="truncate text-xs text-slate-500">{tool.category_display} · {tool.pricing}</div></div>
                <ArrowUpRight className="h-4 w-4 text-slate-600 group-hover:text-violet-300" />
              </a>
            ))}
          </div>
        </section>
      )}

      <main id="directory" className="relative z-10 mx-auto max-w-7xl scroll-mt-24 px-4 pb-24 sm:px-6 lg:px-8">
        <section className="mb-6 rounded-2xl border border-white/10 bg-white/[0.035] p-4 sm:p-5">
          <div className="mb-4 flex flex-wrap gap-2">
            {categories.map((cat) => {
              const Icon = cat.icon;
              const active = selectedCategory === cat.id;
              return (
                <button key={cat.id} onClick={() => setSelectedCategory(cat.id)} className={`inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold transition ${active ? 'bg-white text-slate-950' : 'border border-white/10 bg-white/[0.02] text-slate-400 hover:text-white'}`}>
                  <Icon className="h-3.5 w-3.5" /> {cat.name}
                </button>
              );
            })}
          </div>
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              {pricingOptions.map((opt) => (
                <button key={opt.id} onClick={() => setSelectedPricing(opt.id)} className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${selectedPricing === opt.id ? 'bg-violet-500 text-white' : 'bg-white/5 text-slate-400 hover:text-white'}`}>{opt.name}</button>
              ))}
              <button onClick={() => setShowBookmarksOnly(!showBookmarksOnly)} className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold ${showBookmarksOnly ? 'bg-rose-500/20 text-rose-200' : 'bg-white/5 text-slate-400 hover:text-white'}`}><Heart className={`h-3.5 w-3.5 ${showBookmarksOnly ? 'fill-current' : ''}`} /> Saved ({bookmarkedIds.length})</button>
            </div>
            <div className="text-xs text-slate-500">Showing <span className="font-bold text-slate-300">{filteredTools.length}</span> matching tools</div>
          </div>
        </section>

        {filteredTools.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredTools.map((tool) => {
              const validUrl = getValidExternalUrl(tool);
              return (
                <article key={tool.id} className="group flex flex-col rounded-2xl border border-white/10 bg-[#101218] p-5 transition hover:-translate-y-1 hover:border-violet-400/30 hover:shadow-2xl hover:shadow-violet-950/10">
                  <div className="flex items-start gap-3">
                    <div className="h-12 w-12 shrink-0 overflow-hidden rounded-xl border border-white/10"><ToolLogo tool={tool} /></div>
                    <div className="min-w-0 flex-1"><a href={`/tool/${tool.id}.html`} className="block truncate text-lg font-black text-white hover:text-violet-200">{tool.name}</a><div className="mt-1 text-[10px] font-bold uppercase tracking-widest text-violet-300">{tool.category_display}</div></div>
                    <button onClick={() => toggleBookmark(tool.id)} title="Save tool" className={`rounded-lg border p-2 ${bookmarkedIds.includes(tool.id) ? 'border-rose-400/30 bg-rose-400/10 text-rose-300' : 'border-white/10 text-slate-600 hover:text-white'}`}><Heart className={`h-4 w-4 ${bookmarkedIds.includes(tool.id) ? 'fill-current' : ''}`} /></button>
                  </div>

                  <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-400">{tool.description}</p>
                  <div className="mt-4 flex flex-wrap gap-1.5">{(tool.key_features || []).slice(0, 3).map((feature) => <span key={feature} className="rounded-lg border border-white/10 bg-white/[0.03] px-2 py-1 text-[11px] text-slate-400">{feature}</span>)}</div>

                  <div className="mt-5 grid grid-cols-2 gap-2 rounded-xl bg-white/[0.025] p-3">
                    <div><div className="text-[10px] uppercase tracking-wider text-slate-600">Pricing</div><div className="mt-0.5 text-sm font-bold text-slate-200">{tool.pricing}</div></div>
                    <div className="text-right"><div className="text-[10px] uppercase tracking-wider text-slate-600">Rating</div><div className="mt-0.5 inline-flex items-center gap-1 text-sm font-bold text-slate-200">{tool.rating != null && tool.rating_source_url ? <><Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" /> {tool.rating}</> : 'Source-led'}</div></div>
                  </div>

                  <div className="mt-auto pt-4">
                    <div className="mb-2 grid grid-cols-[1fr_auto] gap-2">
                      <a href={`/tool/${tool.id}.html`} className="flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-xs font-bold text-slate-200 hover:bg-white/10">See buyer guide</a>
                      <button onClick={() => setCompareToolA(tool)} className="flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-3 text-slate-400 hover:text-white" title="Compare side-by-side"><Scale className="h-4 w-4" /></button>
                    </div>
                    {validUrl ? (
                      <a href={validUrl} target="_blank" rel={tool.affiliate_verified === true ? 'sponsored noopener noreferrer' : 'noopener noreferrer'} onClick={() => trackToolClick(tool.id, tool.name, validUrl, tool.affiliate_verified === true)} className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-indigo-500 px-4 py-3 text-sm font-black text-white shadow-lg shadow-violet-950/20 hover:from-violet-400 hover:to-indigo-400">
                        {tool.affiliate_verified === true ? 'Check verified offer' : 'Visit official site'} <ArrowUpRight className="h-4 w-4" />
                      </a>
                    ) : (
                      <div className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-center text-xs font-bold text-slate-600">Official link unavailable</div>
                    )}
                    {tool.affiliate_verified === true && <div className="mt-2 flex items-center justify-center gap-1 text-[10px] text-slate-600"><CheckCircle2 className="h-3 w-3" /> Affiliate link verified in our records · disclosure applies</div>}
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] py-20 text-center"><Search className="mx-auto h-10 w-10 text-slate-700" /><h3 className="mt-4 text-lg font-bold text-white">No matching tools</h3><p className="mt-2 text-sm text-slate-500">Try a broader search, another category or a different price filter.</p></div>
        )}

        <section className="mt-20 grid gap-4 lg:grid-cols-3">
          {[['Source-led pricing', 'We separate official pricing checks from affiliate destinations so shoppers can verify before buying.'], ['Buyer-first comparisons', 'Guides focus on who each product fits, what it costs and the trade-offs that matter before checkout.'], ['Clear affiliate disclosure', 'Some links may earn COSHUMA a commission. That never changes the price you pay.']].map(([title, text], idx) => <div key={title} className="rounded-2xl border border-white/10 bg-white/[0.025] p-5"><div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-violet-400/10 text-violet-300">{idx === 0 ? <Award className="h-4 w-4" /> : idx === 1 ? <ShieldCheck className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}</div><h3 className="font-black text-white">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-500">{text}</p></div>)}
        </section>

        <section id="submit" className="mt-20 overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#141620] to-[#0d0f15] p-8 sm:p-10">
          <div className="max-w-2xl"><div className="text-xs font-bold uppercase tracking-[0.2em] text-violet-300">For software companies</div><h2 className="mt-3 text-3xl font-black text-white">Reach buyers already comparing software</h2><p className="mt-3 text-slate-400">COSHUMA supports clearly disclosed sponsorship and independent software discovery. Sponsored placement does not guarantee a positive recommendation.</p>{paymentConfig.checkoutEnabled && <div className="mt-7"><SponsorshipCheckout /></div>}</div>
        </section>
      </main>

      <footer className="relative z-10 border-t border-white/10 bg-[#06070a] py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center"><div><div className="font-black text-white">COSHUMA</div><p className="mt-1 max-w-xl text-xs leading-5 text-slate-600">Independent AI & SaaS decision guides. Pricing, trial details and outbound links can change, so verify final terms on the vendor site before purchasing.</p></div><div className="flex flex-wrap gap-5 text-xs"><a href="/privacy.html" className="text-slate-500 hover:text-white">Privacy</a><a href="/terms.html" className="text-slate-500 hover:text-white">Terms</a><a href="/sponsorship.html" className="text-slate-500 hover:text-white">Sponsorship</a><a href="/refund.html" className="text-slate-500 hover:text-white">Refunds</a></div></div>
          <div className="mt-7 border-t border-white/5 pt-6 text-[11px] text-slate-700">© {new Date().getFullYear()} COSHUMA. Independent software decision support.</div>
        </div>
      </footer>

      {compareToolA && <CompareModal toolA={compareToolA} allTools={toolsData} onClose={() => setCompareToolA(null)} />}
    </div>
  );
}
