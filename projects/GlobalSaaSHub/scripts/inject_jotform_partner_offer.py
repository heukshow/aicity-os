from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
PAGE = PROJECT / "public" / "tool" / "jotform.html"
AFFILIATE_URL = "https://link.jotform.com/17STYVOunG?username=AnSangkwon"

html = PAGE.read_text(encoding="utf-8")

if AFFILIATE_URL in html:
    print("Jotform AI affiliate CTA already present")
    raise SystemExit(0)

pattern = re.compile(
    r'(?P<anchor><a data-cta="official" href="https://www\.jotform\.com/"[^>]*>.*?</a>)',
    re.DOTALL,
)
match = pattern.search(html)
if not match:
    raise SystemExit("Could not locate the Jotform official CTA anchor; refusing to guess an insertion point")

replacement = f'''<div class="flex flex-col sm:flex-row gap-3">
            <a data-cta="affiliate" href="{AFFILIATE_URL}" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center border border-purple-500 hover:bg-purple-500 transition-all flex items-center justify-center gap-2"><span>Try Jotform AI Agents</span><span>→</span></a>
            {match.group("anchor")}
          </div>
          <p data-affiliate-disclosure="jotform-ai" class="mt-3 text-[11px] leading-relaxed text-slate-400">Affiliate disclosure: COSHUMA may earn a commission if you sign up through the Jotform AI Agents link. The standard Jotform site button remains a non-affiliate official link.</p>'''

html = html[: match.start()] + replacement + html[match.end() :]
PAGE.write_text(html, encoding="utf-8")
print("Injected verified Jotform AI affiliate CTA")
