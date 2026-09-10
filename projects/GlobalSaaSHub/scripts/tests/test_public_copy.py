"""Fail the build for customer-visible legacy branding, state leaks or false comparisons."""
from html.parser import HTMLParser
from pathlib import Path
import re,sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from guard_public_copy import clean

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[];self.hidden=0;self.links=[];self.metadata=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('script','style'):self.hidden+=1
        if tag=='meta':self.metadata.append(a.get('content',''))
        if tag=='a':self.links.append(a)
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.hidden=max(0,self.hidden-1)
    def handle_data(self,data):
        if not self.hidden:self.parts.append(data)

BAD=re.compile(r'GlobalSaaSHub|You prioritize\s+(?:Not rated|Review pending)|pricing structure and\s+(?:Not rated|Review pending)|affiliate_verified|affiliate_status|tools\.next\.json|\brepository\b|tracking_pending|pending_review',re.I)
def violations(html):
    p=Page();p.feed(html)
    return BAD.findall(' '.join(p.parts+p.metadata))

def main():
    # Test split-node leaks and keep valid product terminology / attribution intact.
    assert violations('<p>You prioritize <b>Not rated</b></p>')
    assert violations('<meta name="description" content="GlobalSaaSHub">')
    assert not violations('<p>Connect your internal database.</p><a data-affiliate-status="approved_tracking" href="https://example.com/?ref=ok">Try</a>')
    urls = '<meta property="og:url" content="https://coshuma.com/tool/vidiq.html"><script type="application/ld+json">{"url":"https://coshuma.com/tool/vidiq.html"}</script><a href="https://example.com/?via=GlobalSaaSHub">Text Cortex</a>'
    assert clean(urls) == urls.replace('>Text Cortex<', '>TextCortex<')
    root=Path(sys.argv[1] if len(sys.argv)>1 else 'dist')
    files=list(root.rglob('*.html'))
    assert len(files)>400, f'Incomplete build: {len(files)} HTML files'
    errors=[]
    for path in files:
        html=path.read_text(encoding='utf-8');bad=violations(html)
        if bad:errors.append(f'{path}: {sorted(set(bad))}')
        if re.search(r'\bText Cortex\b', html):errors.append(f'{path}: inconsistent TextCortex brand')
        if re.search(r'<h([1-6])\b[^>]*>\s*</h\1>',html):errors.append(f'{path}: empty heading')
    explanation=(root/'compare/kit-vs-convertkit.html').read_text(encoding='utf-8')
    assert 'same email marketing platform' in explanation
    assert 'href="https://coshuma.com/tool/kit.html"' in explanation
    kit=(root/'tool/kit.html').read_text(encoding='utf-8')
    assert 'href="/tool/convertkit.html"' not in kit
    assert 'Top Alternatives to Nudgera' not in (root/'tool/nudgera.html').read_text(encoding='utf-8')
    assert not errors, '\n'.join(errors)
    print(f'PASS: {len(files)} built HTML files; legacy brand=0, broken rating copy=0, internal-state copy=0, empty headings=0')

if __name__=='__main__':main()
