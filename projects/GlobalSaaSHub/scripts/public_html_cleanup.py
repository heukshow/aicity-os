"""Remove empty presentation markup without deleting interactive or accessible nodes."""
from __future__ import annotations

from html.parser import HTMLParser
import re


class _ParagraphAttributes(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.names: set[str] = set()

    def handle_starttag(self, tag, attrs):
        self.names.update(name for name, _ in attrs)


def remove_empty_presentational_paragraphs(text: str) -> str:
    def clean(match: re.Match[str]) -> str:
        attributes = _ParagraphAttributes()
        attributes.feed(match.group(0))
        # IDs, roles, ARIA, data and other attributes can identify live message or
        # interaction targets. An initially empty node is still functional markup.
        if attributes.names - {"class", "style"}:
            return match.group(0)
        return ""

    return re.sub(r"<p\b[^>]*>\s*</p>", clean, text, flags=re.I)
