"""
GlobalSaaSHub - Programmatic SEO Generator Script
=================================================
Generates individual SEO HTML pages for each AI tool in tools.json
and generates an updated sitemap.xml with all individual tool URLs.
"""
import sys
import os
import json
import re
import argparse
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEXT_JSON = os.path.join(PROJECT_DIR, "data", "tools.next.json")
TOOLS_JSON = os.path.join(PROJECT_DIR, "data", "tools.json")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--source",
    choices=("auto", "tools.json", "tools.next.json"),
    default="auto",
    help="Dataset to generate from; auto preserves the pipeline's candidate-first behavior.",
)
args = parser.parse_args()
if args.source == "tools.json":
    TOOLS_JSON_PATH = TOOLS_JSON
elif args.source == "tools.next.json":
    TOOLS_JSON_PATH = NEXT_JSON
else:
    TOOLS_JSON_PATH = NEXT_JSON if os.path.exists(NEXT_JSON) else TOOLS_JSON

print(f"generate_seo_pages.py reading dataset from: {TOOLS_JSON_PATH}")

PUBLIC_DIR = os.path.join(PROJECT_DIR, "public")
TOOL_PAGES_DIR = os.path.join(PUBLIC_DIR, "tool")

last_updated_date = datetime.utcnow().strftime("%B %d, %Y") # e.g. July 27, 2026



if os.path.exists(TOOL_PAGES_DIR):
    import shutil
    shutil.rmtree(TOOL_PAGES_DIR)
os.makedirs(TOOL_PAGES_DIR, exist_ok=True)


with open(TOOLS_JSON_PATH, "r", encoding="utf-8") as f:
    tools_data = json.load(f)

def canonical_slug(tool):
    """The immutable tools.json id is the sole canonical tool-page slug."""
    slug = tool.get("id")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError(f"Invalid canonical tool id: {slug!r}")
    return slug

def remove_stale_tool_pages(public_dir, canonical_ids):
    """Remove generated detail pages that no longer map to a dataset ID."""
    tool_dir = os.path.join(public_dir, "tool")
    os.makedirs(tool_dir, exist_ok=True)
    canonical_files = {f"{tool_id}.html" for tool_id in canonical_ids}
    removed = []
    for filename in os.listdir(tool_dir):
        path = os.path.join(tool_dir, filename)
        if os.path.isfile(path) and filename.endswith(".html") and filename not in canonical_files:
            os.remove(path)
            removed.append(filename)
    return sorted(removed)

