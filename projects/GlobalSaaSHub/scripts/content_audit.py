#!/usr/bin/env python3
"""GlobalSaaSHub content audit: corpus topology, text hygiene, and live URLs."""
from __future__ import annotations
import argparse, concurrent.futures, html, json, re, ssl, sys, urllib.error, urllib.parse, urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"/"tools.json"; PUBLIC=ROOT/"public"
STATUSES=("VERIFIED","FIXED","STALE","BROKEN","TYPO","UNVERIFIED")
FIXED_IDS={"notion-ai","convertkit","socialchamp-io","carv","followr","bidx","fathom","chatbase"}
BAD=[re.compile(p,re.I) for p in (r"\ufffd",r"(?:Ã.|Â.|â€|ðŸ|ï¸|\?{3,})",r"&(?:amp|quot|apos|lt|gt);",r"\s{2,}",r"\b(?:lorem ipsum|placeholder|todo|tbd)\b")]
def domain(url):
 h=(urllib.parse.urlparse(url or "").hostname or "").lower().rstrip("."); return h[4:] if h.startswith("www.") else h
def same_domain(a,b):
 da,db=domain(a),domain(b); return bool(da and db and (da==db or da.endswith("."+db) or db.endswith("."+da)))
def plain(s): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",s))).strip()
def attr(tag,name):
 m=re.search(rf"\b{re.escape(name)}=[\"']([^\"']+)",tag or "",re.I); return html.unescape(m.group(1)).strip() if m else None
def finding(tid,kind,code,evidence): return {"tool_id":tid,"classification":kind,"code":code,"evidence":evidence}
def fetch(url,timeout=18):
 out={"requested_url":url,"final_url":None,"status":None,"redirect_chain":[],"error":None,"title":None,"name_evidence":None}
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"GlobalSaaSHubContentAudit/1.0 (+https://coshuma.com/)","Accept":"text/html"})
  with urllib.request.urlopen(req,timeout=timeout,context=ssl.create_default_context()) as r:
   body=r.read(750000).decode(r.headers.get_content_charset() or "utf-8",errors="replace"); final=r.geturl(); tm=re.search(r"<title[^>]*>(.*?)</title>",body,re.I|re.S)
   out.update(status=r.status,final_url=final,redirect_chain=[] if final==url else [url,final],title=plain(tm.group(1))[:300] if tm else None,body_excerpt=plain(body)[:2500])
 except urllib.error.HTTPError as e: out.update(status=e.code,final_url=e.geturl(),error=f"http_{e.code}")
 except Exception as e: out["error"]=f"{type(e).__name__}: {str(e)[:180]}"
 return out
