"""Keep Text affiliate CTAs on the exact vendor-issued campaign URL.

The Partner App campaign URL is authoritative. Internal CTA attribution belongs in
`data-cta-source`; adding new query parameters to the external partner URL is not
necessary and can make revenue attribution harder to verify.

Text Support confirmed on 2026-09-12 that the partner program is campaign-based
and there is no deeper campaign than those shown in the partner panel. Therefore
COSHUMA must not present the verified campaign URL as if it were a direct trial
or signup deep link. The trial still exists, but visitors first open the tracked
campaign and then choose Text's Start free trial action on text.com.
"""
from pathlib import Path
import html as html_lib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
EXACT_URL = "https://www.text.com/?a=8IetMhQvR&utm_campaign=pp_text-wins-martech-awards&utm_source=PP"

ANCHOR_RE = re.compile(r"<a\b[^>]*>", re.I)
HREF_RE = re.compile(r'href="([^"]+)"', re.I)
HERO_CTA_RE = re.compile(
    r'(<a\b[^>]*data-cta-source="text-hero-trial"[^>]*>.*?</a>)',
    re.I | re.S,
)

MISLEADING_LABELS = {
    "Start Text Free for 14 Days — No Card →": "Open Text.com → Start 14-day trial",
    "Test Text Free for 14 Days →": "Open Text.com → Start 14-day trial",
}

ROUTING_NOTE_MARKER = "Text partner routing note — September 12, 2026"
ROUTING_NOTE = (
    '<div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 text-sm text-slate-300 leading-relaxed">'
    '<strong class="text-amber-300">Text partner routing note — September 12, 2026:</strong> '
    'Text Support confirmed that its partner program is campaign-based and that there is no deeper affiliate campaign than the campaigns shown in the partner panel. '
    'This verified COSHUMA link therefore opens the tracked Text.com campaign first; on Text.com, choose <strong>Start free trial</strong> to begin the 14-day trial. '
    'Do not treat this campaign URL as a direct trial-signup deep link.'
    '</div>'
)

changed_files = []
changed_links = 0
changed_copy = 0
seen = 0

for path in PUBLIC.rglob("*.html"):
    original = path.read_text(encoding="utf-8")

    def normalize(match: re.Match[str]) -> str:
        global changed_links, seen
        anchor = match.group(0)
        if 'data-cta="affiliate"' not in anchor or 'data-tool-id="text"' not in anchor:
            return anchor
        seen += 1
        href_match = HREF_RE.search(anchor)
        if not href_match:
            raise SystemExit(f"Text affiliate CTA missing href: {path}")
        href = href_match.group(1).replace("&amp;", "&")
        if href == EXACT_URL:
            return anchor
        if not href.startswith("https://www.text.com/?a=8IetMhQvR&utm_campaign=pp_text-wins-martech-awards&utm_source=PP"):
            raise SystemExit(f"Unexpected Text affiliate URL in {path}: {href}")
        changed_links += 1
        return anchor[: href_match.start(1)] + EXACT_URL + anchor[href_match.end(1) :]

    updated = ANCHOR_RE.sub(normalize, original)

    if EXACT_URL in updated:
        for old, new in MISLEADING_LABELS.items():
            occurrences = updated.count(old)
            if occurrences:
                updated = updated.replace(old, new)
                changed_copy += occurrences

    if path.as_posix().endswith("public/tool/text.html") and ROUTING_NOTE_MARKER not in updated:
        if not HERO_CTA_RE.search(updated):
            raise SystemExit("Text hero CTA anchor not found; routing note was not inserted")
        updated = HERO_CTA_RE.sub(r"\1\n          " + ROUTING_NOTE, updated, count=1)
        changed_copy += 1

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed_files.append(path.relative_to(ROOT).as_posix())

if seen == 0:
    raise SystemExit("No Text affiliate CTAs found; expected at least one")

