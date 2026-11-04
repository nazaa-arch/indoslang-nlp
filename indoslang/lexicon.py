"""Aho-Corasick lexicon matching engine for IndoSlang-NLP.

Provides single-pass multi-word and slang replacement with O(N + Z) complexity,
supporting both ahocorasick-rs and pure-Python Trie fallback.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Try importing ahocorasick-rs, with fallback to pure-Python Trie
try:
    import ahocorasick_rs
    HAS_AHOCORASICK_RS = True
except ImportError:
    ahocorasick_rs = None  # type: ignore
    HAS_AHOCORASICK_RS = False


@dataclass
class LexiconEntry:
    """A single normalized vocabulary mapping."""
    pattern: str
    normalized: str
    category: str
    confidence: float
    ambiguous: bool
    source: str
    is_multiword: bool
    context_hint: list[str] = field(default_factory=list)


class PureTrieNode:
    """Trie node for pure-Python fallback."""
    def __init__(self) -> None:
        self.children: dict[str, PureTrieNode] = {}
        self.pattern_indices: list[int] = []


class PureTrieMatcher:
    """Pure-Python fallback trie matcher when ahocorasick-rs is unavailable."""

    def __init__(self, patterns: list[str]) -> None:
        self.patterns = patterns
        self.root = PureTrieNode()
        for idx, pat in enumerate(patterns):
            node = self.root
            for ch in pat:
                if ch not in node.children:
                    node.children[ch] = PureTrieNode()
                node = node.children[ch]
            node.pattern_indices.append(idx)

    def find_matches_as_indexes(self, text: str, overlapping: bool = True) -> list[tuple[int, int, int]]:
        """Find matches in text, returning list of (pattern_idx, start, end)."""
        matches: list[tuple[int, int, int]] = []
        text_len = len(text)

        for i in range(text_len):
            node = self.root
            j = i
            while j < text_len and text[j] in node.children:
                node = node.children[text[j]]
                j += 1
                if node.pattern_indices:
                    for pat_idx in node.pattern_indices:
                        matches.append((pat_idx, i, j))

        return matches


class LexiconMatcher:
    """Compiles and executes single-pass lexicon substitution."""

    def __init__(
        self,
        ambiguity_mode: str = "conservative",
        translate_indoglish: bool = False,
        extra_lexicons: list[str | Path] | None = None,
        custom_entries: dict[str, LexiconEntry] | None = None
    ) -> None:
        self.ambiguity_mode = ambiguity_mode
        self.translate_indoglish = translate_indoglish
        self.extra_lexicons = extra_lexicons or []
        self.automaton: Any = None

        # Load all entries
        if custom_entries is not None:
            self.entries = custom_entries
        else:
            self.entries = self._load_all_dictionaries()

        # Build patterns and automaton
        self._compile_automaton()

    def _load_all_dictionaries(self) -> dict[str, LexiconEntry]:
        """Load default dictionaries and apply any extra lexicons."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dict_dir = os.path.join(base_dir, "data", "dictionaries")

        default_files = [
            os.path.join(dict_dir, "abbreviations.json"),
            os.path.join(dict_dir, "slang_base.json"),
            os.path.join(dict_dir, "indoglish.json"),
            os.path.join(dict_dir, "regional_slang.json"),
        ]

        entries: dict[str, LexiconEntry] = {}

        # 1. Load default dictionaries
        for path in default_files:
            if os.path.exists(path):
                self._load_json_dict(path, entries)

        # 2. Load extra lexicons (highest priority, overwriting defaults)
        for extra in self.extra_lexicons:
            if os.path.exists(extra):
                self._load_json_dict(str(extra), entries)

        return entries

    def _load_json_dict(self, path: str, target: dict[str, LexiconEntry]) -> None:
        """Parse dictionary JSON and load into entry map."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for word, val in data.items():
            senses = val.get("senses", [])
            if not senses:
                continue

            # Pick sense based on highest confidence
            best_sense = max(senses, key=lambda s: s.get("confidence", 0.0))
            is_multi = " " in word
            entry = LexiconEntry(
                pattern=word.lower(),
                normalized=best_sense.get("normalized", word),
                category=best_sense.get("category", "general"),
                confidence=best_sense.get("confidence", 1.0),
                ambiguous=val.get("ambiguous", False),
                source=val.get("source", "lexicon"),
                is_multiword=is_multi,
                context_hint=best_sense.get("context_hint", [])
            )
            target[word.lower()] = entry

    def _compile_automaton(self) -> None:
        """Filter patterns based on mode and compile Aho-Corasick automaton."""
        active_entries: list[LexiconEntry] = []

        for entry in self.entries.values():
            # 1. Filter Indoglish if translate_indoglish is False
            if entry.category == "indoglish" and not self.translate_indoglish:
                continue

            # 2. Ambiguity mode filter
            if self.ambiguity_mode in ("conservative", "context_aware") and not entry.is_multiword and (entry.ambiguous or entry.confidence < 0.98):
                continue
            # "aggressive" allows everything

            active_entries.append(entry)

        # Sort patterns: longer patterns first for trie efficiency
        self.active_entries = active_entries
        self.patterns = [e.pattern for e in active_entries]

        if not self.patterns:
            self.automaton = None
            return

        if HAS_AHOCORASICK_RS and ahocorasick_rs is not None:
            self.automaton = ahocorasick_rs.AhoCorasick(self.patterns)
            self.is_rs = True
        else:
            self.automaton = PureTrieMatcher(self.patterns)
            self.is_rs = False

    def __getstate__(self) -> dict[str, Any]:
        """Exclude unpickleable AhoCorasick extension object from state for pickling/multiprocessing."""
        state = self.__dict__.copy()
        state["automaton"] = None
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore state and recompile AhoCorasick automaton."""
        self.__dict__.update(state)
        self._compile_automaton()

    def replace(self, text: str, trace_records: list[dict[str, str]] | None = None) -> str:
        """Replace all matched lexicon patterns in text respecting word boundaries."""
        if not text or not self.patterns or self.automaton is None:
            return text

        # Get all pattern matches with overlap
        matches = self.automaton.find_matches_as_indexes(text, overlapping=True)
        if not matches:
            return text

        text_len = len(text)
        valid_matches: list[tuple[int, int, int]] = []

        # Filter matches for word boundary
        for pat_idx, start, end in matches:
            # Check left boundary: start == 0 or previous char is not alnum
            left_ok = (start == 0) or not (text[start - 1].isalnum() or text[start - 1] == "_")
            # Check right boundary: end == text_len or next char is not alnum
            right_ok = (end == text_len) or not (text[end].isalnum() or text[end] == "_")

            if left_ok and right_ok:
                valid_matches.append((pat_idx, start, end))

        if not valid_matches:
            return text

        # Sort valid matches: start ASC, length DESC (greedy leftmost-longest)
        valid_matches.sort(key=lambda m: (m[1], -(m[2] - m[1])))

        # Resolve overlaps
        selected: list[tuple[int, int, int]] = []
        last_end = 0
        for m in valid_matches:
            if m[1] >= last_end:
                selected.append(m)
                last_end = m[2]

        # Reconstruct text with substitutions
        result_parts: list[str] = []
        cursor = 0
        for pat_idx, start, end in selected:
            entry = self.active_entries[pat_idx]
            result_parts.append(text[cursor:start])
            orig_token = text[start:end]
            replacement = entry.normalized
            result_parts.append(replacement)

            if trace_records is not None:
                trace_records.append({
                    "stage": "lexicon",
                    "original_token": orig_token,
                    "transformed_token": replacement,
                    "rule_source": f"dict_{entry.category}_{entry.source}"
                })
            cursor = end

        result_parts.append(text[cursor:])
        return "".join(result_parts)
