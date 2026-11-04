"""Token protection mechanism for IndoSlang-NLP.

Protects placeholders, official acronyms, product codes, units, and years
from being modified by case-folding, leetspeak, de-elongation, and reduplication.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Set, Tuple

# Placeholder pattern for system-generated tags
PLACEHOLDER_PATTERN = re.compile(r"<(?:USER|PHONE|EMAIL|ID_NUMBER|ACCOUNT|EMOJI_[A-Za-z0-9_]+)>")

# Numeric exclusions: product codes, units, currencies, years
# Examples: 100rb, 50k, 2024, mp4, 4k, 3x, co2, h2h, v8, covid19
NUMERIC_EXCLUSION_PATTERN = re.compile(
    r"\b(?:"
    r"\d+(?:rb|k|jt|m|b)|"       # currency / quantity: 100rb, 50k, 10jt
    r"\d+x|"                      # multiplier: 3x, 5x
    r"(?:19|20)\d{2}|"            # years: 1999, 2024
    r"mp[34]|"                    # audio/video: mp3, mp4
    r"[248]k|"                    # resolution: 2k, 4k, 8k
    r"v\d+|"                      # engine/version: v8, v6
    r"co2|h2h|covid\d*"           # chemistry, h2h, covid19
    r")\b",
    re.IGNORECASE
)

# Control character sentinels for masking (using lowercase to survive lowercasing)
SENTINEL_PREFIX = "\x02p_"
SENTINEL_SUFFIX = "\x03"
SENTINEL_PATTERN = re.compile(r"\x02p_(\d+)\x03", re.IGNORECASE)


def load_official_acronyms(path: str | None = None) -> Set[str]:
    """Load official Indonesian and international acronyms from file."""
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "data", "rules", "official_acronyms.txt")
    
    acronyms: Set[str] = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    acronyms.add(line.upper())
    return acronyms


class TokenProtector:
    """Manages token protection throughout the normalization pipeline."""

    def __init__(self, official_acronyms: Set[str] | None = None, preserve_acronyms: bool = True) -> None:
        self.official_acronyms: Set[str] = official_acronyms if official_acronyms is not None else load_official_acronyms()
        self.preserve_acronyms = preserve_acronyms

    def is_numeric_exclusion(self, token: str) -> bool:
        """Check if a token matches numeric / code / currency exclusions."""
        return bool(NUMERIC_EXCLUSION_PATTERN.fullmatch(token.strip()))

    def is_placeholder(self, token: str) -> bool:
        """Check if a token is a system placeholder."""
        return bool(PLACEHOLDER_PATTERN.fullmatch(token.strip()))

    def protect(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Find all protected tokens in text and replace them with sentinels.
        
        Returns:
            Tuple of (masked_text, protected_mapping)
        """
        protected_map: Dict[str, str] = {}
        idx = 0

        # Collect spans to protect: (start, end, original_text)
        spans: List[Tuple[int, int, str]] = []

        # 1. System placeholders (<USER>, <PHONE>, etc.)
        for m in PLACEHOLDER_PATTERN.finditer(text):
            spans.append((m.start(), m.end(), m.group()))

        # 2. Official acronyms (if preserve_acronyms=True)
        # Matches word tokens that are all-uppercase and in official_acronyms
        if self.preserve_acronyms and self.official_acronyms:
            for m in re.finditer(r"\b[A-Z0-9]{2,10}\b", text):
                token = m.group()
                if token in self.official_acronyms:
                    spans.append((m.start(), m.end(), token))

        # 3. Numeric exclusions (100rb, 2024, mp4, 4k, 3x, co2, h2h, covid19)
        for m in NUMERIC_EXCLUSION_PATTERN.finditer(text):
            spans.append((m.start(), m.end(), m.group()))

        if not spans:
            return text, protected_map

        # Sort spans by start asc, length desc, and resolve overlaps
        spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
        non_overlapping: List[Tuple[int, int, str]] = []
        last_end = -1
        for start, end, orig in spans:
            if start >= last_end:
                non_overlapping.append((start, end, orig))
                last_end = end

        # Construct masked text
        result_parts: List[str] = []
        cursor = 0
        for start, end, orig in non_overlapping:
            result_parts.append(text[cursor:start])
            sentinel = f"{SENTINEL_PREFIX}{idx}{SENTINEL_SUFFIX}"
            protected_map[sentinel] = orig
            result_parts.append(sentinel)
            idx += 1
            cursor = end
        result_parts.append(text[cursor:])

        return "".join(result_parts), protected_map

    @staticmethod
    def restore(text: str, protected_map: Dict[str, str]) -> str:
        """Restore all sentinels in text back to their original protected tokens."""
        if not protected_map:
            return text

        lower_map = {k.lower(): v for k, v in protected_map.items()}

        def repl(match: re.Match[str]) -> str:
            sentinel = match.group(0).lower()
            return lower_map.get(sentinel, match.group(0))

        return SENTINEL_PATTERN.sub(repl, text)
