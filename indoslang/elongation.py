"""Contextual, candidate-per-run word de-elongation for IndoSlang-NLP.

Prevents destruction of valid Indonesian words with double letters (saat, maaf, taat,
cemooh, massa) while reducing elongated text (bangeeeettt -> banget, haaaaai -> hai).
"""

from __future__ import annotations

import itertools
import os
import re
from typing import Dict, List, Set, Tuple


def load_whitelist_elongation(path: str | None = None) -> Set[str]:
    """Load whitelist of valid Indonesian double-letter words."""
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "data", "rules", "whitelist_elongation.txt")

    whitelist: Set[str] = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                if w and not w.startswith("#"):
                    whitelist.add(w)
    return whitelist


class DeElongator:
    """Adaptive per-run word de-elongation engine."""

    def __init__(
        self,
        vocab: Set[str],
        whitelist: Set[str] | None = None,
        slang_keys: Set[str] | None = None
    ) -> None:
        self.vocab = vocab
        self.whitelist = whitelist if whitelist is not None else load_whitelist_elongation()
        self.slang_keys = slang_keys or set()

    def de_elongate_token(self, token: str) -> Tuple[str, bool]:
        """De-elongate a single token.
        
        Returns:
            Tuple of (normalized_token, was_elongated)
        """
        # Lowercase for dictionary checks
        lower_token = token.lower()

        # 1. Non-destructive: if token is already in whitelist or vocab, keep original
        if lower_token in self.whitelist or lower_token in self.vocab:
            return token, False

        # 2. Identify runs of repeated consecutive identical letters
        # Run matches: ([a-z])\1+
        runs: List[Tuple[int, int, str, int]] = []  # (start, end, char, length)
        for m in re.finditer(r"([a-zA-Z])\1+", token):
            runs.append((m.start(), m.end(), m.group(1).lower(), len(m.group(0))))

        if not runs:
            return token, False

        # Check if any run >= 3, or run == 2 for a token outside vocab
        has_significant_run = any(length >= 3 for _, _, _, length in runs)
        if not has_significant_run and lower_token in self.slang_keys:
            return token, False

        # 3. Generate candidate variations per-run (1 or 2 letters per run)
        # Limit to 4 runs (max 2^4 = 16 candidates)
        effective_runs = runs[:4]
        run_options: List[List[str]] = []
        for _, _, ch, length in effective_runs:
            if length >= 3:
                run_options.append([ch, ch * 2])
            else:  # length == 2
                run_options.append([ch, ch * 2])

        # Reconstruct candidates
        candidates: List[str] = []
        for combo in itertools.product(*run_options):
            parts: List[str] = []
            cursor = 0
            for (start, end, _, _), replacement in zip(effective_runs, combo):
                parts.append(lower_token[cursor:start])
                parts.append(replacement)
                cursor = end
            parts.append(lower_token[cursor:])
            candidate = "".join(parts)
            candidates.append(candidate)

        # 4. Filter and select best candidate
        # Priority 1: Match in whitelist (e.g. saat, maaf, cemooh)
        for cand in candidates:
            if cand in self.whitelist:
                return self._match_case(token, cand), True

        # Priority 2: Match in standard vocabulary
        # Prefer candidate with minimal changes or in vocab
        # If candidate is in vocab, check if it's not the original
        vocab_matches = [c for c in candidates if c in self.vocab]
        if vocab_matches:
            # Sort: prefer candidate with shortest length if elongating (e.g. 'banget' over 'bangeet')
            # but if whitelist has it, whitelist won earlier
            best = min(vocab_matches, key=len)
            return self._match_case(token, best), True

        # Priority 3: Match in slang dictionary (e.g. 'sih', 'ya', 'woi', 'kureng')
        slang_matches = [c for c in candidates if c in self.slang_keys]
        if slang_matches:
            best = min(slang_matches, key=len)
            return self._match_case(token, best), True

        # 5. Fallback rule:
        # Run >= 3 compressed to 1 letter; run == 2 left untouched
        fallback_parts: List[str] = []
        cursor = 0
        was_compressed = False
        for start, end, ch, length in runs:
            fallback_parts.append(token[cursor:start])
            if length >= 3:
                fallback_parts.append(token[start])  # Single char
                was_compressed = True
            else:
                fallback_parts.append(token[start:end])  # Keep 2 chars
            cursor = end
        fallback_parts.append(token[cursor:])
        result = "".join(fallback_parts)

        return result, was_compressed

    def process_text(self, text: str) -> Tuple[str, List[str]]:
        """De-elongate all eligible tokens in text.
        
        Returns:
            Tuple of (de_elongated_text, list_of_elongated_tokens_normalized)
        """
        elongated_tokens: List[str] = []

        def repl(match: re.Match[str]) -> str:
            tok = match.group(0)
            norm, was_elong = self.de_elongate_token(tok)
            if was_elong:
                elongated_tokens.append(norm.lower())
            return norm

        # Process alphanumeric words (skip placeholders like <USER> or \x02...)
        result = re.sub(r"[A-Za-z]+", repl, text)
        return result, elongated_tokens

    @staticmethod
    def _match_case(original: str, replacement: str) -> str:
        """Preserve case pattern from original token if all uppercase or capitalized."""
        if original.isupper():
            return replacement.upper()
        if original and original[0].isupper() and original[1:].islower():
            return replacement.capitalize()
        return replacement.lower()
