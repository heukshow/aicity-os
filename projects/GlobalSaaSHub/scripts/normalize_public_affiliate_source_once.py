from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TARGETS = [ROOT / "index.html", *PUBLIC.rglob("*")]
TEXT_EXTS = {".html", ".txt", ".xml", ".json", ".js", ".webmanifest"}
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)

DISCLOSURE = '<p class="text-xs text-slate-500 leading-relaxed"><strong>Affiliate disclosure:</strong> COSHUMA may earn a commission if you sign up or purchase through a partner link on this page, at no extra cost to you.</p>'

def rewrite_non_url(text: str) -> str:
    text = re.sub(r"\bPartnerStack\b", "partner program", text, flags=re.I)
    text = re.sub(r"\bFirstPromoter\b", "partner program", text, flags=re.I)
    text = re.sub(r"\baffiliate\s+manager\b", "vendor", text, flags=re.I)
    text = re.sub(r"\bpartner\s+manager\b", "vendor", text, flags=re.I)
    text = re.sub(r"\bverified\s+(?:COSHUMA\s+)?partner\s+(route|link|offer)\b", r"partner \1", text, flags=re.I)
    text = re.sub(r"\bverified\s+tracking\b", "partner link", text, flags=re.I)
    text = re.sub(r"\bverified\s+(?:affiliate|referral|customer-facing\s+)?link\b", "partner link", text, flags=re.I)
    text = re.sub(r"\bcustomer-facing\s+(?:tracking|referral|partner)\s+(?:URL|route|link)\b", "partner link", text, flags=re.I)
    text = re.sub(r"\btracking\s+verification\b", "link details", text, flags=re.I)
    text = re.sub(r"\btracking\s+status\b", "link details", text, flags=re.I)
    text = re.sub(r"\b(?:affiliate|partner|referral|commission)\s+(?:dashboard|portal)\b", "vendor information", text, flags=re.I)
    text = re.sub(r"\bauthenticated\s+partner\s+account\b", "vendor information", text, flags=re.I)
    text = re.sub(r"\bAffiliate\s+evidence\b", "Source note", text, flags=re.I)
    text = re.sub(r"\b(?:internal\s+verification|verification\s+evidence|partner-side\s+evidence|partner\s+correspondence)\b", "source information", text, flags=re.I)
    text = re.sub(r"\brevenue[ _-]?truth\b", "results", text, flags=re.I)
    text = re.sub(r"\bbrowser[ _-]?(?:required[ _-]?)?queue\b", "review", text, flags=re.I)
    text = re.sub(r"\bapproved_tracking\b", "partner_link", text, flags=re.I)
    text = re.sub(r"\baffiliate[ _-]?verified\b", "partner_link", text, flags=re.I)
    text = re.sub(r"\baffiliate[ _-]?evidence(?:[ _-]?markers)?\b", "source_notes", text, flags=re.I)
    text = re.sub(r"\baffiliate[ _-]?status\b", "partner_disclosure", text, flags=re.I)
    text = re.sub(r"\bapplication[ _-]?state\b", "availability", text, flags=re.I)
    text = re.sub(
        r"([^.!?<>]*\b(?:affiliate|partner|referral|creator)\s+application\s+(?:status|pending|submitted|under\s+review)\b[^.!?<>]*[.!?])",
        "COSHUMA does not currently use a partner link for this product.",
        text,
        flags=re.I,
    )
    # Contextual network labels: rewrite only when the same short text span explicitly
    # describes affiliate/partner/referral/tracking/commission operations.
    network = r"(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Awin|CJ\s+Affiliate)"
    ops = r"(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)"
    text = re.sub(rf"\b{network}\b(?=[^\n<>]{{0,80}}\b{ops}\b)", "partner program", text, flags=re.I)
    text = re.sub(rf"\b{ops}\b([^\n<>]{{0,80}})\b{network}\b", lambda m: m.group(0).replace(m.group(0)[m.group(0).lower().rfind(m.group(0).split()[-1].lower()):], "partner program"), text, flags=re.I)
    return text

def rewrite(text: str, suffix: str) -> str:
    # Keep outbound tracking/referral URLs byte-for-byte intact.
    parts=[]
    pos=0
    for m in URL_RE.finditer(text):
        parts.append(rewrite_non_url(text[pos:m.start()]))
        parts.append(m.group(0))
        pos=m.end()
    parts.append(rewrite_non_url(text[pos:]))
    text="".join(parts)

    # Public analytics source labels must not carry network names.
    text = re.sub(
        r'data-cta-source="([^"]*?)(partnerstack|firstpromoter|impact|dub|cello|tolt|awin|cj[_-]?affiliate)([^"]*?)"',
        lambda m: f'data-cta-source="{m.group(1)}partner{m.group(3)}"',
        text,
        flags=re.I,
    )

    if suffix == ".html" and re.search(r'data-cta="affiliate"', text, flags=re.I):
        if "Affiliate disclosure:" not in text:
            text = re.sub(r'(<a\b[^>]*data-cta="affiliate"[^>]*>)', DISCLOSURE + "\n" + r"\1", text, count=1, flags=re.I)
    return text

changed=[]
for path in TARGETS:
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
        continue
    old=path.read_text(encoding="utf-8", errors="replace")
    new=rewrite(old, path.suffix.lower())
    if new != old:
        path.write_text(new, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

print(f"normalized public affiliate source files={len(changed)}")
for p in changed:
    print(p)

# One-time cleanup branch only; remove after source boundary reaches zero.
