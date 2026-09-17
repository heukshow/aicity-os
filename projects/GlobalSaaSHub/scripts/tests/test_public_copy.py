"""Fail the build for customer-visible legacy branding, state leaks, secrets or internal operations copy."""
from html.parser import HTMLParser
from pathlib import Path
import re,sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from guard_public_copy import clean
from security_guard import main as security_main

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

BAD=re.compile(
    r'GlobalSaaSHub|'
    r'You prioritize\s+(?:Not rated|Review pending)|'
    r'pricing structure and\s+(?:Not rated|Review pending)|'
    r'affiliate_verified|affiliate_status|tools\.next\.json|\brepository\b|tracking_pending|pending_review|'
    r'Verified affiliate paths|Check verified offer|Affiliate link verified in our records|'
    r'Verified low-friction buyer routes|Start with a tracked trial|'
    r'customer-facing destinations were supplied directly by the partner programs|'
    r'COSHUMA does not invent referral parameters|'
    r'Verified revenue alternative|via verified COSHUMA link|'
    r'Separate link verification|Recently verified partner buyer guides|'
    r'Fill eSignature pricing & verified partner offer|'
    r'\b(?:affiliate|partner|referral)-status\b|'
    r'\bAffiliate status\b|'
    r'\bOfficial pricing and affiliate pages checked\b|'
    r'\bFind the right verified route\b|'
    r'Affiliate destinations, vendor terms and revenue evidence|'
    r'\bVerified SaaS Free Trials & Partner Offers\b|'
    r'\bSoftware free trials and partner offers worth testing before you pay\b|'
    r'\bCurrent Pictory partner offer\b|'
    r'\bverified\s+(?:Impact|PartnerStack|Dub|Cello)\b[^.]{0,60}\b(?:route|link|status)\b|'
    r'COSHUMA[^.]{0,80}affiliate application remains separate|'
    r'no Pipedrive revenue attribution is claimed',
    re.I,
)
LLMS_BAD=re.compile(
    r'PartnerStack|Cello referral route|Impact (?:partner-)?route|Dub partner route|'
    r'\b(?:affiliate|partner|referral)-status\b|'
    r'verified partner route|verified affiliate route|verified customer referral route|'
    r'non-affiliate|signup, sale, commission or revenue event|'
    r'How COSHUMA verifies public sources, affiliate links',
    re.I,
)
def violations(html):
    p=Page();p.feed(html)
    return BAD.findall(' '.join(p.parts+p.metadata))

def main():
    assert violations('<p>You prioritize <b>Not rated</b></p>')
    assert violations('<meta name="description" content="GlobalSaaSHub">')
    assert violations('<p>Affiliate link verified in our records · disclosure applies</p>')
    assert violations('<p>Recently verified partner buyer guides</p>')
    assert violations('<p>Pricing and affiliate-status buyer guide</p>')
    assert violations('<h2>Affiliate status</h2>')
    assert violations('<p>Find the right verified route</p>')
    assert not violations('<p>Affiliate disclosure: COSHUMA may earn a commission from some links at no extra cost to you.</p>')
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
    llms_path=root/'llms.txt'
    assert llms_path.exists(), 'Missing dist/llms.txt'
    llms=llms_path.read_text(encoding='utf-8')
    assert not LLMS_BAD.search(llms), 'Internal affiliate/network/status copy remains in dist/llms.txt'
    explanation=(root/'compare/kit-vs-convertkit.html').read_text(encoding='utf-8')
    assert 'same email marketing platform' in explanation
    assert 'href="https://coshuma.com/tool/kit.html"' in explanation
    kit=(root/'tool/kit.html').read_text(encoding='utf-8')
    assert 'href="/tool/convertkit.html"' not in kit
    assert 'Top Alternatives to Nudgera' not in (root/'tool/nudgera.html').read_text(encoding='utf-8')
    deals=(root/'best/verified-software-free-trials-deals.html').read_text(encoding='utf-8')
    for leaked in (
        'customer-facing PartnerStack route',
        'partner-side evidence',
        'partner correspondence',
        'guessing referral parameters',
        'existing affiliate account',
        "Jotform's affiliate team supplied",
    ):
        assert leaked not in deals, f'Internal buyer-hub copy remains: {leaked}'
    assert not errors, '\n'.join(errors)
    security_main()
    print(f'PASS: {len(files)} built HTML files; legacy brand=0, broken rating copy=0, internal-state copy=0, internal-affiliate-copy=0, llms-internal-copy=0, empty headings=0, security guard=pass')

if __name__=='__main__':main()
