from pathlib import Path

app = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = app.read_text(encoding="utf-8")
needle = "              onFocus={() => document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'center' })}\n"
if needle in text:
    text = text.replace(needle, "", 1)
    app.write_text(text, encoding="utf-8")
    print("Removed search focus auto-scroll from App.jsx")
elif "onFocus={() => document.getElementById('directory')?.scrollIntoView" in text:
    raise SystemExit("Search focus auto-scroll still exists but exact patch no longer matches; refusing unsafe edit")
else:
    print("Search focus auto-scroll already absent")
