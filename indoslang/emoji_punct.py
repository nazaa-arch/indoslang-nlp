"""Emoji normalization and punctuation compression for IndoSlang-NLP."""

from __future__ import annotations

import re
from typing import Dict

# Indonesian Demojize dictionary for common emojis
EMOJI_ID_MAP: Dict[str, str] = {
    "😭": "<EMOJI_MENANGIS>",
    "😢": "<EMOJI_SEDIH>",
    "😡": "<EMOJI_MARAH>",
    "🤬": "<EMOJI_KASAR>",
    "😠": "<EMOJI_KESAL>",
    "😂": "<EMOJI_TERTAWA>",
    "🤣": "<EMOJI_TERBAHAK>",
    "😍": "<EMOJI_CINTA>",
    "❤️": "<EMOJI_HATI>",
    "💔": "<EMOJI_PATAH_HATI>",
    "👍": "<EMOJI_JEMPOL>",
    "👎": "<EMOJI_JEMPOL_BAWAH>",
    "🙏": "<EMOJI_BERDOA>",
    "🔥": "<EMOJI_API>",
    "🥺": "<EMOJI_MEMOHON>",
    "😊": "<EMOJI_SENYUM>",
    "🤔": "<EMOJI_BERPIKIR>",
    "💀": "<EMOJI_TENGKORAK>",
    "🤡": "<EMOJI_BADUT>",
    "✨": "<EMOJI_KILAU>",
    "🎉": "<EMOJI_PERAYAAN>",
    "💯": "<EMOJI_SERATUS>",
    "🤦": "<EMOJI_TEPUK_JIDAT>",
    "🤷": "<EMOJI_ANGKAT_BAHU>",
    "😴": "<EMOJI_TIDUR>",
    "🤢": "<EMOJI_MUAL>",
    "🤮": "<EMOJI_MUNTAH>",
    "💩": "<EMOJI_KOTORAN>",
}

# Regex matching Unicode Emoji ranges
EMOJI_PATTERN = re.compile(
    r"["
    r"\U0001F600-\U0001F64F"  # emoticons
    r"\U0001F300-\U0001F5FF"  # symbols & pictographs
    r"\U0001F680-\U0001F6FF"  # transport & map
    r"\U0001F1E0-\U0001F1FF"  # flags
    r"\U0001F900-\U0001F9FF"  # supplemental symbols
    r"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
    r"\U00002702-\U000027B0"
    r"\U000024C2-\U0001F251"
    r"]+",
    flags=re.UNICODE
)


def handle_emoji(text: str, mode: str = "ignore") -> str:
    """Handle emojis in text according to specified mode.
    
    Modes:
        'ignore': Keep emojis as is.
        'remove': Remove all emojis.
        'demojize': Replace known emojis with Indonesian tokens (<EMOJI_...>).
    """
    if mode == "ignore":
        return text

    if mode == "remove":
        return EMOJI_PATTERN.sub("", text)

    if mode == "demojize":
        for emoji_char, token in EMOJI_ID_MAP.items():
            text = text.replace(emoji_char, f" {token} ")
        # Any remaining emojis can either be left or converted to generic token
        text = EMOJI_PATTERN.sub(lambda m: f" <EMOJI_SIMBOL> ", text)
        return text

    return text


def compress_punctuation(text: str, max_repeats: int = 1) -> str:
    """Compress repeated punctuation marks (e.g. ???? -> ?, !!!! -> !).
    
    If max_repeats == 2, '????' -> '??', '!!!!' -> '!!'.
    """
    if max_repeats <= 0:
        max_repeats = 1

    # Match 2 or more repeated punctuation characters: ! ? . , -
    def repl(m: re.Match[str]) -> str:
        ch = m.group(1)
        # Ellipsis standard: '...' kept if max_repeats == 2 or reduced to max_repeats
        return ch * max_repeats

    # Pattern for repeated ! ? . , ; :
    return re.sub(r"([!?,;:~])\1+", repl, text)
