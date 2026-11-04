"""Leetspeak and algospeak decoding with vocabulary verification for IndoSlang-NLP.

Prevents blind substitutions so numeric data, product codes, and currencies
remain uncorrupted.
"""

from __future__ import annotations

import itertools
import json
import os
import re
from typing import Dict, List, Set


def load_leetspeak_map(path: str | None = None) -> Dict[str, List[str]]:
    """Load leetspeak substitution map from JSON file."""
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "data", "rules", "leetspeak_map.json")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Fallback default map
    return {
        "0": ["o"],
        "1": ["i", "l"],
        "3": ["e"],
        "4": ["a"],
        "5": ["s"],
        "7": ["t"],
        "8": ["b"],
        "!": ["i"],
        "@": ["a"],
        "$": ["s"]
    }


class LeetspeakDecoder:
    """Decodes masked or leetspeak words by validating against known vocabulary."""

    def __init__(
        self,
        vocab: Set[str],
        slang_keys: Set[str] | None = None,
        leetspeak_map: Dict[str, List[str]] | None = None,
        max_candidates: int = 64
    ) -> None:
        self.vocab = vocab
        self.slang_keys = slang_keys or set()
        self.leetspeak_map = leetspeak_map or load_leetspeak_map()
        self.max_candidates = max_candidates
        self.leet_chars = set(self.leetspeak_map.keys())

    def decode_token(self, token: str) -> str:
        """Decode a single token if it represents valid leetspeak."""
        # 1. Skip pure digits
        if token.isdigit():
            return token

        # 2. Skip if already valid in vocabulary or slang
        lower_token = token.lower()
        if lower_token in self.vocab or lower_token in self.slang_keys:
            return token

        # 3. Check if token contains leet characters mixed with letters/symbols
        has_leet = any(ch in self.leet_chars for ch in lower_token)
        if not has_leet:
            return token

        # 4. Generate candidate word variations
        char_options: List[List[str]] = []
        ambiguous_count = 0

        for ch in lower_token:
            if ch in self.leetspeak_map:
                options = self.leetspeak_map[ch]
                char_options.append(options)
                if len(options) > 1:
                    ambiguous_count += 1
            else:
                char_options.append([ch])

        # Limit combinatorial explosion (2^6 = 64 candidates)
        if 2 ** ambiguous_count > self.max_candidates:
            # Fall back to first option for each character
            char_options = [[opts[0]] if len(opts) > 1 else opts for opts in char_options]

        candidates = ["".join(p) for p in itertools.islice(itertools.product(*char_options), self.max_candidates)]

        # 5. Check against standard vocab first
        for cand in candidates:
            if cand in self.vocab:
                return cand

        # 6. Check against slang dictionary
        for cand in candidates:
            if cand in self.slang_keys:
                return cand

        # 7. No valid candidate found -> preserve original token
        return token

    def decode_text(self, text: str) -> str:
        """Decode all candidate leetspeak tokens in text."""
        # Split tokens by whitespace or punctuation while preserving structure
        def replace_match(match: re.Match[str]) -> str:
            token = match.group(0)
            return self.decode_token(token)

        # Match tokens containing at least one alphanumeric character
        return re.sub(r"[A-Za-z0-9!@$]+", replace_match, text)
