"""Affective signal preservation and feature extraction for IndoSlang-NLP.

Preserves emotion markers (yelling caps ratio, exclamations, questions,
negative emoticons, and word elongation) for downstream sentiment analysis.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

# Negative emojis and emoticons indicating sadness, frustration, or anger
NEGATIVE_EMOJIS_AND_EMOTICONS: set[str] = {
    "😭", "😡", "🤬", "😢", "😠", "👿", "💔", "😞", "😔", "😣", "😫", "😩",
    "🥺", "😤", "😿", "😾",
    ":(", ":-(", ":'(", ":'-(", "D:", "D=", "Dx"
}


@dataclass
class AffectiveFeatures:
    """Extracted affective signals for sentiment/emotion modeling."""
    caps_ratio: float = 0.0
    exclamation_count: int = 0
    question_count: int = 0
    emoticon_negative_count: int = 0
    elongation_count: int = 0
    elongated_tokens: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert features to a dictionary."""
        return asdict(self)


class AffectiveFeatureExtractor:
    """Extracts affective and emotional signals from text."""

    @staticmethod
    def extract_pre_normalization(text: str) -> AffectiveFeatures:
        """Extract features that must be measured before lowercasing and punctuation compression."""
        # 1. Punctuation counts
        exclamation_count = text.count("!")
        question_count = text.count("?")

        # 2. Negative emoticons / emojis count
        emoticon_negative_count = 0
        for item in NEGATIVE_EMOJIS_AND_EMOTICONS:
            emoticon_negative_count += text.count(item)

        # 3. Caps ratio: uppercase letters / total alphabetic characters
        # Filter out system placeholders like <USER>, <PHONE>, etc., so they don't skew ratio
        clean_text_for_caps = re.sub(r"<[A-Z0-9_]+>", "", text)
        letters = [ch for ch in clean_text_for_caps if ch.isalpha()]
        if letters:
            upper_letters = [ch for ch in letters if ch.isupper()]
            caps_ratio = round(len(upper_letters) / len(letters), 4)
        else:
            caps_ratio = 0.0

        return AffectiveFeatures(
            caps_ratio=caps_ratio,
            exclamation_count=exclamation_count,
            question_count=question_count,
            emoticon_negative_count=emoticon_negative_count,
            elongation_count=0,
            elongated_tokens=[]
        )
