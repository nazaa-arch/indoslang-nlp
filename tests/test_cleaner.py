"""Unit tests for TextCleaner and Unicode sanitization."""

import math
import pytest
from indoslang.cleaner import TextCleaner, strip_invisible_format_chars


def test_cleaner_none_and_nan():
    cleaner = TextCleaner()
    assert cleaner.clean(None) == ""
    assert cleaner.clean(float("nan")) == ""
    assert cleaner.clean(12345) == "12345"


def test_unicode_nfkc():
    cleaner = TextCleaner()
    # Mathematical bold Unicode letters
    stylized = "𝗕𝗔𝗡𝗚𝗘𝗧"
    assert cleaner.clean(stylized) == "BANGET"

    # Fullwidth Latin
    fullwidth = "ｇａｕｌ"
    assert cleaner.clean(fullwidth) == "gaul"


def test_strip_invisible_format_chars():
    # Zero-width space (\u200b) and soft hyphen (\u00ad)
    text_with_zwsp = "halo\u200bdunia"
    assert strip_invisible_format_chars(text_with_zwsp) == "halodunia"

    # Preserves ZWJ inside emojis
    emoji_family = "👨\u200d👩\u200d👧"
    assert "\u200d" in strip_invisible_format_chars(emoji_family)


def test_clean_social_tags():
    cleaner = TextCleaner(clean_social_tags=True)
    text = "Kunjungi https://example.com/test atau www.test.com ya #seru #mantap"
    cleaned = cleaner.clean(text)
    assert "https://" not in cleaned
    assert "www.test.com" not in cleaned
    assert "seru" in cleaned
    assert "#" not in cleaned


def test_clean_social_tags_disabled():
    cleaner = TextCleaner(clean_social_tags=False)
    text = "Cek https://t.co/abc #keren"
    cleaned = cleaner.clean(text)
    assert "https://t.co/abc" in cleaned
    assert "#keren" in cleaned