for path in PUBLIC.rglob("*.html"):
    html = path.read_text(encoding="utf-8")
    for anchor in ANCHOR_RE.findall(html):
        if 'data-cta="affiliate"' not in anchor or 'data-tool-id="text"' not in anchor:
            continue
        href_match = HREF_RE.search(anchor)
        href = href_match.group(1).replace("&amp;", "&") if href_match else ""
        if href != EXACT_URL:
            raise SystemExit(f"Text affiliate CTA is not exact vendor route in {path}: {href}")

text_page = PUBLIC / "tool" / "text.html"
if text_page.exists():
    text_html = text_page.read_text(encoding="utf-8")
    if ROUTING_NOTE_MARKER not in text_html:
        raise SystemExit("Text partner routing note missing after normalization")
    for old in MISLEADING_LABELS:
        if old in text_html:
            raise SystemExit(f"Misleading direct-trial CTA survived normalization: {old}")

print(
    f"normalize_text_verified_tracking: seen={seen} changed_links={changed_links} "
    f"changed_copy={changed_copy} files_changed={len(changed_files)}"
)
for item in changed_files:
    print(f" - {item}")

# ---------------------------------------------------------------------------
# Public-copy privacy pass
# ---------------------------------------------------------------------------
# Affiliate operations, application state, tracking verification mechanics and
# account troubleshooting belong in private/admin records, not buyer-facing
# pages. Keep product facts and the short legal commission disclosure, but strip
# internal workflow commentary from static HTML and FAQ JSON-LD before Vite
# copies public/ into dist. This also makes the cleanup durable for non-JS
# crawlers instead of relying only on brand-runtime.js.

INTERNAL_OPS_PATTERNS = [
    re.compile(p, re.I) for p in [
        r"^Affiliate status:",
        r"COSHUMA affiliate status",
        r"COSHUMA CTA state",
        r"PartnerStack application not submitted",
        r"Waiting vendor response",
        r"outreach thread pending",
        r"COSHUMA (?:currently )?has not (?:submitted|verified|yet recovered|recovered|received)",
        r"COSHUMA's? account .*?(?:pending|blocked|awaiting|upgrade|support)",
        r"no verified (?:account[- ]specific |customer[- ]facing )?(?:referral|tracking) URL",
        r"no .* customer referral URL .* verified",
        r"Official non-affiliate link",
        r"official non-affiliate (?:links|destinations)",
        r"These buttons (?:intentionally )?remain official non-affiliate",
        r"Tracking verification:",
        r"exact customer-facing .* referral URL .* (?:issued|confirmed|dashboard)",
        r"customer-facing destinations were supplied directly by the partner programs",
        r"COSHUMA does not invent referral parameters",
        r"uses only the exact .* (?:referral|invite) URL issued",
        r"A click (?:does not imply|is never treated as) a (?:signup|sale)",
        r"No clicks?, signups?, paid customers?, commissions? or revenue (?:are|is) inferred",
        r"approval .* unknown",
        r"application .* pending",
        r"application .* declined",
        r"application .* rejected",
        r"application .* not submitted",
        r"support resolving",
        r"awaiting help for an upgrade",
        r"upgrade-screen loop",
        r"account-access evidence",
        r"affiliate dashboard rather than a generic homepage",
        r"Affiliate link verified in our records",
        r"Use the exact tracked .* confirmed for COSHUMA",
        r"partner-tagged .* approved for COSHUMA",
        r"COSHUMA uses only the exact personal .* (?:referral|invite)",
        r"COSHUMA (?:currently )?has a verified .* (?:route|referral|tracking)",
        r"dashboard, onboarding page or generic homepage is never treated as an affiliate link",
        r"Text partner routing note",
        r"This verified COSHUMA link therefore opens the tracked Text\.com campaign first",
    ]
]

TAG_RE = re.compile(r"<[^>]+>")
JSONLD_RE = re.compile(
    r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S,
)


