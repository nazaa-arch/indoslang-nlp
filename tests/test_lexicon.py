"""Unit tests for LexiconMatcher."""

from indoslang.lexicon import LexiconMatcher, PureTrieMatcher


def test_pure_trie_matcher():
    patterns = ["tidak apa apa", "tidak", "yg", "cm kamu"]
    matcher = PureTrieMatcher(patterns)
    matches = matcher.find_matches_as_indexes("saya tidak apa apa yg ada")
    assert len(matches) > 0


def test_lexicon_matcher_word_boundary():
    matcher = LexiconMatcher(ambiguity_mode="conservative")
    # 'yg' must match 'yg' but NOT inside 'tayg'
    text = "saya tayg yg suka"
    result = matcher.replace(text)
    assert "tayg" in result
    assert "yang" in result


def test_lexicon_matcher_multiword_priority():
    matcher = LexiconMatcher(ambiguity_mode="conservative")
    # Bound phrase 'cm kamu' -> 'cuma kamu'
    assert matcher.replace("cm kamu") == "cuma kamu"
    # Ambiguous standalone 'cm' in conservative mode should NOT be changed
    assert matcher.replace("jarak 5 cm") == "jarak 5 cm"


def test_lexicon_matcher_aggressive_mode():
    matcher = LexiconMatcher(ambiguity_mode="aggressive")
    # Standalone 'cm' converted in aggressive mode
    assert matcher.replace("hanya cm satu") == "hanya cuma satu"


def test_indoglish_toggle():
    # When translate_indoglish is False (default)
    matcher_off = LexiconMatcher(translate_indoglish=False)
    assert matcher_off.replace("which is") == "which is"

    # When translate_indoglish is True
    matcher_on = LexiconMatcher(translate_indoglish=True)
    assert matcher_on.replace("which is") == "yang mana"
