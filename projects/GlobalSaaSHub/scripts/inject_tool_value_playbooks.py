from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PUBLIC = ROOT / "public"
START = "<!-- COSHUMA_VALUE_PLAYBOOK_START -->"
END = "<!-- COSHUMA_VALUE_PLAYBOOK_END -->"

SPECIAL_PATHS = {
    "fillout": "best/fillout-form-builder.html",
}

SPECIAL_DETAIL_PATHS = {
    "fillout": "/best/fillout-form-builder.html",
}


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def load_playbooks() -> dict:
    merged: dict = {}
    files = sorted(DATA_DIR.glob("tool_value_playbooks*.json"))
    if not files:
        raise SystemExit("No tool value playbook data files found")
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SystemExit(f"Playbook file must contain an object: {path.name}")
        overlap = sorted(set(merged).intersection(payload))
        if overlap:
            raise SystemExit(f"Duplicate tool value playbook ids in {path.name}: {', '.join(overlap)}")
        merged.update(payload)
    return merged


def detail_path(tool_id: str) -> str:
    return SPECIAL_DETAIL_PATHS.get(tool_id, f"/tool/{tool_id}.html")


def render_recommendations(entry: dict) -> str:
    pairs = entry.get("pairs") or []
    if not pairs:
        return ""

    cards = "".join(
        (
            f'<a href="{esc(detail_path(item["id"]))}" class="block rounded-2xl border border-cyan-500/20 bg-cyan-500/[0.05] p-4 hover:border-cyan-400/40 transition">'
            f'<div class="font-bold text-cyan-200">{esc(item["id"].replace("-", " ").title())}</div>'
            f'<p class="mt-2 text-sm text-slate-300">{esc(item["why"])}</p>'
            '</a>'
        )
        for item in pairs
    )

    return f'''
      <section class="p-6 rounded-3xl bg-[#131520] border border-cyan-500/20 space-y-5" aria-label="Tools that may be useful in the same workflow">
        <div>
          <div class="text-xs font-bold uppercase tracking-[0.18em] text-cyan-300">Workflow recommendation</div>
          <h2 class="mt-2 text-2xl font-black text-white">Useful together when...</h2>
          <p class="mt-2 text-sm leading-6 text-slate-400">COSHUMA only shows this section when another tool has a distinct workflow role. This does not imply a native integration unless the page explicitly says so.</p>
        </div>
        <div class="grid gap-3 md:grid-cols-3">{cards}</div>
      </section>'''


def render(tool_id: str, entry: dict) -> str:
    problems = "".join(
        f'<li class="flex gap-2"><span class="text-emerald-300">✓</span><span>{esc(item)}</span></li>'
        for item in entry.get("problems", [])
    )

    methods = "".join(
        (
            '<article class="rounded-2xl border border-violet-500/20 bg-violet-500/[0.05] p-4">'
            f'<h3 class="font-bold text-white">{esc(item["title"])}</h3>'
            f'<p class="mt-2 text-xs text-slate-400">Difficulty: {esc(item["difficulty"])} · Starting cost: {esc(item["cost"])}</p>'
            f'<p class="mt-2 text-sm text-slate-300">Example deliverable: {esc(item["output"])}</p>'
            '</article>'
        )
        for item in entry.get("monetization", [])
    )

    recommendations = render_recommendations(entry)

    return f'''{START}
      <section class="p-6 rounded-3xl bg-[#131520] border border-emerald-500/20 space-y-5" aria-label="Problems this tool can help solve">
        <div>
          <div class="text-xs font-bold uppercase tracking-[0.18em] text-emerald-300">Practical value</div>
          <h2 class="mt-2 text-2xl font-black text-white">Problems it can help solve</h2>
          <p class="mt-2 text-sm leading-6 text-slate-400">These are workflow problems the tool's documented capabilities can help address. COSHUMA does not promise a specific business result.</p>
        </div>
        <ul class="space-y-3 text-sm leading-6 text-slate-300">{problems}</ul>
      </section>

      <section class="p-6 rounded-3xl bg-[#131520] border border-violet-500/20 space-y-5" aria-label="Ways to make money with this tool">
        <div>
          <div class="text-xs font-bold uppercase tracking-[0.18em] text-violet-300">Service ideas</div>
          <h2 class="mt-2 text-2xl font-black text-white">Ways to make money with this tool</h2>
          <p class="mt-2 text-sm leading-6 text-slate-400">Use the tool to create a service, workflow or deliverable someone may pay for. These are use-case ideas, not income guarantees.</p>
        </div>
        <div class="grid gap-3 md:grid-cols-3">{methods}</div>
      </section>{recommendations}
{END}'''


def inject_file(tool_id: str, entry: dict) -> None:
    relative = entry.get("path") or SPECIAL_PATHS.get(tool_id) or f"tool/{tool_id}.html"
    path = PUBLIC / relative
    if not path.exists():
        raise SystemExit(f"Missing target page for {tool_id}: {relative}")

    text = path.read_text(encoding="utf-8")
    block = render(tool_id, entry)

    if START in text and END in text:
        before, rest = text.split(START, 1)
        _, after = rest.split(END, 1)
        text = before + block + after
    else:
        anchor_pos = text.find("Which ")
        if anchor_pos != -1:
            section_pos = text.rfind("<section", 0, anchor_pos)
        else:
            section_pos = -1

        if section_pos == -1:
            section_pos = text.rfind("</main>")
        if section_pos == -1:
            raise SystemExit(f"No safe insertion point found for {tool_id}: {relative}")

        text = text[:section_pos] + block + "\n\n      " + text[section_pos:]

    path.write_text(text, encoding="utf-8")
    print(f"Injected value playbook: {tool_id} -> {relative}")


def main() -> None:
    payload = load_playbooks()
    if not payload:
        raise SystemExit("Tool value playbooks are empty")
    for tool_id, entry in payload.items():
        inject_file(tool_id, entry)
    print(f"Injected {len(payload)} tool value playbooks")


if __name__ == "__main__":
    main()
