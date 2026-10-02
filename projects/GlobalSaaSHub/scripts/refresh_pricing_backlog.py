#!/usr/bin/env python3
import copy, html, json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

from auto_aggregator import extract_domain, query_gemini_batch, query_tavily

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "data" / "tools.json"
TOOLS_NEXT = ROOT / "data" / "tools.next.json"
STATE = ROOT / "data" / "pricing-refresh-state.json"
ALLOWED_CURRENCIES = {"USD","GBP","EUR","CAD","AUD","BRL"}
ALLOWED_BILLING = {"monthly","annual","annual/monthly","per_user","usage_based","mixed"}
PRICE_FIELDS = {
    "pricing","pricing_source_url","pricing_verified","pricing_verified_at",
    "pricing_source_http_status","pricing_source_final_url","pricing_evidence_markers",
    "currency","billing_period","evidence_source_type"
}
PRICE_RE = re.compile(r"(?:[$€£]\s*\d+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?\s*(?:USD|EUR|GBP|CAD|AUD|BRL))", re.I)
PERIOD_RE = re.compile(r"\b(month|monthly|mo|year|yearly|annual|annually|yr|user|seat|usage|credit|request)\b", re.I)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

def norm(value):
    return SPACE_RE.sub(" ", html.unescape(str(value or ""))).strip().casefold()

def page_text(raw):
    return norm(TAG_RE.sub(" ", raw))

def same_domain(url, official):
    return bool(url and extract_domain(url) and extract_domain(url) == extract_domain(official))

def currency_present(currency, markers):
    joined = " ".join(markers)
    if currency == "USD":
        return "$" in joined or re.search(r"\bUSD\b", joined, re.I) is not None
    return re.search(rf"\b{re.escape(currency)}\b", joined, re.I) is not None

def billing_present(period, markers):
    joined = " ".join(markers).casefold()
    rules = {
        "monthly": r"\b(month|monthly|mo)\b",
        "annual": r"\b(year|yearly|annual|annually|yr)\b",
        "annual/monthly": r"\b(month|monthly|mo)\b.*\b(year|yearly|annual|annually|yr)\b|\b(year|yearly|annual|annually|yr)\b.*\b(month|monthly|mo)\b",
        "per_user": r"\b(user|seat)\b",
        "usage_based": r"\b(usage|credit|request)\b",
        "mixed": r"\b(month|monthly|year|annual|user|seat|usage|credit|request)\b",
    }
    return re.search(rules[period], joined, re.I) is not None

def validate_proposal(tool, proposal, source_urls, raw_html, final_url, checked_at):
    if not isinstance(proposal, dict):
        return None
    source = proposal.get("pricing_source_url")
    pricing = proposal.get("pricing")
    currency = proposal.get("currency")
    billing = proposal.get("billing_period")
    markers = proposal.get("pricing_evidence_markers")
    if source not in source_urls or not same_domain(source, tool["official_url"]) or not same_domain(final_url, tool["official_url"]):
        return None
    if not isinstance(pricing, str) or not re.search(r"\d", pricing):
        return None
    if currency not in ALLOWED_CURRENCIES or billing not in ALLOWED_BILLING:
        return None
    if not isinstance(markers, list) or not (2 <= len(markers) <= 5) or any(not isinstance(x,str) or not x.strip() for x in markers):
        return None
    body = page_text(raw_html)
    normalized_markers = [norm(x) for x in markers]
    if any(x not in body for x in normalized_markers):
        return None
    if not any(PRICE_RE.search(x) for x in markers) or not any(PERIOD_RE.search(x) for x in markers):
        return None
    if not currency_present(currency, markers) or not billing_present(billing, markers):
        return None
    pricing_numbers = set(re.findall(r"\d+(?:[.,]\d{1,2})?", pricing))
    marker_numbers = set(re.findall(r"\d+(?:[.,]\d{1,2})?", " ".join(markers)))
    if not pricing_numbers or pricing_numbers.isdisjoint(marker_numbers):
        return None
    return {
        "pricing": pricing.strip(),
        "pricing_source_url": source,
        "pricing_verified": True,
        "pricing_verified_at": checked_at,
        "pricing_source_http_status": 200,
        "pricing_source_final_url": final_url,
        "pricing_evidence_markers": markers,
        "currency": currency,
        "billing_period": billing,
        "evidence_source_type": "official_pricing_page",
    }

def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (compatible; COSHUMA-PricingVerifier/1.0)"})
    with urllib.request.urlopen(req, timeout=20) as res:
        if res.getcode() != 200:
            return None
        final = res.geturl()
        raw = res.read(2_000_000).decode("utf-8", errors="ignore")
        return final, raw

def load_state():
    if not STATE.exists():
        return {"schema_version":1,"tools":{}}
    data = json.loads(STATE.read_text(encoding="utf-8"))
    return data if isinstance(data,dict) and data.get("schema_version")==1 else {"schema_version":1,"tools":{}}

def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")

