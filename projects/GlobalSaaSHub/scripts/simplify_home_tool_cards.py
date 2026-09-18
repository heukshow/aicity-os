from pathlib import Path

app = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = app.read_text(encoding="utf-8")

replacements = [
    (
        '<p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-400">{tool.description}</p>',
        '<p className="mt-4 line-clamp-2 text-sm leading-6 text-slate-400">{tool.description}</p>',
    ),
    (
        "{(tool.key_features || []).slice(0, 3).map((feature) =>",
        "{(tool.key_features || []).slice(0, 2).map((feature) =>",
    ),
]

changes = 0
for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Homepage card markup changed; refusing unsafe replacement: {old[:80]}")
    text = text.replace(old, new, 1)
    changes += 1

blocked = (
    "affiliate_verified",
    "affiliate_status",
    "affiliate_evidence",
    "PartnerStack",
    "FirstPromoter",
    "Verified affiliate paths",
    "Affiliate link verified in our records",
)
for token in blocked:
    if token in text:
        raise SystemExit(f"Homepage source contains internal affiliate token: {token}")

app.write_text(text, encoding="utf-8")
print(f"Homepage cards simplified: changes={changes}; affiliate state remains outside frontend source")
