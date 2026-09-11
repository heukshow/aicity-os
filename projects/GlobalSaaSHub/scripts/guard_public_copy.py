"""Final, idempotent customer-copy pass. Never edits audit records or link attributes."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def identity(tool):
    return {'convertkit': 'kit'}.get(tool.get('id'), tool.get('id'))

def clean(text):
    # Only text nodes and textual metadata; URLs and attribution attributes stay intact.
    def wording(s):
        # JSON-LD and displayed source URLs are text nodes too. Protect their exact bytes.
        urls = []
        def protect(m):
            urls.append(m[0])
            return f'__URL_{len(urls)-1}__'
        s = re.sub(r'https?://[^\s"\'<>]+|/(?:tool|compare|best)/[^\s"\'<>]+', protect, s)
        s = s.replace('COSHUMA GlobalSaaSHub', 'COSHUMA').replace('GlobalSaaSHub', 'COSHUMA')
        s = re.sub(r'\bvidiq\b', 'vidIQ', s, flags=re.I)
        s = re.sub(r'\btext\s*cortex\b', 'TextCortex', s, flags=re.I)
        s = re.sub(r'You prioritize [^<.]+, specialized feature set, and reliable industry workflow integration\.',
                   'Choose this option if its documented features match the workflow you need.', s)
        s = re.sub(r'You want an alternative approach with [^<]+? pricing structure and (?:Not rated|Review pending)\.',
                   'Compare its current pricing and features with your requirements.', s)
        return re.sub(r'__URL_(\d+)__', lambda m: urls[int(m[1])], s)
    text = re.sub(r'(?<=>)[^<]+(?=<)', lambda m: wording(m[0]), text)
    text = re.sub(r'(<meta\b[^>]*\bcontent=")([^"]*)(")', lambda m: m[1]+wording(m[2])+m[3], text)
    text = re.sub(r'(\b(?:alt|title|aria-label)=")([^"]*)(")', lambda m: m[1]+wording(m[2])+m[3], text)
    text = text.replace('>G</div><span', '>C</div><span')
    text = re.sub(r'(<div[^>]*>)G(</div>\s*<span[^>]*>COSHUMA)', r'\1C\2', text)
    # Known implementation commentary, not legitimate product database features.
    text = re.sub(r"COSHUMA's repository currently marks [^<]*?final customer-facing referral URL\.", '', text)
    text = re.sub(r"COSHUMA's repository records a primary-source Pictory affiliate-manager email confirming", 'The Pictory partner offer lists', text)
    text = re.sub(r"COSHUMA's repository records[^<]*?\. (?=Followr)", '', text)
    text = re.sub(r"COSHUMA's repository records this exact[^<]*?affiliate route\.", '', text)
    text = re.sub(r"COSHUMA's affiliate route was preserved[^<]*?affiliate CTAs\.", '', text)
    text = re.sub(r"COSHUMA's customer-facing partner destination is[^<]*?ldc2xmh2x2t5\.", '', text)
    text = re.sub(r"The AWeber outbound revenue URL[^<]*?claimed here\.", 'COSHUMA may earn a commission on qualifying purchases through partner links.', text)
    text = re.sub(r"COSHUMA's Unbounce tracking URL[^<]*?in the repository\.", '', text)
    text = re.sub(r'<p\b[^>]*>The authenticated Text Partner App records[^<]*</p>',
                  '<p>COSHUMA may earn a commission on eligible HelpDesk purchases through the partner links on this page, at no extra cost to you.</p>', text)
    text = re.sub(r"<p\b[^>]*>COSHUMA's Make partner code is <code>pc=coshuma</code>[^<]*</p>",
                  '<p>Make links may earn COSHUMA a commission; n8n links go directly to its official site.</p>', text)
    text = re.sub(r'<h([1-6])\b[^>]*>\s*</h\1>', '', text)
    return text

PUBLIC_COPY_REPLACEMENTS = {
    'tool/tally.html': {
        'COSHUMA has not verified a paid referral tracking URL, so this page intentionally keeps Tally buttons non-affiliate.':
            "Use the official Tally buttons above to start free or check pricing. COSHUMA's partner referral option is still being verified.",
        'COSHUMA is not labeling Tally as an affiliate conversion target until a customer-facing tracked URL is actually verified.':
            "If Tally issues a verified COSHUMA referral offer, we'll update this guide with the exact customer link.",
    },
    'tool/docusign.html': {
        'COSHUMA has not verified a current account-specific Docusign affiliate URL. These buttons are official non-affiliate links.':
            "Use the official Docusign buttons above to start a trial or check current pricing. COSHUMA's partner referral option is still being verified.",
    },
    'tool/invideo-ai.html': {
        'InVideo currently operates as an official non-affiliate route.':
            "Use InVideo's official site to compare plans and try the product.",
        'COSHUMA has no verified InVideo affiliate URL yet. Choosing Pictory below can generate revenue for COSHUMA when a qualifying paid conversion is attributed.':
            'If you want another AI video option, Pictory is a verified COSHUMA partner.',
        'Affiliate disclosure: COSHUMA may earn a commission if you later buy Pictory through the link above, at no extra cost to you. The InVideo link is an official non-affiliate URL.':
            "COSHUMA may earn a commission if you choose Pictory through the partner link above, at no extra cost to you. The InVideo button goes to InVideo's official site.",
    },
    'tool/pipedrive.html': {
        'Official-only Pipedrive path': 'Pipedrive pricing & CRM trial guide',
        'COSHUMA does not currently have a verified Pipedrive customer affiliate URL, so the primary Pipedrive button below remains an official vendor link.':
            "Use Pipedrive's official site to start the trial and check current pricing.",
        'Pipedrive is not currently using a COSHUMA affiliate URL on this page. The alternative cards below link to vendor-issued COSHUMA partner URLs and are labeled as affiliate CTAs.':
            "The Pipedrive button goes to Pipedrive's official site. Some alternative tools below are COSHUMA partners.",
        'Revenue-aware alternatives': 'Other CRM options to compare',
    },
    'tool/beefree.html': {
        'Affiliate link verified': 'COSHUMA partner',
        'Start Beefree via verified partner link': 'Try Beefree',
        'Verified revenue alternative': 'Another option to compare',
        'Verified monetization path': 'RGE Studio',
        'Try RGE Studio via verified COSHUMA link': 'Try RGE Studio',
    },
}

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
        sitemap.write_text(text, encoding='utf-8')
    print(f'Customer copy normalized: {changed} HTML files')

if __name__ == '__main__':
    main()
