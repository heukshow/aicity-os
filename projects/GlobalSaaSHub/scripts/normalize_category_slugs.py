from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
CAT = PUBLIC / 'category'
SITEMAP = PUBLIC / 'sitemap.xml'

RENAMES = {
    'video.html': 'ai-video.html',
    'voice.html': 'ai-voice.html',
}

for src_name, dst_name in RENAMES.items():
    src = CAT / src_name
    dst = CAT / dst_name
    if not src.exists():
        continue
    text = src.read_text(encoding='utf-8')
    text = text.replace('/category/video.html', '/category/ai-video.html')
    text = text.replace('/category/voice.html', '/category/ai-voice.html')
    dst.write_text(text, encoding='utf-8')
    src.unlink()

if SITEMAP.exists():
    text = SITEMAP.read_text(encoding='utf-8')
    for slug in ('video','voice'):
        text = re.sub(r'\s*<url>\s*<loc>https://coshuma\.com/category/' + slug + r'\.html</loc>.*?</url>\s*', '\n', text, flags=re.S)
    for slug in ('ai-video','ai-voice'):
        url = f'https://coshuma.com/category/{slug}.html'
        if f'<loc>{url}</loc>' not in text and '</urlset>' in text:
            block = f'  <url>\n    <loc>{url}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
            text = text.replace('</urlset>', block + '</urlset>')
    SITEMAP.write_text(text, encoding='utf-8')

print('normalize_category_slugs: done')