def assert_price_only(before, after):
    if len(before) != len(after):
        raise RuntimeError("Pricing refresh may not add/remove tools")
    old = {x["id"]:x for x in before}
    for row in after:
        prior = old[row["id"]]
        a = {k:v for k,v in prior.items() if k not in PRICE_FIELDS}
        b = {k:v for k,v in row.items() if k not in PRICE_FIELDS}
        if a != b:
            raise RuntimeError(f"Non-pricing mutation detected for {row['id']}")
        if prior.get("pricing_verified") is True and row != prior:
            raise RuntimeError(f"Already-verified pricing changed for {row['id']}")

def main():
    tavily = os.environ.get("TAVILY_API_KEY")
    gemini = os.environ.get("GEMINI_API_KEY")
    if not tavily or not gemini:
        raise SystemExit("Missing TAVILY_API_KEY or GEMINI_API_KEY")
    batch = max(1, min(int(os.environ.get("PRICING_REFRESH_BATCH","10")), 25))
    tools = json.loads(TOOLS.read_text(encoding="utf-8"))
    next_tools = json.loads(TOOLS_NEXT.read_text(encoding="utf-8")) if TOOLS_NEXT.exists() else copy.deepcopy(tools)
    before = copy.deepcopy(tools)
    state = load_state()
    attempts = state.setdefault("tools", {})
    candidates = [
        t for t in tools
        if t.get("pricing_verified") is not True
        and t.get("official_verification_status") == "verified"
        and isinstance(t.get("official_url"),str)
        and t["official_url"].startswith(("http://","https://"))
    ]
    candidates.sort(key=lambda t: (attempts.get(t["id"],{}).get("checked_at",""), t["id"]))
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updated = []
    for tool in candidates[:batch]:
        tid, domain = tool["id"], extract_domain(tool["official_url"])
        outcome = {"checked_at":checked_at,"status":"no_verified_price"}
        try:
            search, status = query_tavily(tavily, f'site:{domain} "{tool["name"]}" pricing plans monthly annual')
            if status != "OK" or not isinstance(search,dict):
                outcome["status"] = f"search_{status.lower()}"
                attempts[tid] = outcome
                continue
            results = []
            for item in search.get("results",[]):
                url = item.get("url")
                if same_domain(url, tool["official_url"]) and (
                    re.search(r"(pricing|price|plans|billing)", urllib.parse.urlparse(url).path, re.I)
                    or re.search(r"(pricing|price|plans)", str(item.get("title","")), re.I)
                ):
                    results.append({"url":url,"title":item.get("title",""),"content":item.get("content","")})
            if not results:
                outcome["status"] = "no_official_pricing_result"
                attempts[tid] = outcome
                continue
            prompt = (
                "Use only the supplied official-domain search snippets. Return [] if current public pricing is not explicit. "
                "Otherwise return a JSON array with exactly one object containing pricing_source_url, pricing, currency, billing_period, pricing_evidence_markers. "
                "pricing_evidence_markers must be 2-5 short verbatim strings from the snippets, including a price/currency string and billing-period string. "
                "Allowed currency: USD, GBP, EUR, CAD, AUD, BRL. Allowed billing_period: monthly, annual, annual/monthly, per_user, usage_based, mixed. "
                "Do not infer, estimate, convert currency, or invent missing values."
            )
            proposals, gstatus = query_gemini_batch(gemini, prompt, results)
            if gstatus != "OK" or not isinstance(proposals,list) or len(proposals) != 1:
                outcome["status"] = f"extract_{gstatus.lower()}"
                attempts[tid] = outcome
                continue
            proposal = proposals[0]
            source = proposal.get("pricing_source_url") if isinstance(proposal,dict) else None
            source_urls = {x["url"] for x in results}
            if source not in source_urls:
                outcome["status"] = "proposal_source_not_in_official_results"
                attempts[tid] = outcome
                continue
            fetched = fetch_html(source)
            if not fetched:
                outcome["status"] = "pricing_http_not_200"
                attempts[tid] = outcome
                continue
            final_url, raw = fetched
            patch = validate_proposal(tool, proposal, source_urls, raw, final_url, checked_at)
            if not patch:
                outcome["status"] = "evidence_validation_failed"
                attempts[tid] = outcome
                continue
            tool.update(patch)
            twin = next((x for x in next_tools if x.get("id")==tid), None)
            if twin is None:
                raise RuntimeError(f"tools.next missing {tid}")
            if twin.get("pricing_verified") is True:
                raise RuntimeError(f"tools.next already has verified pricing for {tid}")
            twin.update(patch)
            updated.append(tid)
            outcome = {"checked_at":checked_at,"status":"verified","pricing_source_url":patch["pricing_source_url"]}
        except Exception as exc:
            outcome["status"] = f"error_{type(exc).__name__}"
        attempts[tid] = outcome
    assert_price_only(before, tools)
    save_json(TOOLS, tools)
    save_json(TOOLS_NEXT, next_tools)
    state["last_run_at"] = checked_at
    state["last_batch_size"] = min(batch, len(candidates))
    state["last_updated_tools"] = updated
    save_json(STATE, state)
    print(json.dumps({"checked":min(batch,len(candidates)),"updated":updated,"remaining_unverified":sum(t.get("pricing_verified") is not True for t in tools)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
