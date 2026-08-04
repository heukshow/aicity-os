import importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"content_audit.py"; S=importlib.util.spec_from_file_location("content_audit",P); M=importlib.util.module_from_spec(S); S.loader.exec_module(M)
class Tests(unittest.TestCase):
 def test_domains(self): self.assertTrue(M.same_domain("https://example.com","https://app.example.com/x")); self.assertFalse(M.same_domain("https://example.com","https://example.com.evil.test"))
 def test_corpus(self):
  r=M.audit(False,1); self.assertEqual((r["tool_count"],r["detail_pages_checked"],r["compare_pages_checked"],r["sitemap_tool_urls_checked"]),(150,150,231,150)); bad=sum(r["classification_counts"][s] for s in ("BROKEN","STALE","TYPO"))
  if bad: self.fail(json.dumps([(t["id"],t["issues"]) for t in r["tools"] if t["classification"] in {"BROKEN","STALE","TYPO"}],ensure_ascii=False,indent=2))
if __name__=="__main__": unittest.main()
