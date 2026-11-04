"""Reduplication and clitic resolution for IndoSlang-NLP.

Resolves informal reduplication patterns written with number '2' (e.g. buku2 -> buku-buku,
temen2nya -> teman-temannya) while respecting exclusions.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

# Reduplication pattern: word of at least 2 alphabetic characters, followed by 2,
# with optional clitics (nya, ku, mu)
# Examples: buku2 -> buku-buku, temen2nya -> teman-temannya, mobil2ku -> mobil-mobilku
REDUP_PATTERN = re.compile(
    r"\b([A-Za-z]{2,})2(nya|ku|mu)?\b"
)


class ReduplicationResolver:
    """Expands Indonesian informal reduplications with affix clitics."""

    def __init__(self, base_map: Optional[Dict[str, str]] = None) -> None:
        self.base_map = base_map or {}

    def set_base_map(self, base_map: Dict[str, str]) -> None:
        """Update base word normalization mapping."""
        self.base_map = base_map

    def expand(self, text: str, base_map: Optional[Dict[str, str]] = None) -> str:
        """Expand all valid reduplication patterns in text."""
        mapping = base_map if base_map is not None else self.base_map

        def repl(match: re.Match[str]) -> str:
            base = match.group(1)
            clitic = match.group(2) or ""

            # Check if base has a direct normalized form (e.g. temen -> teman, org -> orang)
            norm_base = mapping.get(base.lower(), base.lower())

            # Preserve case
            if base.isupper():
                norm_base_upper = norm_base.upper()
                clitic_str = clitic.upper()
                return f"{norm_base_upper}-{norm_base_upper}{clitic_str}"
            elif base[0].isupper() and base[1:].islower():
                return f"{norm_base.capitalize()}-{norm_base.lower()}{clitic}"
            else:
                return f"{norm_base}-{norm_base}{clitic}"

        return REDUP_PATTERN.sub(repl, text)
