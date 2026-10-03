import importlib.util, pathlib
from datetime import datetime, timezone

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "refresh_pricing_backlog.py"
spec = importlib.util.spec_from_file_location("pricing_refresh", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def tool():
    return {"id":"demo","official_url":"https://example.com/","pricing_verified":False}

def proposal(markers=None):
    return {
        "pricing_source_url":"https://example.com/pricing",
        "pricing":"From $19/month",
        "currency":"USD",
        "billing_period":"monthly",
        "pricing_evidence_markers": markers or ["Starter $19 / month","Billed monthly"],
    }

def test_accepts_exact_official_evidence():
    raw="<html><body><div>Starter $19 / month</div><p>Billed monthly</p></body></html>"
    p=m.validate_proposal(tool(),proposal(),{"https://example.com/pricing"},raw,"https://example.com/pricing","2026-10-03T00:00:00Z")
    assert p and p["pricing_verified"] is True and p["pricing_source_http_status"]==200

def test_rejects_missing_marker():
    raw="<html><body>Starter $19 / month</body></html>"
    assert m.validate_proposal(tool(),proposal(),{"https://example.com/pricing"},raw,"https://example.com/pricing","2026-10-03T00:00:00Z") is None

def test_rejects_cross_domain_source():
    q=proposal(); q["pricing_source_url"]="https://evil.example/pricing"
    raw="<html><body>Starter $19 / month Billed monthly</body></html>"
    assert m.validate_proposal(tool(),q,{"https://evil.example/pricing"},raw,"https://evil.example/pricing","2026-10-03T00:00:00Z") is None

def test_rejects_price_not_backed_by_markers():
    q=proposal(); q["pricing"]="From $99/month"
    raw="<html><body>Starter $19 / month Billed monthly</body></html>"
    assert m.validate_proposal(tool(),q,{"https://example.com/pricing"},raw,"https://example.com/pricing","2026-10-03T00:00:00Z") is None

def test_cooldown_blocks_recent_and_allows_old_or_missing_attempts():
    now=datetime(2026,10,3,tzinfo=timezone.utc)
    assert m.cooldown_elapsed({"checked_at":"2026-10-02T23:30:00Z"},now,24) is False
    assert m.cooldown_elapsed({"checked_at":"2026-10-01T23:00:00Z"},now,24) is True
    assert m.cooldown_elapsed({},now,24) is True

if __name__=="__main__":
    for fn in [test_accepts_exact_official_evidence,test_rejects_missing_marker,test_rejects_cross_domain_source,test_rejects_price_not_backed_by_markers,test_cooldown_blocks_recent_and_allows_old_or_missing_attempts]:
        fn()
    print("PASS pricing backlog verifier tests")
