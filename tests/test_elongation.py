"""Unit tests for DeElongator."""

import pytest

from indoslang.elongation import DeElongator, load_whitelist_elongation
from indoslang.normalizer import load_vocab_baku


@pytest.fixture
def elongator():
    vocab = load_vocab_baku()
    whitelist = load_whitelist_elongation()
    slang_keys = {"banget", "bagus", "parah", "sih", "woi", "ya", "kureng"}
    return DeElongator(vocab=vocab, whitelist=whitelist, slang_keys=slang_keys)


def test_whitelist_non_destruction(elongator):
    # Valid words with double letters should NOT be reduced
    for word in ["maaf", "saat", "taat", "cemooh", "massa", "naas", "illahi", "koordinasi", "zoologi"]:
        norm, was_elong = elongator.de_elongate_token(word)
        assert norm == word
        assert was_elong is False


def test_elongation_reduction(elongator):
    assert elongator.de_elongate_token("bangeeeettt")[0] == "banget"
    assert elongator.de_elongate_token("maaaaf")[0] == "maaf"
    assert elongator.de_elongate_token("saaattt")[0] == "saat"
    assert elongator.de_elongate_token("baguss")[0] == "bagus"
    assert elongator.de_elongate_token("woii")[0] == "woi"
    assert elongator.de_elongate_token("yaa")[0] == "ya"


def test_process_text(elongator):
    text = "parahhh bangeeettt sihhh"
    norm_text, tokens = elongator.process_text(text)
    assert norm_text == "parah banget sih"
    assert set(tokens) == {"parah", "banget", "sih"}
