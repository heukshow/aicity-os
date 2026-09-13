from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
APP = ROOT / "src" / "App.jsx"

FAVICON = '<link rel="icon" href="/brand/coshuma-favicon.svg" type="image/svg+xml" />'
PLACEHOLDER_PATTERNS = [
    re.compile(r'<div class="h-8 w-8 rounded-lg bg-purple-600 flex items-center justify-center font-extrabold text-white text-lg">C</div>'),
    re.compile(r'<div class="h-8 w-8 rounded-lg bg-purple-600 flex items-center justify-center font-extrabold">C</div>'),
]
BRAND_IMG = '<img src="/brand/coshuma-mark.svg" alt="COSHUMA" class="h-8 w-8 object-contain" />'


def patch_public_html() -> int:
    changed = 0
    for path in PUBLIC.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        original = text
        if "/brand/coshuma-favicon.svg" not in text and "</head>" in text:
            text = text.replace("</head>", f"  {FAVICON}\n</head>", 1)
        for pattern in PLACEHOLDER_PATTERNS:
            text = pattern.sub(BRAND_IMG, text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def patch_app() -> bool:
    text = APP.read_text(encoding="utf-8")
    original = text
    old_nav = '''            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 shadow-lg shadow-violet-950/40">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="text-lg font-black tracking-tight">COSHUMA</div>
              <div className="-mt-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">AI & SaaS decision guides</div>
            </div>'''
    new_nav = '''            <img src="/brand/coshuma-mark.svg" alt="COSHUMA" className="h-10 w-12 object-contain" />
            <div>
              <div className="text-lg font-black tracking-[0.08em]">COSHUMA</div>
              <div className="-mt-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">Better Tools · A Brighter Tomorrow</div>
            </div>'''
    if old_nav in text:
        text = text.replace(old_nav, new_nav, 1)
    if 'href="/brand/"' not in text:
        pos = text.rfind("</footer>")
        if pos != -1:
            text = text[:pos] + '          <a href="/brand/" className="text-xs font-semibold text-slate-500 hover:text-slate-300">Brand identity & logo downloads</a>\n' + text[pos:]
    if text != original:
        APP.write_text(text, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    public_count = patch_public_html()
    app_changed = patch_app()
    print(f"COSHUMA brand rollout: public_html={public_count}, app_changed={app_changed}")
