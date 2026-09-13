"""Add fast client-side discovery to the verified-offers revenue hub.

The buyer hub now contains many vendor-verified customer routes. This patch reduces
choice friction without changing affiliate destinations, pricing claims, ranking,
or revenue state. It only filters offer cards already present in the final page.
"""
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_VERIFIED_OFFER_SEARCH_V1 -->"
HUB_DESCRIPTION = (
    "Compare verified SaaS free trials and partner offers across AI, CRM, email, forms, "
    "video and sales tools, with pricing context and disclosed referral links."
)
HUB_OG_DESCRIPTION = (
    "Compare low-risk SaaS trials and verified COSHUMA partner routes across AI, CRM, "
    "email, forms, video and sales tools before you subscribe."
)

SEARCH_PANEL = r'''<!-- COSHUMA_VERIFIED_OFFER_SEARCH_V1 -->
    <section data-offer-search-panel class="rounded-3xl border border-cyan-400/20 bg-[#11131a] p-6 md:p-7" aria-labelledby="verified-offer-search-heading">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <div class="text-xs font-black uppercase tracking-[0.18em] text-cyan-300">Find the right verified route</div>
          <h2 id="verified-offer-search-heading" class="mt-2 text-2xl font-black text-white md:text-3xl">Filter by tool, use case or trial condition</h2>
          <p class="mt-2 text-sm leading-6 text-slate-400">Search only narrows the verified offers already on this page. Affiliate destinations, vendor terms and revenue evidence are not changed. Filters can be shared with the page URL.</p>
        </div>
        <div class="w-full lg:max-w-xl">
          <label for="verified-offer-search" class="sr-only">Search verified software offers</label>
          <div class="flex gap-2">
            <input id="verified-offer-search" type="search" autocomplete="off" inputmode="search" placeholder="Try: no card, free plan, CRM, email, video..." class="min-h-12 w-full rounded-xl border border-white/10 bg-[#090b10] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-400/60 focus:ring-2 focus:ring-cyan-400/20" />
            <button id="verified-offer-reset" type="button" class="min-h-12 shrink-0 rounded-xl border border-white/10 px-4 py-3 text-sm font-bold text-slate-300 hover:bg-white/5">Reset</button>
          </div>
          <div class="mt-3 flex flex-wrap gap-2" aria-label="Quick filters">
            <button type="button" data-offer-query="no card" class="rounded-full border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-cyan-400/30 hover:text-white">No card</button>
            <button type="button" data-offer-query="free" class="rounded-full border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-cyan-400/30 hover:text-white">Free</button>
            <button type="button" data-offer-query="trial" class="rounded-full border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-cyan-400/30 hover:text-white">Trial</button>
            <button type="button" data-offer-query="AI" class="rounded-full border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-cyan-400/30 hover:text-white">AI</button>
            <button type="button" data-offer-query="CRM" class="rounded-full border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-cyan-400/30 hover:text-white">CRM</button>
            <button type="button" data-offer-query="B2B" class="rounded-full border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-cyan-400/30 hover:text-white">B2B</button>
            <button type="button" data-offer-query="email" class="rounded-full border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-cyan-400/30 hover:text-white">Email</button>
            <button type="button" data-offer-query="video" class="rounded-full border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-cyan-400/30 hover:text-white">Video</button>
          </div>
          <p id="verified-offer-search-status" class="mt-3 text-xs font-bold text-cyan-200" aria-live="polite"></p>
          <p id="verified-offer-no-results" class="mt-2 hidden text-sm text-amber-200">No verified offer on this page matches that search. Reset the filter to see every route.</p>
        </div>
      </div>
    </section>
'''

