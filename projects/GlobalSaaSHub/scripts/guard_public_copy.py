"""Final, idempotent customer-copy pass. Never edits audit records or link attributes."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

STANDARD_AFFILIATE_DISCLOSURE = (
    '<p data-affiliate-disclosure="compare" class="text-[11px] leading-relaxed text-slate-500">'
    'Affiliate disclosure: COSHUMA may earn an affiliate commission when you purchase through partner links on this page, at no extra cost to you. '
    '<a href="/affiliate-disclosure.html" class="underline hover:text-slate-300">How this works</a>.'
    '</p>'
)

def identity(tool):
    return {'convertkit': 'kit'}.get(tool.get('id'), tool.get('id'))

def clean(text):
    def wording(s):
        urls = []
        def protect(m):
            urls.append(m[0])
            return f'__URL_{len(urls)-1}__'
        s = re.sub(r'https?://[^\s"\'<>]+|/(?:tool|compare|best)/[^\s"\'<>]+', protect, s)
        s = s.replace('COSHUMA GlobalSaaSHub', 'COSHUMA').replace('GlobalSaaSHub', 'COSHUMA')
        s = re.sub(r'\bvidiq\b', 'vidIQ', s, flags=re.I)
        s = re.sub(r'\btext\s*cortex\b', 'TextCortex', s, flags=re.I)
        s = re.sub(r'You prioritize [^<.]+, specialized feature set, and reliable industry workflow integration\.', 'Choose this option if its documented features match the workflow you need.', s)
        s = re.sub(r'You want an alternative approach with [^<]+? pricing structure and (?:Not rated|Review pending)\.', 'Compare its current pricing and features with your requirements.', s)
        return re.sub(r'__URL_(\d+)__', lambda m: urls[int(m[1])], s)
    text = re.sub(r'(?<=>)[^<]+(?=<)', lambda m: wording(m[0]), text)
    text = re.sub(r'(<meta\b[^>]*\bcontent=")([^"]*)(")', lambda m: m[1]+wording(m[2])+m[3], text)
    text = re.sub(r'(\b(?:alt|title|aria-label)=")([^"]*)(")', lambda m: m[1]+wording(m[2])+m[3], text)
    text = text.replace('>G</div><span', '>C</div><span')
    text = re.sub(r'(<div[^>]*>)G(</div>\s*<span[^>]*>COSHUMA)', r'\1C\2', text)
    text = re.sub(r"COSHUMA's repository currently marks [^<]*?final customer-facing referral URL\.", '', text)
    text = re.sub(r"COSHUMA's repository records a primary-source Pictory affiliate-manager email confirming", 'The Pictory partner offer lists', text)
    text = re.sub(r"COSHUMA's repository records[^<]*?\. (?=Followr)", '', text)
    text = re.sub(r"COSHUMA's repository records this exact[^<]*?affiliate route\.", '', text)
    text = re.sub(r"COSHUMA's affiliate route was preserved[^<]*?affiliate CTAs\.", '', text)
    text = re.sub(r"COSHUMA's customer-facing partner destination is[^<]*?ldc2xmh2x2t5\.", '', text)
    text = re.sub(r"The AWeber outbound revenue URL[^<]*?claimed here\.", 'COSHUMA may earn a commission on qualifying purchases through partner links.', text)
    text = re.sub(r"COSHUMA's Unbounce tracking URL[^<]*?in the repository\.", '', text)
    text = re.sub(r'<p\b[^>]*>The authenticated Text Partner App records[^<]*</p>', '<p>COSHUMA may earn a commission on eligible HelpDesk purchases through the partner links on this page, at no extra cost to you.</p>', text)
    text = re.sub(r"<p\b[^>]*>COSHUMA's Make partner code is <code>pc=coshuma</code>[^<]*</p>", '<p>Make links may earn COSHUMA a commission; n8n links go directly to its official site.</p>', text)
    text = re.sub(r'<h([1-6])\b[^>]*>\s*</h\1>', '', text)
    return text

PUBLIC_COPY_REPLACEMENTS = {
    'tool/tally.html': {
        'COSHUMA has not verified a paid referral tracking URL, so this page intentionally keeps Tally buttons non-affiliate.': '',
        'COSHUMA is not labeling Tally as an affiliate conversion target until a customer-facing tracked URL is actually verified.': '',
        'COSHUMA has not verified a current account-specific Tally affiliate URL. These buttons are official non-affiliate links.': '',
        "Use Tally's official site to start free or check current pricing. COSHUMA's partner referral option is still being verified.": '',
    },
    'tool/docusign.html': {
        'COSHUMA has not verified a current account-specific Docusign affiliate URL. These buttons are official non-affiliate links.': '',
        'COSHUMA has not verified a Docusign account-specific affiliate URL. These Docusign buttons are official non-affiliate links.': '',
        "Use Docusign's official site to start a trial or check current pricing. COSHUMA's partner referral option is still being verified.": '',
        'Verified alternative': 'Another option to compare',
        'Compare BoldSign via verified partner link': 'Compare BoldSign',
    },
    'tool/invideo-ai.html': {
        'InVideo currently operates as an official non-affiliate route.': "Use InVideo's official site to compare plans and try the product.",
        'COSHUMA has no verified InVideo affiliate URL yet. Choosing Pictory below can generate revenue for COSHUMA when a qualifying paid conversion is attributed.': 'If you want another AI video option, compare Pictory below.',
        'InVideo currently operates an affiliate program through Impact, but COSHUMA has not yet verified an account-specific customer tracking URL. Until that exact issued URL is recovered, these InVideo buttons intentionally remain official non-affiliate links.': '',
        "Use InVideo's official buttons above to try the product or compare plans. COSHUMA's partner referral option is still being verified.": '',
        'Alternative with a verified COSHUMA offer': 'Another AI video option to compare',
        "COSHUMA's exact Pictory affiliate link has been confirmed by Pictory's affiliate manager, and code <strong>COSHUMA20</strong> remains the vendor-confirmed promotion code.": 'Code <strong>COSHUMA20</strong> is the current Pictory partner promotion code.',
    },
    'tool/pipedrive.html': {
        'Official-only Pipedrive path': 'Pipedrive pricing & CRM trial guide',
        'COSHUMA does not currently have a verified Pipedrive customer affiliate URL, so the primary Pipedrive button below remains an official vendor link.': "Use Pipedrive's official site to start the trial and check current pricing.",
        'Pipedrive is not currently using a COSHUMA affiliate URL on this page. The alternative cards below link to vendor-issued COSHUMA partner URLs and are labeled as affiliate CTAs.': "The Pipedrive button goes to Pipedrive's official site. Some alternative tools below are COSHUMA partners.",
        'Revenue-aware alternatives': 'Other CRM options to compare',
        "This guide keeps Pipedrive on official non-affiliate links and uses COSHUMA's separately verified HighLevel partner link only for visitors who need a broader agency stack.": 'Use Pipedrive for a focused sales CRM. Compare HighLevel if you need a broader agency stack with funnels, messaging, calendars and automation.',
        'Verified revenue alternative': 'Agency-focused alternative',
        'Try HighLevel via verified COSHUMA link': 'Try HighLevel',
        'HighLevel verified partner link →': 'HighLevel pricing & trial →',
        "Source check: Pipedrive official pricing and plan documentation, plus HighLevel official pricing, verified Sep 10, 2026. COSHUMA's Pipedrive affiliate application remains separate from this page; no Pipedrive revenue attribution is claimed until an exact customer-facing tracking link is verified.": 'Source check: Pipedrive and HighLevel official pricing and plan documentation, verified Sep 10, 2026. Check each vendor for current terms before purchasing.',
    },
    'tool/beefree.html': {
        'Affiliate link verified': 'COSHUMA partner',
        'Start Beefree via verified partner link': 'Try Beefree',
        'Verified revenue alternative': 'Another option to compare',
        'Verified monetization path': 'RGE Studio',
        'Try RGE Studio via verified COSHUMA link': 'Try RGE Studio',
        'COSHUMA partner Sep 9, 2026': 'RGE Studio partner guide',
        'Start RGE Studio via verified partner link →': 'Try RGE Studio →',
        'Start RGE Studio via verified COSHUMA link →': 'Try RGE Studio →',
        'Try AWeber via verified COSHUMA link →': 'Try AWeber →',
    },
}

def normalize_affiliate_disclosure(text):
    if 'Affiliate Disclosure | COSHUMA' in text:
        return text
    has_affiliate = 'data-cta="affiliate"' in text
    text = re.sub(r'<p\b[^>]*data-affiliate-disclosure="[^"]*"[^>]*>.*?</p>', '', text, flags=re.S)
    text = re.sub(r'<p\b[^>]*>\s*Affiliate disclosure:.*?</p>', '', text, flags=re.S | re.I)
    text = re.sub(r'<p\b[^>]*>(?:(?!</p>).)*COSHUMA may earn (?:an affiliate )?commission(?:(?!</p>).)*</p>', '', text, flags=re.S | re.I)
    text = re.sub(r'<p\b[^>]*>(?:(?!</p>).)*may earn COSHUMA a commission(?:(?!</p>).)*</p>', '', text, flags=re.S | re.I)
    legacy_trust_disclosure = ('<div><div class="text-[10px] uppercase tracking-wider text-slate-500">Affiliate disclosure</div>' '<div class="mt-1 text-sm text-slate-300">Affiliate destination verified separately from editorial product sources.</div></div>')
    text = text.replace(legacy_trust_disclosure, '')
    if not has_affiliate:
        return text
    return re.sub(r'(<a\b[^>]*data-cta="affiliate"[^>]*>.*?</a>)', r'\1\n' + STANDARD_AFFILIATE_DISCLOSURE, text, count=1, flags=re.S)

def page_copy(path, text):
    if path.parent.name == 'tool' and path.stem in ('kit', 'convertkit'):
        other = 'convertkit' if path.stem == 'kit' else 'kit'
        text = re.sub(r'<a href="/tool/'+other+r'.html"[^>]*>.*?</a>', '', text, flags=re.S)
        text = text.replace('https://www.kit.co/', 'https://kit.com/')
    if path.name == 'nudgera.html':
        text = re.sub(r'<!-- Alternatives & Direct Competitors Section -->.*?(?=<!-- Pricing & Action -->)', '', text, flags=re.S)
    if path.name == 'liftmycv.html':
        text = text.replace('pay-as-you-go, Basic or Unlimited', 'the available credit bundles or subscription plans')
    if path.is_relative_to(ROOT / 'public'):
        rel = path.relative_to(ROOT / 'public').as_posix()
        for source, replacement in PUBLIC_COPY_REPLACEMENTS.get(rel, {}).items():
            text = text.replace(source, replacement)
    if path.name != 'affiliate-disclosure.html':
        text = normalize_affiliate_disclosure(text)
    return text

def main():
    changed = 0
    for path in [ROOT/'index.html', *(ROOT/'public').rglob('*.html')]:
        original = path.read_text(encoding='utf-8')
        updated = page_copy(path, clean(original))
        if updated != original:
            path.write_text(updated, encoding='utf-8')
            changed += 1
    for source in (ROOT/'scripts/public-copy-templates').glob('*.html'):
        folder = 'compare' if source.name == 'kit-vs-convertkit.html' else 'tool'
        (ROOT/'public'/folder/source.name).write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
    sitemap = ROOT/'public/sitemap.xml'
    if sitemap.exists():
        text = sitemap.read_text(encoding='utf-8')
        text = re.sub(r'\s*<url>\s*<loc>https://coshuma.com/(?:tool/merlin-ai|compare/kit-vs-convertkit)\.html</loc>.*?</url>', '', text, flags=re.S)
        disclosure_url = '<url><loc>https://coshuma.com/affiliate-disclosure.html</loc></url>'
        if 'https://coshuma.com/affiliate-disclosure.html' not in text and '</urlset>' in text:
            text = text.replace('</urlset>', f'  {disclosure_url}\n</urlset>')
        sitemap.write_text(text, encoding='utf-8')
    print(f'Customer copy normalized: {changed} HTML files')

if __name__ == '__main__':
    main()
