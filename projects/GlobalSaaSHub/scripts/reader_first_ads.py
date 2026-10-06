"""Install shared reader-first presentation on the existing house-ad pages only."""
STYLE = '<link rel="stylesheet" href="/reader-first-ads.css?v=20261006" />'
SCRIPT = '<script defer src="/reader-first-ads.js?v=20261006"></script>'
def reader_style(text):
    if text.count('</head>') != 1 or text.count('</body>') != 1:
        raise ValueError('Missing unique document boundary')
    text = text.replace('src="/affiliate-attribution.js"', 'src="/affiliate-attribution.js?v=reader-20261006"')
    if STYLE not in text:
        text = text.replace('</head>', STYLE + '</head>', 1)
    if SCRIPT not in text:
        text = text.replace('</body>', SCRIPT + '</body>', 1)
    return text
