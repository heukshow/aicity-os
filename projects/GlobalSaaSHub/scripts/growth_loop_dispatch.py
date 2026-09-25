#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data"/"operations_registry.json"
data=json.loads(REG.read_text(encoding="utf-8"))
terminal={"production_verified","measured","rejected_with_evidence"}
rank={"critical":0,"high":1,"normal":2,"low":3}
# Never let a known external blocker monopolize productive dispatch.
items=[x for x in data.get("active_queue",[]) if x.get("lifecycle") not in terminal and not x.get("blocker")]
items.sort(key=lambda x:(rank.get(x.get("priority"),99),x.get("last_evidence_at",""),x.get("record_id","")))
next_task=items[0] if items else None
# Closed-loop stages are role contracts, not claims that a stage has executed.
stages=[
 {"stage":"discover","owner":"Market & Competitive Intelligence Team","gate":"validated demand / monetization evidence"},
 {"stage":"affiliate","owner":"Affiliate Partnerships Team","gate":"application evidence or verified tracking URL"},
 {"stage":"search_content","owner":"Growth & SEO Team / Editorial Quality Team","gate":"bounded buyer-intent implementation evidence"},
 {"stage":"release","owner":"Release & Reliability Team","gate":"production_verified"},
 {"stage":"measure","owner":"Audience Growth Team / Revenue Intelligence Team","gate":"measured traffic, intent, affiliate and revenue truth"},
 {"stage":"decide","owner":"Operations Governance Team","gate":"expand / iterate / stop decision backed by evidence"}
]
out={"schema_version":1,"registry_updated_at":data.get("updated_at"),"next_executable_task":next_task,"growth_loop":stages,
"rules":{"external_blocker_policy":"preserve evidence and skip until new recovery evidence","unknown_revenue_policy":"unknown is never coerced to zero","expansion_policy":"expand only from measured demand/conversion evidence; do not mass-generate thin pages","user_gate_policy":"CAPTCHA/OTP/legal consent/payment/forced identity verification only"}}
print(json.dumps(out,ensure_ascii=False,indent=2))
