"""Unit tests for LeetspeakDecoder."""

import pytest

from indoslang.leetspeak import LeetspeakDecoder
from indoslang.normalizer import load_vocab_baku


@pytest.fixture
def leet_decoder():
    vocab = load_vocab_baku()
    slang_keys = {"bodoh", "anjing", "gila", "toxic"}
    return LeetspeakDecoder(vocab=vocab, slang_keys=slang_keys)


def test_decode_valid_leetspeak(leet_decoder):
    assert leet_decoder.decode_token("g!la") == "gila"
    assert leet_decoder.decode_token("b0d0h") == "bodoh"
    assert leet_decoder.decode_token("4nj1ng") == "anjing"
    assert leet_decoder.decode_token("t0x1c") == "toxic"


def test_preserve_non_leetspeak_numbers(leet_decoder):
    # Pure numbers must NOT be transformed
    assert leet_decoder.decode_token("2024") == "2024"
    assert leet_decoder.decode_token("100") == "100"
    # Unmatched alphanumerics must NOT be corrupted
    assert leet_decoder.decode_token("covid19") == "covid19"


def test_decode_text(leet_decoder):
    text = "dia orgnya b0d0h dan g!la bgt"
    assert leet_decoder.decode_text(text) == "dia orgnya bodoh dan gila bgt"
