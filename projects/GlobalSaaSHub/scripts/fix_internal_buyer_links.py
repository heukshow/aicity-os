"""Repair known buyer-path HTML links before production verification.

Keep this exact-match and idempotent. The purpose is to prevent purchase-intent
visitors and crawlers from being sent to internal 404s while preserving topical
navigation.
"""
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
TARGET = PROJECT_DIR / "public" / "compare" / "elevenlabs-vs-murf-ai.html"
OLD = 'href="/compare/index.html">Comparisons</a>'
NEW = 'href="/category/ai-voice.html">AI voice</a>'

text = TARGET.read_text(encoding="utf-8")
if NEW in text:
    print("Internal buyer link already repaired: ElevenLabs vs Murf AI -> AI voice category")
elif OLD in text:
    TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("Repaired broken buyer link: /compare/index.html -> /category/ai-voice.html")
else:
    raise SystemExit("Refusing uncertain link repair: expected ElevenLabs vs Murf breadcrumb not found")