SEARCH_SCRIPT = r'''  <script>
  (() => {
    const initOfferSearch = () => {
      const input = document.getElementById('verified-offer-search');
      const reset = document.getElementById('verified-offer-reset');
      const status = document.getElementById('verified-offer-search-status');
      const empty = document.getElementById('verified-offer-no-results');
      if (!input || !reset || !status || !empty) return;

      const cards = Array.from(document.querySelectorAll('main article')).filter((card) =>
        card.querySelector('[data-cta="affiliate"]')
      );
      const groups = Array.from(new Set(cards.map((card) => card.closest('section')).filter(Boolean)));
      const searchable = new Map(cards.map((card) => [card, card.textContent.toLowerCase().replace(/\s+/g, ' ')]));
      const pageUrl = new URL(window.location.href);
      const initialOfferQuery = (pageUrl.searchParams.get('offer') || '').trim();
      if (initialOfferQuery) input.value = initialOfferQuery;

      const syncOfferParam = (query) => {
        const url = new URL(window.location.href);
        if (query) url.searchParams.set('offer', query);
        else url.searchParams.delete('offer');
        window.history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
      };

      const apply = ({ syncUrl = true } = {}) => {
        const query = input.value.trim().toLowerCase();
        const tokens = query.split(/\s+/).filter(Boolean);
        let visible = 0;

        for (const card of cards) {
          const text = searchable.get(card) || '';
          const match = tokens.length === 0 || tokens.every((token) => text.includes(token));
          card.hidden = !match;
          if (match) visible += 1;
        }

        for (const section of groups) {
          const sectionCards = cards.filter((card) => card.closest('section') === section);
          section.hidden = tokens.length > 0 && sectionCards.length > 0 && sectionCards.every((card) => card.hidden);
        }

        status.textContent = tokens.length
          ? `${visible} of ${cards.length} verified offers match`
          : `${cards.length} verified offers available`;
        empty.classList.toggle('hidden', visible !== 0 || tokens.length === 0);
        if (syncUrl) syncOfferParam(query);
      };

      input.addEventListener('input', () => apply());
      input.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
          input.value = '';
          apply();
          input.blur();
        }
      });
      reset.addEventListener('click', () => {
        input.value = '';
        apply();
        input.focus();
      });
      document.querySelectorAll('[data-offer-query]').forEach((button) => {
        button.addEventListener('click', () => {
          input.value = button.getAttribute('data-offer-query') || '';
          apply();
          input.focus();
        });
      });

      apply({ syncUrl: false });
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initOfferSearch, { once: true });
    } else {
      initOfferSearch();
    }
  })();
  </script>
'''


def main() -> None:
    if not PAGE.exists():
        raise SystemExit("Verified-offers hub missing; refusing discovery patch")

    html = PAGE.read_text(encoding="utf-8")
    if MARKER not in html:
        main_pos = html.find("<main")
        if main_pos < 0:
            raise SystemExit("Verified-offers main element missing; refusing discovery patch")
        hero_end = html.find("</section>", main_pos)
        if hero_end < 0:
            raise SystemExit("Verified-offers hero section missing; refusing discovery patch")
        hero_end += len("</section>")
        html = html[:hero_end] + "\n\n" + SEARCH_PANEL + html[hero_end:]

    if "initOfferSearch" not in html:
        script_anchor = '  <script defer src="/affiliate-attribution.js"></script>'
        if script_anchor not in html:
            raise SystemExit("Affiliate attribution anchor missing; refusing discovery patch")
        html = html.replace(script_anchor, SEARCH_SCRIPT + script_anchor, 1)
    else:
        # Replace the generated discovery panel/script on repeat builds so filter
        # improvements are durable without touching vendor cards or affiliate URLs.
        panel_pattern = re.compile(r'<!-- COSHUMA_VERIFIED_OFFER_SEARCH_V1 -->.*?</section>', re.S)
        html, panel_count = panel_pattern.subn(SEARCH_PANEL.strip(), html, count=1)
        if panel_count != 1:
            raise SystemExit("Verified-offer search panel missing or duplicated")
        script_pattern = re.compile(r'  <script>\n  \(\(\) => \{\n    const initOfferSearch = \(\) => \{.*?\n  </script>\n', re.S)
        html, script_count = script_pattern.subn(SEARCH_SCRIPT, html, count=1)
        if script_count != 1:
            raise SystemExit("Verified-offer discovery script missing or duplicated")

    # Run after every verified-offer surfacing script so legacy scripts can keep
    # their fail-closed metadata guards while the final production page receives
    # durable search/social copy that does not become stale as vendors are added.
    head, body = html.split("</head>", 1)
    for pattern, replacement in (
        (
            r'<meta name="description" content="[^"]*"\s*/?>',
            f'<meta name="description" content="{escape(HUB_DESCRIPTION)}" />',
        ),
        (
            r'<meta property="og:description" content="[^"]*"\s*/?>',
            f'<meta property="og:description" content="{escape(HUB_OG_DESCRIPTION)}" />',
        ),
    ):
        head, count = re.subn(pattern, lambda _: replacement, head, flags=re.S)
        if count != 1:
            raise SystemExit(f"Verified-offer metadata field missing or duplicated: {pattern}")
    html = head + "</head>" + body

    required = (
        MARKER,
        'id="verified-offer-search"',
        'id="verified-offer-search-status"',
        'data-offer-query="no card"',
        'data-offer-query="free"',
        'data-offer-query="CRM"',
        "searchParams.get('offer')",
        "searchParams.set('offer', query)",
        "initOfferSearch",
        "card.querySelector('[data-cta=\"affiliate\"]')",
        'script defer src="/affiliate-attribution.js"',
        f'<meta name="description" content="{escape(HUB_DESCRIPTION)}"',
        f'<meta property="og:description" content="{escape(HUB_OG_DESCRIPTION)}"',
    )
    for token in required:
        if token not in html:
            raise SystemExit(f"Verified-offer discovery patch lost required token: {token}")

    PAGE.write_text(html, encoding="utf-8")
    print("verified-offer-discovery-search-v3-shareable-intent")


if __name__ == "__main__":
    main()
