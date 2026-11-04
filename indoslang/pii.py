"""Personally Identifiable Information (PII) detection and masking for IndoSlang-NLP.

Complies with ethical NLP research standards and Indonesian UU No. 27 Tahun 2022
(Pelindungan Data Pribadi).
"""

from __future__ import annotations

import re

# Regex for Indonesian Phone Numbers:
# Covers +628xx, 628xx, 08xx with optional dashes/spaces
PHONE_PATTERN = re.compile(
    r"(?:\+?62|0)8[1-9][0-9\-\s]{7,13}[0-9]\b"
)

# Standard Email pattern
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

# Social media username mention: @username
MENTION_PATTERN = re.compile(
    r"@([A-Za-z0-9_]{1,30})\b"
)

# Indonesian NIK (Nomor Induk Kependudukan): exactly 16 digits
NIK_PATTERN = re.compile(
    r"\b\d{16}\b"
)

# Card / Bank Account patterns
CARD_PATTERN = re.compile(
    r"\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{13,19}\b"
)


def luhn_checksum_valid(card_number_str: str) -> bool:
    """Validate a card number string using the Luhn algorithm."""
    digits = [int(c) for c in card_number_str if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    
    total = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            total += (doubled - 9) if doubled > 9 else doubled
        else:
            total += d
    return total % 10 == 0


class PIIMasker:
    """Masks sensitive personally identifiable information in raw text."""

    def __init__(
        self,
        mask_phone: bool = True,
        mask_email: bool = True,
        mask_user: bool = True,
        mask_id: bool = True,
        mask_account: bool = True,
    ) -> None:
        self.mask_phone = mask_phone
        self.mask_email = mask_email
        self.mask_user = mask_user
        self.mask_id = mask_id
        self.mask_account = mask_account

    def mask(self, text: str) -> str:
        """Apply PII masking to the input text."""
        if not text:
            return ""

        # 1. Mask Email first (so domain/usernames don't interfere with other patterns)
        if self.mask_email:
            text = EMAIL_PATTERN.sub("<EMAIL>", text)

        # 2. Mask User Mentions
        if self.mask_user:
            text = MENTION_PATTERN.sub("<USER>", text)

        # 3. Mask Phone Numbers
        if self.mask_phone:
            text = PHONE_PATTERN.sub("<PHONE>", text)

        # 4. Mask Bank/Credit Card Accounts (if Luhn valid) - run before NIK
        if self.mask_account:
            def replace_card(m: re.Match[str]) -> str:
                match_str = m.group(0)
                clean_digits = re.sub(r"\D", "", match_str)
                if len(clean_digits) in (15, 16) and luhn_checksum_valid(clean_digits):
                    return "<ACCOUNT>"
                return match_str

            text = CARD_PATTERN.sub(replace_card, text)

        # 5. Mask NIK (16 digits)
        if self.mask_id:
            text = NIK_PATTERN.sub("<ID_NUMBER>", text)

        return text