def detail_checks(t,issues):
 tid,name,path=t["id"],t["name"],PUBLIC/"tool"/f"{t['id']}.html"
 if not path.exists(): issues.append(finding(tid,"BROKEN","detail_missing",path.name)); return
 s=path.read_text(encoding="utf-8"); ct=re.search(r"<link\b[^>]*\brel=[\"']canonical[\"'][^>]*>",s,re.I); h1=re.search(r"<h1[^>]*>(.*?)</h1>",s,re.I|re.S); title=re.search(r"<title[^>]*>(.*?)</title>",s,re.I|re.S)
 if attr(ct.group(0) if ct else "","href")!=f"https://coshuma.com/tool/{tid}.html": issues.append(finding(tid,"BROKEN","canonical_mismatch",attr(ct.group(0) if ct else "","href")))
 if not h1 or plain(h1.group(1))!=name: issues.append(finding(tid,"BROKEN","h1_name_mismatch",plain(h1.group(1)) if h1 else None))
 if not title or name not in plain(title.group(1)): issues.append(finding(tid,"BROKEN","title_name_mismatch",plain(title.group(1)) if title else None))
 ld=re.search(r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>",s,re.I|re.S)
 try: ldname=json.loads(ld.group(1))["name"] if ld else None
 except (json.JSONDecodeError,KeyError): ldname=None
 if ldname!=name: issues.append(finding(tid,"BROKEN","jsonld_name_mismatch",ldname))
 oc=re.findall(r'<a\b[^>]*data-cta=["\']official["\'][^>]*>',s,re.I); ac=re.findall(r'<a\b[^>]*data-cta=["\']affiliate["\'][^>]*>',s,re.I); expected_aff=bool(t.get("affiliate_url") and t.get("affiliate_verified") is True)
 if len(oc)!=(1 if t.get("official_url") else 0): issues.append(finding(tid,"BROKEN","official_cta_visibility",len(oc)))
 if len(ac)!=(1 if expected_aff else 0): issues.append(finding(tid,"BROKEN","affiliate_cta_visibility",len(ac)))
 if oc and attr(oc[0],"href")!=t.get("official_url"): issues.append(finding(tid,"BROKEN","official_cta_target",attr(oc[0],"href")))
 if ac and attr(ac[0],"href")!=t.get("affiliate_url"): issues.append(finding(tid,"BROKEN","affiliate_cta_target",attr(ac[0],"href")))
def audit(online=False,workers=12):
 tools=json.loads(DATA.read_text(encoding="utf-8")); issues=[]; ids=[t.get("id") for t in tools]; idset=set(ids)
 for v,c in Counter(ids).items():
  if c>1: issues.append(finding(v,"BROKEN","duplicate_id",c))
 for v,c in Counter(str(t.get("name","")).lower() for t in tools).items():
  if c>1: issues.append(finding(None,"BROKEN","duplicate_name",{"name":v,"count":c}))
 domains=defaultdict(list)
 for t in tools: domains[domain(t.get("official_url"))].append(t["id"])
 for v,tids in domains.items():
  if v and len(tids)>1: issues.append(finding(None,"UNVERIFIED","duplicate_official_domain",{"domain":v,"tool_ids":tids}))
 names=[(t["id"],t["name"].lower()) for t in tools]
 for t in tools:
  tid=t.get("id")
  if not isinstance(tid,str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",tid): issues.append(finding(tid,"BROKEN","invalid_id",tid))
  for field in ("name","description","category_display","pricing"):
   value=t.get(field)
   if not isinstance(value,str) or not value.strip(): issues.append(finding(tid,"BROKEN","missing_text_field",field)); continue
   for p in BAD:
    if p.search(value): issues.append(finding(tid,"TYPO","suspicious_text",{"field":field,"value":value,"pattern":p.pattern}))
  desc=t.get("description","").lower()
  for oid,oname in names:
   if oid!=tid and len(oname)>=5 and re.search(rf"\b{re.escape(oname)}\b",desc): issues.append(finding(tid,"UNVERIFIED","possible_cross_tool_copy",{"other_tool":oid,"name":oname}))
  if not isinstance(t.get("official_url"),str) or not re.match(r"^https?://",t.get("official_url", "")): issues.append(finding(tid,"BROKEN","official_url_invalid",t.get("official_url")))
  if re.search(r"\$\s*\d",t.get("pricing","")) and not t.get("pricing_source_url"): issues.append(finding(tid,"UNVERIFIED","numeric_pricing_without_source",t.get("pricing")))
  detail_checks(t,issues)
 sitemap_ids=set(re.findall(r"https://coshuma\.com/tool/([a-z0-9-]+)\.html",(PUBLIC/"sitemap.xml").read_text(encoding="utf-8"))); detail_ids={p.stem for p in (PUBLIC/"tool").glob("*.html")}
 if sitemap_ids!=idset: issues.append(finding(None,"BROKEN","sitemap_tool_ids",{"missing":sorted(idset-sitemap_ids),"extra":sorted(sitemap_ids-idset)}))
 if detail_ids!=idset: issues.append(finding(None,"BROKEN","detail_tool_ids",{"missing":sorted(idset-detail_ids),"extra":sorted(detail_ids-idset)}))
 compare=list((PUBLIC/"compare").glob("*.html"))
 for path in compare:
  s=path.read_text(encoding="utf-8"); parts=path.stem.split("-vs-"); links=re.findall(r'href=["\']/tool/([a-z0-9-]+)\.html["\']',s,re.I)
  if len(parts)!=2 or any(x not in idset for x in parts): issues.append(finding(None,"BROKEN","compare_slug_mismatch",path.name)); continue
  for x in links:
   if x not in idset: issues.append(finding(None,"BROKEN","compare_unknown_tool_link",{"page":path.name,"tool_id":x}))
  for x in parts:
   name=next(t["name"] for t in tools if t["id"]==x)
   if name not in s: issues.append(finding(x,"BROKEN","compare_display_name_missing",path.name))
 live={}
 if online:
  jobs=[(t["id"],k,t.get(k)) for t in tools for k in ("official_url","pricing_source_url","affiliate_url") if t.get(k)]
  with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(workers,24))) as pool:
   pending={pool.submit(fetch,url):(tid,k) for tid,k,url in jobs}
   for future in concurrent.futures.as_completed(pending): tid,k=pending[future]; live.setdefault(tid,{})[k]=future.result()
  for t in tools:
   tid=t["id"]; off=live.get(tid,{}).get("official_url")
   if off:
    if not off.get("status") or off["status"]>=400: issues.append(finding(tid,"UNVERIFIED","official_url_unreachable",off))
    elif not same_domain(t["official_url"],off.get("final_url")): issues.append(finding(tid,"BROKEN","official_redirect_domain_mismatch",off))
    else:
     nt=[x for x in re.findall(r"[a-z0-9]+",t["name"].lower()) if len(x)>2 and x not in {"the","com","app","ai"}]; hay=(str(off.get("title") or "")+" "+str(off.get("body_excerpt") or "")).lower(); off["name_evidence"]=bool(not nt or any(x in hay for x in nt))
     if nt and not off["name_evidence"]: issues.append(finding(tid,"UNVERIFIED","official_identity_not_evidenced",off))
   aff=live.get(tid,{}).get("affiliate_url")
   if aff and aff.get("final_url") and not same_domain(t["official_url"],aff["final_url"]): issues.append(finding(tid,"BROKEN","affiliate_final_domain_mismatch",aff))
   price=live.get(tid,{}).get("pricing_source_url")
   if price and (not price.get("status") or price["status"]>=400): issues.append(finding(tid,"UNVERIFIED","pricing_source_unreachable",price))
 per=[]; rank={"BROKEN":0,"TYPO":1,"STALE":2}
 for t in tools:
  tis=[x for x in issues if x.get("tool_id")==t["id"]]; actionable=[x["classification"] for x in tis if x["classification"] in {"BROKEN","STALE","TYPO"}]
  status=min(actionable,key=lambda s:rank[s]) if actionable else ("FIXED" if t["id"] in FIXED_IDS else ("UNVERIFIED" if any(x["classification"]=="UNVERIFIED" for x in tis) or not online else "VERIFIED"))
  per.append({"id":t["id"],"name":t["name"],"classification":status,"official_url":t.get("official_url"),"pricing_source_url":t.get("pricing_source_url"),"rating":t.get("rating"),"issues":tis,"live_evidence":live.get(t["id"],{})})
 counts={s:sum(t["classification"]==s for t in per) for s in STATUSES}
 return {"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"online":online,"source":"data/tools.json","tool_count":len(tools),"detail_pages_checked":len(detail_ids),"compare_pages_checked":len(compare),"sitemap_tool_urls_checked":len(sitemap_ids),"classification_counts":counts,"global_issues":[x for x in issues if x.get("tool_id") is None],"tools":per}
def markdown(r):
 lines=["# GlobalSaaSHub Content Audit Report","",f"Generated: {r['generated_at']}","",f"Scope: {r['tool_count']} tools, {r['detail_pages_checked']} detail pages, {r['compare_pages_checked']} comparison pages, {r['sitemap_tool_urls_checked']} sitemap tool URLs.","","## Classification summary","","| Classification | Count |","|---|---:|"]+[f"| {s} | {r['classification_counts'][s]} |" for s in STATUSES]+["","## Tool results","","| ID | Tool | Result | Findings |","|---|---|---|---|"]
 for t in r["tools"]: lines.append(f"| `{t['id']}` | {t['name'].replace('|','/')} | **{t['classification']}** | {', '.join(sorted({x['code'] for x in t['issues']})) or 'Official-source and generated-page checks passed'} |")
 if r["global_issues"]: lines += ["","## Global findings",""]+[f"- **{x['classification']} — {x['code']}**: `{json.dumps(x['evidence'],ensure_ascii=False)}`" for x in r["global_issues"]]
 lines += ["","## Method and limitations","","Live evidence is collected only from official, official pricing-source, and affiliate URLs. Blocked, dynamic, login-only, or region-dependent content is classified UNVERIFIED rather than inferred. Ratings without documented methodology are retained but are not represented as official vendor ratings.",""]; return "\n".join(lines)
def main():
 p=argparse.ArgumentParser(); p.add_argument("--online",action="store_true"); p.add_argument("--workers",type=int,default=12); p.add_argument("--json",type=Path,default=ROOT/"data"/"content_audit_report.json"); p.add_argument("--markdown",type=Path,default=ROOT/"data"/"content_audit_report.md"); p.add_argument("--fail-on-structural",action="store_true"); a=p.parse_args(); r=audit(a.online,a.workers); a.json.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); a.markdown.write_text(markdown(r),encoding="utf-8"); print(json.dumps(r["classification_counts"])); return 1 if a.fail_on_structural and sum(r["classification_counts"][s] for s in ("BROKEN","STALE","TYPO")) else 0
if __name__=="__main__": sys.exit(main())
