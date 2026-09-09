from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "best" / "databox-genie-ai-analyst.html"
VERIFIED_AFFILIATE = "https://databox.com?aff_id=15298659&fp_ref=sangkwon-72c9ec"
MARKER = "<!-- DATABOX_AI_STACK_2026_09_09 -->"

html = PAGE.read_text(encoding="utf-8")

html = html.replace(
    'content="Databox Genie AI Analyst review for 2026: see current pricing, AI credit limits, 130+ integrations, dashboard/report automation, free-plan limits and the 14-day no-card Growth trial."',
    'content="Databox Genie AI Analyst review for 2026: compare Genie, Databox MCP, AI performance summaries, current pricing, AI credits, 130+ integrations and the 14-day no-card Growth trial."',
)
html = html.replace('"dateModified": "2026-09-05"', '"dateModified": "2026-09-09"')
html = html.replace('AI analytics buyer guide · updated Sep 5, 2026', 'AI analytics buyer guide · updated Sep 9, 2026')

section = f'''\n      {MARKER}\n      <section class="p-7 rounded-3xl bg-[#131520] border border-purple-500/30 space-y-5">\n        <div>\n          <h2 class="text-2xl font-black text-white">Databox AI is broader than Genie</h2>\n          <p class="text-sm text-slate-300 mt-2 leading-relaxed">Databox's current AI stack now spans three buyer-relevant workflows: ask Genie questions inside Databox, connect trusted Databox metrics to external AI tools through MCP, and use AI performance summaries to explain changes without rebuilding the analysis from scratch. That matters if your real goal is not another dashboard, but a reusable data layer for people and AI agents.</p>\n        </div>\n        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">\n          <div class="p-5 rounded-2xl bg-[#181a29] border border-[#222538]">\n            <div class="text-xs font-bold text-purple-300 uppercase tracking-wider">1 · Genie</div>\n            <h3 class="font-bold text-white mt-2">Ask your business data</h3>\n            <p class="text-sm text-slate-400 mt-2 leading-relaxed">Use natural-language questions to investigate performance, compare periods and turn an analysis into dashboards, reports or shareable artifacts.</p>\n            <a class="inline-flex mt-3 text-xs font-bold text-purple-300 underline" href="https://databox.com/ai-analyst" target="_blank" rel="noopener noreferrer">Official Genie page</a>\n          </div>\n          <div class="p-5 rounded-2xl bg-[#181a29] border border-[#222538]">\n            <div class="text-xs font-bold text-purple-300 uppercase tracking-wider">2 · MCP</div>\n            <h3 class="font-bold text-white mt-2">Bring governed metrics into AI tools</h3>\n            <p class="text-sm text-slate-400 mt-2 leading-relaxed">Databox MCP can expose the metrics, definitions and business context already governed in Databox to MCP-compatible tools such as ChatGPT, Claude and n8n. Databox currently says MCP is available during the 14-day trial and on paid plans; free-plan accounts need to upgrade for MCP access.</p>\n            <a class="inline-flex mt-3 text-xs font-bold text-purple-300 underline" href="https://databox.com/mcp" target="_blank" rel="noopener noreferrer">Official MCP page</a>\n          </div>\n          <div class="p-5 rounded-2xl bg-[#181a29] border border-[#222538]">\n            <div class="text-xs font-bold text-purple-300 uppercase tracking-wider">3 · AI summaries</div>\n            <h3 class="font-bold text-white mt-2">Explain what changed</h3>\n            <p class="text-sm text-slate-400 mt-2 leading-relaxed">AI-powered performance summaries add written context around metrics, goals and dashboards so teams can review what changed and why without starting every analysis from a blank prompt.</p>\n            <a class="inline-flex mt-3 text-xs font-bold text-purple-300 underline" href="https://databox.com/performance-summary" target="_blank" rel="noopener noreferrer">Official summaries page</a>\n          </div>\n        </div>\n        <div class="p-5 rounded-2xl bg-purple-500/5 border border-purple-500/20 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">\n          <div>\n            <div class="font-bold text-white">Best no-cost evaluation path</div>\n            <p class="text-sm text-slate-300 mt-1 leading-relaxed">Start with the current no-card trial, connect a few real data sources, then test one question in Genie and one repeated reporting task. If the workflow saves real analyst time, compare paid plans by data-source, user and AI-credit needs before upgrading.</p>\n            <p class="text-[11px] text-slate-500 mt-2">Affiliate disclosure: COSHUMA uses the exact Databox referral URL issued to our account. The official feature links above are non-affiliate references.</p>\n          </div>\n          <a data-cta="affiliate" data-tool-id="databox" data-cta-source="databox_ai_stack" href="{VERIFIED_AFFILIATE}" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-extrabold text-sm text-center whitespace-nowrap">Try Databox Free →</a>\n        </div>\n      </section>\n'''

if MARKER not in html:
    anchor = '      <section class="p-7 rounded-3xl bg-[#131520] border border-[#222538] space-y-5">\n        <div>\n          <h2 class="text-2xl font-black text-white">Databox pricing and AI credits</h2>'
    if anchor not in html:
        raise SystemExit("Databox pricing anchor not found; refusing a blind patch")
    html = html.replace(anchor, section + "\n" + anchor, 1)

if VERIFIED_AFFILIATE not in html:
    raise SystemExit("Verified Databox affiliate URL missing after patch")
if html.count(MARKER) != 1:
    raise SystemExit("Databox AI-stack section marker is missing or duplicated")

PAGE.write_text(html, encoding="utf-8")
print("Applied current Databox AI-stack buyer guidance without changing the verified referral route.")