html_template = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name} Pricing, Features & Review (2026) | GlobalSaaSHub</title>
    <meta name="description" content="{description_short} Discover features, pricing ({pricing}), {rating_meta}and official links for {name} on GlobalSaaSHub." />
    <link rel="canonical" href="https://coshuma.com/tool/{slug}.html" />
    
    <!-- Open Graph SEO Tags -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://coshuma.com/tool/{slug}.html" />
    <meta property="og:title" content="{name} Review & Pricing (2026) | GlobalSaaSHub" />
    <meta property="og:description" content="{description_short} Check rating, pricing, and features." />

    <!-- JSON-LD Structured Data for Google Indexing -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "{name}",
      "operatingSystem": "Web",
      "applicationCategory": "{category_display}",
      "description": "{description_escaped}"
    }}
    </script>

    <!-- Tailwind & Fonts -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
      body {{ font-family: 'Inter', sans-serif; background-color: #0b0c10; color: #f1f5f9; }}
      h1, h2, h3 {{ font-family: 'Outfit', sans-serif; }}
    </style>
  </head>
  <body class="min-h-screen flex flex-col justify-between">
    <!-- Header Navigation -->
    <header class="border-b border-[#222538] bg-[#07080c]/80 backdrop-blur-md sticky top-0 z-50 py-4 px-6">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <a href="/" class="flex items-center gap-3">
          <div class="h-8 w-8 rounded-lg bg-purple-600 flex items-center justify-center font-extrabold text-white text-lg">G</div>
          <span class="font-extrabold text-lg tracking-tight text-white">GlobalSaaSHub</span>
        </a>
        <a href="/" class="text-xs font-bold px-4 py-2 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 hover:bg-purple-500/20 transition-all">
          ← Back to All Tools
        </a>
      </div>
    </header>

    <!-- Tool Detail Hero Section -->
    <main class="max-w-4xl mx-auto px-4 py-12 w-full">
      <div class="p-8 rounded-3xl bg-[#131520] border border-[#222538] shadow-2xl space-y-8">
        
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border-b border-[#222538] pb-6">
          <div class="flex items-center gap-5">
            <img src="{logo_url}" alt="{name} logo" class="h-16 w-16 rounded-2xl border border-[#222538] bg-slate-900 object-contain p-2" onError="this.onerror=null;this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚀</text></svg>'" />
            <div>
              <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-purple-500/10 border border-purple-500/20 text-purple-300 mb-2">
                <span>{category_display}</span>
              </div>
              <h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">{name}</h1>
            </div>
          </div>

          <div class="flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 text-amber-400 px-4 py-2 rounded-xl text-sm font-bold">
            <span>{rating}</span>
          </div>
        </div>

        <!-- Description -->
        <div class="space-y-3">
          <h2 class="text-xl font-bold text-white">Overview</h2>
          <p class="text-slate-300 text-base leading-relaxed">{description}</p>
        </div>

        <!-- Key Features -->
        <div class="space-y-4">
          <h2 class="text-xl font-bold text-white">Key Features & Capabilities</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {features_html}
          </div>
        </div>

        <!-- Pros & Cons Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 space-y-2">
            <h3 class="text-sm font-bold text-emerald-400 flex items-center gap-2">👍 Key Advantages (Pros)</h3>
            <ul class="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
              {rating_pro}
              <li>Flexible pricing structure ({pricing})</li>
              <li>Seamless workflow integration & API support</li>
            </ul>
          </div>

          <div class="p-5 rounded-2xl bg-rose-500/5 border border-rose-500/20 space-y-2">
            <h3 class="text-sm font-bold text-rose-400 flex items-center gap-2">⚠️ Considerations (Cons)</h3>
            <ul class="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
              <li>Requires active internet connection</li>
              <li>Advanced features require premium tier subscription</li>
            </ul>
          </div>
        </div>

        <!-- Alternatives & Direct Competitors Section -->
        <div class="space-y-4 pt-4 border-t border-[#222538]">
          <h2 class="text-xl font-bold text-white flex items-center justify-between">
            <span>Top Alternatives to {name}</span>
            <span class="text-xs font-semibold text-purple-400">Compare Alternatives</span>
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {alternatives_html}
          </div>
        </div>

        <!-- Pricing & Action -->
        <div class="p-6 rounded-2xl bg-[#181a29] border border-[#222538] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="text-xs uppercase font-bold text-slate-400 tracking-wider">Pricing Plan</div>
            <div class="text-xl font-extrabold text-emerald-400 mt-0.5">{pricing}</div>
          </div>
          {cta_button_html}
        </div>

        <!-- Claim Profile & Official Founder Badge Section -->
        <div class="p-6 rounded-2xl bg-[#181a29]/80 border border-purple-500/30 space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 text-purple-300 font-bold text-sm">
              <span>🏆 Are you the founder of {name}?</span>
            </div>
            <span class="text-[10px] uppercase tracking-wider font-extrabold bg-purple-500/20 text-purple-300 px-2.5 py-0.5 rounded-full border border-purple-500/30">Founder Verification</span>
          </div>
          <p class="text-xs text-slate-400 leading-relaxed">
            Claim this official profile to update tool information, manage pricing details, and embed the verified rating badge on your website:
          </p>
          <div class="p-3 rounded-xl bg-[#0b0c10] border border-[#222538] text-[11px] text-slate-400 font-mono">
            ⚖️ <strong class="text-slate-300">Editorial Independence Disclosure:</strong> Claiming a profile or purchasing sponsorship does not guarantee or alter editorial ratings or ranking positions.
          </div>
          <div class="flex flex-col sm:flex-row items-center gap-3">
            <a href="/#submit" class="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs text-center transition-all shadow-md">
              ⚡ Claim {name} Profile ($49/yr)
            </a>
          </div>
          <div class="relative pt-2">
            <div class="text-[10px] font-bold text-slate-400 mb-1">Official Embed Badge Code:</div>
            <textarea readonly class="w-full bg-[#0b0c10] border border-[#222538] text-[11px] font-mono text-slate-300 p-3 rounded-xl focus:outline-none resize-none h-16">&lt;a href="https://coshuma.com/tool/{slug}.html" target="_blank" title="Featured on GlobalSaaSHub TOP AI"&gt;&lt;img src="https://coshuma.com/assets/verified-badge.svg" alt="{name} Verified on GlobalSaaSHub" width="200" /&gt;&lt;/a&gt;</textarea>
          </div>
        </div>


      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-[#222538] bg-[#07080c] py-8 text-center text-xs text-slate-500">
      <div class="max-w-6xl mx-auto px-4">
        &copy; 2026 GlobalSaaSHub. Global AI SaaS Decision Platform. All rights reserved.
      </div>
    </footer>
  </body>
</html>

"""

sitemap_urls = [
    """  <url>
    <loc>https://coshuma.com/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""
]

generated_count = 0

canonical_ids = [canonical_slug(tool) for tool in tools_data]
if len(canonical_ids) != len(set(canonical_ids)):
    raise ValueError("Duplicate canonical tool ids in selected dataset")
removed_stale_pages = remove_stale_tool_pages(PUBLIC_DIR, canonical_ids)
if removed_stale_pages:
    print(f"Removed {len(removed_stale_pages)} stale tool pages: {', '.join(removed_stale_pages)}")

for tool in tools_data:
    slug = canonical_slug(tool)
    
    features_list = tool.get("key_features", [])
    features_html = "\n".join([
        f'<div class="flex items-center gap-2.5 p-3 rounded-xl bg-[#131520] border border-[#222538] text-sm text-slate-200"><span class="text-purple-400 font-bold">✓</span> {f}</div>'
        for f in features_list
    ])
    
    desc = tool.get("description", "")
    desc_short = desc[:150].replace('"', '&quot;') + "..."
    desc_escaped = desc.replace('"', '\\"').replace('\n', ' ')

    # Generate dynamic alternatives html (3 same comparison_group competitors)
    group_cur = tool.get("comparison_group") or tool.get("category")
    same_group_comp = [t for t in tools_data if t.get("id") != tool.get("id") and t.get("comparison_group") == group_cur]
    if not same_group_comp:
        same_group_comp = [t for t in tools_data if t.get("id") != tool.get("id") and t.get("category") == tool.get("category")]
    
    comp_tools = same_group_comp[:3]

    alternatives_html = "\n".join([
        f'<a href="/tool/{canonical_slug(c)}.html" class="p-3.5 rounded-xl bg-[#181a29] border border-[#222538] hover:border-purple-500/40 transition-all flex items-center justify-between group">'
        f'<div class="flex items-center gap-2.5">'
        f'<img src="{c.get("logo_url")}" class="h-6 w-6 rounded object-contain p-0.5 bg-slate-900 border border-[#222538]" onError="this.style.display=\'none\'"/>'
        f'<span class="text-xs font-bold text-slate-200 group-hover:text-purple-300">{c.get("name")}</span>'
        f'</div>'
        f'<span class="text-[10px] font-extrabold text-emerald-400">{c.get("pricing")}</span>'
        f'</a>'
        for c in comp_tools
    ])


    r_val = tool.get("rating")
    if r_val is not None and tool.get("rating_source_url"):
        rating_badge = f'⭐ {r_val} / 5.0 Rating'
        rating_meta = f'rating ({r_val}/5.0), '
        rating_pro = f'<li>Editorial rating ({r_val}/5.0)</li>'
    else:
        rating_badge = 'Not yet editorially rated'
        rating_meta = ''
        rating_pro = '<li>Editorial review in progress</li>'

    # Helper to validate and clean HTTP/HTTPS URLs
    def clean_url(url_val):
        if not url_val or not isinstance(url_val, str):
            return None
        u = url_val.strip()
        if not u or u.lower() in ("null", "undefined", "none", "n/a", "#"):
            return None
        if u.startswith("http://") or u.startswith("https://"):
            return u
        return None

    tool_name = tool.get("name", "AI Tool")
    official_url = clean_url(tool.get("official_url"))
    affiliate_url = clean_url(tool.get("affiliate_url")) if tool.get("affiliate_verified") is True else None
    cta_parts = []
    if official_url:
        cta_parts.append(f'<a data-cta="official" href="{official_url}" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Official {tool_name} Site</span><span>→</span></a>')
    else:
        cta_parts.append('<div class="px-6 py-3.5 rounded-xl font-bold text-xs bg-slate-800 text-slate-500 border border-slate-700/50 text-center">Official Link Unavailable</div>')
    if affiliate_url:
        cta_parts.append(f'<a data-cta="affiliate" href="{affiliate_url}" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-center shadow-lg shadow-purple-950/50 hover:brightness-110 transition-all flex items-center justify-center gap-2"><span>Visit {tool_name} via Verified Affiliate Link</span><span>→</span></a>')
    cta_button_html = "\n".join(cta_parts)

    file_content = html_template.format(
        name=tool.get("name", "AI Tool"),
        slug=slug,
        category_display=tool.get("category_display", "AI & SaaS"),
        description=desc,
        description_short=desc_short,
        description_escaped=desc_escaped,
        pricing=tool.get("pricing", "Pricing on site"),
        rating=rating_badge,
        rating_meta=rating_meta,
        rating_pro=rating_pro,
        logo_url=tool.get("logo_url", ""),
        cta_button_html=cta_button_html,
        features_html=features_html,
        alternatives_html=alternatives_html
    )

    # Sanity check: Ensure generated HTML contains NO invalid hrefs
    invalid_href_matches = re.findall(r'href=["\'](None|null|undefined|#|javascript:|[^\s"\']*javascript:[^\s"\']*)["\']', file_content)
    if invalid_href_matches:
        raise ValueError(f"Generated HTML for '{slug}' contains invalid href string: {invalid_href_matches}")



    file_path = os.path.join(TOOL_PAGES_DIR, f"{slug}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
    
    generated_count += 1
    sitemap_urls.append(f"""  <url>
    <loc>https://coshuma.com/tool/{slug}.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

# Create public/compare directory for static compare SEO pages and clean old files
COMPARE_PAGES_DIR = os.path.join(PUBLIC_DIR, "compare")
if os.path.exists(COMPARE_PAGES_DIR):
    import shutil
    shutil.rmtree(COMPARE_PAGES_DIR)
os.makedirs(COMPARE_PAGES_DIR, exist_ok=True)



compare_template = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{toolA_name} vs {toolB_name} Comparison, Pricing & Winner (2026) | GlobalSaaSHub</title>
    <meta name="description" content="In-depth side-by-side comparison of {toolA_name} vs {toolB_name}. Compare pricing, features, ratings ({toolA_rating_badge} vs {toolB_rating_badge}), and find out which AI tool is best for your workflow." />

    <link rel="canonical" href="https://coshuma.com/compare/{slug_a}-vs-{slug_b}.html" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="https://coshuma.com/compare/{slug_a}-vs-{slug_b}.html" />
    <meta property="og:title" content="{toolA_name} vs {toolB_name} Comparison (2026) | GlobalSaaSHub" />
    <meta property="og:description" content="Compare {toolA_name} and {toolB_name} by pricing, features, and verified public information." />

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": {comparison_name_json},
      "url": "https://coshuma.com/compare/{slug_a}-vs-{slug_b}.html",
      "description": {comparison_description_json},
      "isPartOf": {{
        "@type": "WebSite",
        "name": "GlobalSaaSHub",
        "url": "https://coshuma.com/"
      }},
      "about": [
        {{"@type": "SoftwareApplication", "name": {toolA_name_json}, "url": "https://coshuma.com/tool/{slug_a}.html"}},
        {{"@type": "SoftwareApplication", "name": {toolB_name_json}, "url": "https://coshuma.com/tool/{slug_b}.html"}}
      ]
    }}
    </script>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
      body {{ font-family: 'Inter', sans-serif; background-color: #0b0c10; color: #f1f5f9; }}
      h1, h2, h3 {{ font-family: 'Outfit', sans-serif; }}
    </style>
  </head>
  <body class="min-h-screen flex flex-col justify-between">
    <header class="border-b border-[#222538] bg-[#07080c]/80 backdrop-blur-md sticky top-0 z-50 py-4 px-6">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <a href="/" class="flex items-center gap-3">
          <div class="h-8 w-8 rounded-lg bg-purple-600 flex items-center justify-center font-extrabold text-white text-lg">G</div>
          <span class="font-extrabold text-lg tracking-tight text-white">GlobalSaaSHub</span>
        </a>
        <a href="/" class="text-xs font-bold px-4 py-2 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 hover:bg-purple-500/20 transition-all">
          ← Back to All Tools
        </a>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-12 w-full space-y-8">
      <div class="text-center space-y-3">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-purple-500/10 border border-purple-500/20 text-purple-300">
          ⚖️ Side-by-Side Head-to-Head Comparison
        </div>
        <h1 class="text-3xl md:text-5xl font-black text-white tracking-tight">{toolA_name} vs {toolB_name}</h1>
        <p class="text-slate-400 text-sm max-w-2xl mx-auto">
          Detailed breakdown of pricing, ratings, core capabilities, and decision recommendations to help you choose the best {category_display} tool.
        </p>
      </div>

      <!-- Decision Summary & Verification Transparency Box -->
      <div class="p-6 rounded-3xl bg-[#131520] border border-purple-500/30 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <span>🧠 Decision Summary & Evidence</span>
          </h2>
          <span class="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-md">
            ✓ Publicly Available Data (Last updated: {last_updated_date})
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div class="p-4 rounded-2xl bg-[#181a29] border border-purple-500/20 space-y-2">
            <div class="font-bold text-purple-300">Choose {toolA_name} if:</div>
            <p class="text-slate-300 leading-relaxed">
              You prioritize {toolA_rating_badge}, specialized feature set, and reliable industry workflow integration.
            </p>
            <div class="text-[10px] text-slate-400 font-mono pt-1 border-t border-[#222538]">
              Source: Official Documentation & Public Pricing Specs ({last_updated_date})
            </div>
          </div>
          <div class="p-4 rounded-2xl bg-[#181a29] border border-blue-500/20 space-y-2">
            <div class="font-bold text-blue-300">Choose {toolB_name} if:</div>
            <p class="text-slate-300 leading-relaxed">
              You want an alternative approach with {toolB_pricing} pricing structure and {toolB_rating_badge}.
            </p>
            <div class="text-[10px] text-slate-400 font-mono pt-1 border-t border-[#222538]">
              Source: Official Vendor Specifications & Benchmark Data ({last_updated_date})
            </div>
          </div>
        </div>
      </div>



      <!-- 2-Column Comparison Table -->
      <div class="p-6 rounded-3xl bg-[#131520] border border-[#222538] space-y-6">
        <h2 class="text-xl font-bold text-white">Side-by-Side Comparison</h2>
        
        <div class="grid grid-cols-2 gap-4 text-center">
          <div class="p-4 rounded-2xl bg-[#181a29] border border-purple-500/30 font-bold text-white text-base">
            <a href="/tool/{slug_a}.html" class="hover:text-purple-300">{toolA_name}</a>
          </div>
          <div class="p-4 rounded-2xl bg-[#181a29] border border-blue-500/30 font-bold text-white text-base">
            <a href="/tool/{slug_b}.html" class="hover:text-blue-300">{toolB_name}</a>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 p-4 rounded-2xl bg-[#181a29]/60 border border-[#222538] text-center">
          <div>
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">GlobalSaaSHub Editorial Rating</div>
            <div class="text-lg font-black text-amber-400">{toolA_rating_badge}</div>
          </div>
          <div>
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">GlobalSaaSHub Editorial Rating</div>
            <div class="text-lg font-black text-amber-400">{toolB_rating_badge}</div>
          </div>
        </div>



        <div class="grid grid-cols-2 gap-4 p-4 rounded-2xl bg-[#181a29]/60 border border-[#222538] text-center">
          <div>
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Pricing Plan</div>
            <div class="text-base font-extrabold text-emerald-400">{toolA_pricing}</div>
          </div>
          <div>
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Pricing Plan</div>
            <div class="text-base font-extrabold text-emerald-400">{toolB_pricing}</div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 p-4 rounded-2xl bg-[#181a29]/60 border border-[#222538]">
          <div>
            <div class="text-[10px] font-bold text-purple-300 uppercase tracking-wider mb-2 text-center">{toolA_name} Features</div>
            <div class="space-y-1.5 text-xs text-slate-300">
              {toolA_features}
            </div>
          </div>
          <div>
            <div class="text-[10px] font-bold text-blue-300 uppercase tracking-wider mb-2 text-center">{toolB_name} Features</div>
            <div class="space-y-1.5 text-xs text-slate-300">
              {toolB_features}
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 pt-2">
          {toolA_cta_html}
          {toolB_cta_html}
        </div>
      </div>
    </main>

    <footer class="border-t border-[#222538] bg-[#07080c] py-8 text-center text-xs text-slate-500">
      <div class="max-w-6xl mx-auto px-4">
        &copy; 2026 GlobalSaaSHub. Programmatic Compare Engine. All rights reserved.
      </div>
    </footer>
  </body>
</html>
"""

# Generate static /compare/ pages for same comparison_group competitors (Unordered Pair Deduplicated)
compare_generated_count = 0
generated_compare_pairs = set()
generated_compare_files = set()

for tool_a in tools_data:
    slug_a = canonical_slug(tool_a)
    group_a = tool_a.get("comparison_group") or tool_a.get("category")
    same_group = [t for t in tools_data if t.get("id") != tool_a.get("id") and t.get("comparison_group") == group_a]
    
    for tool_b in same_group[:2]: # Top 2 direct competitors
        slug_b = canonical_slug(tool_b)
        
        pair_key = tuple(sorted([slug_a, slug_b]))
        if pair_key in generated_compare_pairs:
            continue
        generated_compare_pairs.add(pair_key)



        
        feat_a = "\n".join([f'<div>✓ {f}</div>' for f in tool_a.get("key_features", [])])
        feat_b = "\n".join([f'<div>✓ {f}</div>' for f in tool_b.get("key_features", [])])
        
        r_a = tool_a.get("rating") if tool_a.get("rating_source_url") else None
        r_b = tool_b.get("rating") if tool_b.get("rating_source_url") else None
        rating_a_disp = f"⭐ {r_a} / 5.0" if r_a is not None else "Not rated"
        rating_b_disp = f"⭐ {r_b} / 5.0" if r_b is not None else "Not rated"

        target_a_affiliate = clean_url(tool_a.get("affiliate_url")) if tool_a.get("affiliate_verified") is True else None
        target_b_affiliate = clean_url(tool_b.get("affiliate_url")) if tool_b.get("affiliate_verified") is True else None
        target_a_url = target_a_affiliate or clean_url(tool_a.get("official_url"))
        target_b_url = target_b_affiliate or clean_url(tool_b.get("official_url"))
        target_a_rel = "sponsored noopener noreferrer" if target_a_affiliate else "noopener noreferrer"
        target_b_rel = "sponsored noopener noreferrer" if target_b_affiliate else "noopener noreferrer"

        if target_a_url:
            cta_a_html = f'<a href="{target_a_url}" target="_blank" rel="{target_a_rel}" class="py-3.5 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 font-extrabold text-xs text-white text-center shadow-lg transition-all">Get {tool_a.get("name")} →</a>'
        else:
            cta_a_html = '<div class="py-3.5 px-4 rounded-xl bg-slate-800 text-slate-500 font-bold text-xs text-center border border-slate-700/50">Link Unavailable</div>'

        if target_b_url:
            cta_b_html = f'<a href="{target_b_url}" target="_blank" rel="{target_b_rel}" class="py-3.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 font-extrabold text-xs text-white text-center shadow-lg transition-all">Get {tool_b.get("name")} →</a>'
        else:
            cta_b_html = '<div class="py-3.5 px-4 rounded-xl bg-slate-800 text-slate-500 font-bold text-xs text-center border border-slate-700/50">Link Unavailable</div>'

        comp_content = compare_template.format(
            toolA_name=tool_a.get("name"),
            toolB_name=tool_b.get("name"),
            slug_a=slug_a,
            slug_b=slug_b,
            category_display=tool_a.get("category_display", "AI & SaaS"),
            toolA_rating_badge=rating_a_disp,
            toolB_rating_badge=rating_b_disp,
            toolA_pricing=tool_a.get("pricing", "Free Trial / Paid"),
            toolB_pricing=tool_b.get("pricing", "Free Trial / Paid"),
            toolA_features=feat_a,
            toolB_features=feat_b,
            toolA_cta_html=cta_a_html,
            toolB_cta_html=cta_b_html,
            comparison_name_json=json.dumps(f'{tool_a.get("name")} vs {tool_b.get("name")} Comparison', ensure_ascii=False),
            comparison_description_json=json.dumps(
                f'Compare {tool_a.get("name")} and {tool_b.get("name")} by pricing, features, and verified public information.',
                ensure_ascii=False,
            ),
            toolA_name_json=json.dumps(tool_a.get("name"), ensure_ascii=False),
            toolB_name_json=json.dumps(tool_b.get("name"), ensure_ascii=False),
            last_updated_date=last_updated_date
        )

        # Sanity check: Ensure generated compare HTML contains NO invalid hrefs
        invalid_compare_matches = re.findall(r'href=["\'](None|null|undefined|#|javascript:|[^\s"\']*javascript:[^\s"\']*)["\']', comp_content)
        if invalid_compare_matches:
            raise ValueError(f"Generated compare HTML for '{slug_a}-vs-{slug_b}' contains invalid href string: {invalid_compare_matches}")

        
        comp_filename = f"{slug_a}-vs-{slug_b}.html"
        generated_compare_files.add(comp_filename)
        comp_file_path = os.path.join(COMPARE_PAGES_DIR, comp_filename)
        with open(comp_file_path, "w", encoding="utf-8") as f:
            f.write(comp_content)
        
        compare_generated_count += 1
        sitemap_urls.append(f"""  <url>
    <loc>https://coshuma.com/compare/{slug_a}-vs-{slug_b}.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""")

stale_compare_pages = []
for filename in os.listdir(COMPARE_PAGES_DIR):
    path = os.path.join(COMPARE_PAGES_DIR, filename)
    if os.path.isfile(path) and filename.endswith(".html") and filename not in generated_compare_files:
        os.remove(path)
        stale_compare_pages.append(filename)
if stale_compare_pages:
    print(f"Removed {len(stale_compare_pages)} stale compare pages: {', '.join(sorted(stale_compare_pages))}")

# Write updated sitemap.xml
sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(sitemap_urls) + '\n</urlset>\n'
sitemap_path = os.path.join(PUBLIC_DIR, "sitemap.xml")
with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write(sitemap_content)

print(f"✅ Successfully generated {generated_count} tool pages and {compare_generated_count} static compare pages (/compare/)! Updated sitemap.xml to {len(sitemap_urls)} URLs!")

