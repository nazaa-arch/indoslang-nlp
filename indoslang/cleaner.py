"""Text sanitization, Unicode NFKC normalization, and cleaner for IndoSlang-NLP."""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Any, List

# URL pattern: http, https, ftp, and www. prefixes
URL_PATTERN = re.compile(
    r"(?:https?://|www\.)[^\s/$.?#].[^\s]*",
    re.IGNORECASE
)

# Hashtag pattern: #word -> extract word
HASHTAG_PATTERN = re.compile(r"#([A-Za-z0-9_]+)")

# Max safe text length before chunking (protect against ReDoS)
MAX_CHUNK_LENGTH = 50000


def is_nan(val: Any) -> bool:
    """Check if value is float NaN."""
    try:
        return isinstance(val, float) and math.isnan(val)
    except Exception:
        return False


def strip_invisible_format_chars(text: str) -> str:
    """Remove Unicode Cf (Format) characters, preserving ZWJ (\\u200d) for emoji sequences."""
    cleaned_chars: List[str] = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat == "Cf":
            # Preserve Zero-Width Joiner (ZWJ) for compound emojis like skin tones/flags
            if ch == "\u200d":
                cleaned_chars.append(ch)
            # Drop zero-width spaces, directional marks, etc.
            continue
        cleaned_chars.append(ch)
    return "".join(cleaned_chars)


class TextCleaner:
    """Performs input sanitization, Unicode NFKC normalization, and social tag cleaning."""

    def __init__(self, clean_social_tags: bool = True) -> None:
        self.clean_social_tags = clean_social_tags

    def sanitize_input(self, text: Any) -> str:
        """Safely ensure input is a string, handling None, NaN, and other types."""
        if text is None or is_nan(text):
            return ""
        if not isinstance(text, str):
            return str(text)
        return text

    def clean(self, raw_text: Any) -> str:
        """Sanitize and clean text."""
        text = self.sanitize_input(raw_text)
        if not text:
            return ""

        # Safe processing for oversized texts
        if len(text) > MAX_CHUNK_LENGTH:
            chunks = [text[i:i + MAX_CHUNK_LENGTH] for i in range(0, len(text), MAX_CHUNK_LENGTH)]
            return "".join(self.clean(chunk) for chunk in chunks)

        # 1. Unicode NFKC Normalization (e.g. 𝗕𝗔𝗡𝗚𝗘𝗧 -> BANGET)
        text = unicodedata.normalize("NFKC", text)

        # 2. Strip invisible format characters (Cf category)
        text = strip_invisible_format_chars(text)

        # 3. Clean social media tags (URLs, hashtags)
        if self.clean_social_tags:
            # Remove URLs
            text = URL_PATTERN.sub(" ", text)
            # Convert #hashtag to plain hashtag text
            text = HASHTAG_PATTERN.sub(r"\1", text)

        return text