def visible_text(fragment: str) -> str:
    text = TAG_RE.sub(" ", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(text)).strip()


def internal_ops_text(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", html_lib.unescape(text)).strip()
    return bool(normalized) and any(pattern.search(normalized) for pattern in INTERNAL_OPS_PATTERNS)


def strip_block(match: re.Match[str]) -> str:
    block = match.group(0)
    text = visible_text(block)
    if re.search(r"may earn (?:an affiliate )?commission|at no extra cost", text, re.I) and not re.search(
        r"non-affiliate|not submitted|pending|declined|rejected|has not verified", text, re.I
    ):
        return block
    return "" if internal_ops_text(text) else block


def sanitize_jsonld(html: str) -> str:
    def rewrite(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(2))
        except Exception:
            return match.group(0)

        changed = False

        def walk(node):
            nonlocal changed
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if not isinstance(node, dict):
                return
            types = node.get("@type")
            types = types if isinstance(types, list) else [types]
            if "FAQPage" in types and isinstance(node.get("mainEntity"), list):
                original_items = node["mainEntity"]
                kept = []
                for item in original_items:
                    question = str(item.get("name", "")) if isinstance(item, dict) else ""
                    answer_obj = item.get("acceptedAnswer", {}) if isinstance(item, dict) else {}
                    answer = str(answer_obj.get("text", "")) if isinstance(answer_obj, dict) else ""
                    combined = f"{question} {answer}".strip()
                    admin_question = bool(
                        re.search(r"COSHUMA|affiliate link|referral link|tracking URL", question, re.I)
                    )
                    if (admin_question and internal_ops_text(combined)) or internal_ops_text(combined):
                        changed = True
                        continue
                    kept.append(item)
                if len(kept) != len(original_items):
                    node["mainEntity"] = kept
            for value in node.values():
                walk(value)

        walk(data)
        if not changed:
            return match.group(0)
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    return JSONLD_RE.sub(rewrite, html)


def strip_internal_ops_html(source: str) -> str:
    updated = source
    updated = re.sub(
        r"<tr\b[^>]*>(?:(?!</tr>).)*?(?:COSHUMA\s+)?(?:affiliate status|CTA state)(?:(?!</tr>).)*?</tr>",
        "",
        updated,
        flags=re.I | re.S,
    )
    for tag in ("p", "li", "small"):
        updated = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", strip_block, updated, flags=re.I | re.S)
    updated = re.sub(r"<div\b[^>]*>(?:(?!<div\b).)*?</div>", strip_block, updated, flags=re.I | re.S)
    updated = re.sub(
        r"<section\b[^>]*>(?:(?!</section>).)*?<h[1-3]\b[^>]*>\s*How this list is gated\s*</h[1-3]>(?:(?!</section>).)*?</section>",
        "",
        updated,
        flags=re.I | re.S,
    )
    return sanitize_jsonld(updated)


# This buyer hub is intentionally assembled by several strict, fail-closed
# partner-offer scripts that run after this step. Leave its source structure
# intact; brand-runtime.js applies the same customer-facing cleanup after load.
# Other pages are statically cleaned before Vite so non-JS crawlers also receive
# the simplified copy.
OPS_STATIC_SKIP = {
    PUBLIC / "best" / "verified-software-free-trials-deals.html",
}

ops_changed = []
for ops_path in [ROOT / "index.html", *PUBLIC.rglob("*.html")]:
    if not ops_path.exists() or ops_path in OPS_STATIC_SKIP:
        continue
    before = ops_path.read_text(encoding="utf-8")
    after = strip_internal_ops_html(before)
    if after != before:
        ops_path.write_text(after, encoding="utf-8")
        ops_changed.append(ops_path.relative_to(ROOT).as_posix())

print(f"public_ops_copy_cleanup: files_changed={len(ops_changed)}")
for item in ops_changed:
    print(f" - {item}")
