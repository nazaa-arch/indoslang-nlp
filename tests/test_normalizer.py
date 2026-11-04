"""Comprehensive unit tests for IndoNormalizer and Golden Test Cases."""

import pytest

from indoslang.normalizer import IndoNormalizer


@pytest.fixture
def normalizer():
    return IndoNormalizer()


@pytest.fixture
def normalizer_feat():
    return IndoNormalizer(extract_features=True)


def test_golden_cases(normalizer):
    """Verify all 17 Golden Test Cases from Section 15.4 of the design specification."""
    test_cases = [
        ("bangeeeettt", "banget"),
        ("maaaaf", "maaf"),
        ("saaattt", "saat"),
        ("saat", "saat"),
        ("g!la", "gila"),
        ("100rb", "100rb"),
        ("2024", "2024"),
        ("covid19", "covid19"),
        ("mp4", "mp4"),
        ("4k", "4k"),
        ("h2h", "h2h"),
        ("buku2", "buku-buku"),
        ("temen2nya", "teman-temannya"),
        ("cm kamu", "cuma kamu"),
        ("5 cm", "5 cm"),
        ("BCA", "BCA"),
        ("𝗕𝗔𝗡𝗚𝗘𝗧", "banget"),
        ("@budi_99", "<USER>"),
        ("08123456789", "<PHONE>"),
        ("????", "?"),
    ]

    for raw, expected in test_cases:
        out = normalizer.normalize(raw)
        assert out == expected, f"Failed for '{raw}': got '{out}', expected '{expected}'"
        # Idempotency check: normalize(normalize(text)) == normalize(text)
        out2 = normalizer.normalize(out)
        assert out2 == out, f"Idempotency failed for '{raw}': '{out}' -> '{out2}'"


def test_golden_special_cases(normalizer, normalizer_feat):
    # ???? with extract_features=True -> ??
    assert normalizer_feat.normalize("????") == "??"

    # None and NaN robustness
    assert normalizer.normalize(None) == ""
    assert normalizer.normalize(float("nan")) == ""


def test_end_to_end_walkthrough(normalizer_feat):
    """Test the complete end-to-end walkthrough from Section 6.2."""
    raw = "WOII @user_99 jgn mager bangeeettt, bsk ktmuan yaa!! 😭 kontak: 08123456789"
    doc = normalizer_feat.process(raw)
    expected_text = "woi <USER> jangan malas gerak banget, besok ketemuan ya!! 😭 kontak: <PHONE>"
    assert doc.text == expected_text
    assert doc.features["exclamation_count"] == 2
    assert doc.features["emoticon_negative_count"] == 1
    assert doc.features["elongation_count"] == 3


def test_affect_extraction_example(normalizer_feat):
    """Test the affective extraction example from Section 9."""
    raw = "PARAHHH BANGEEETTT SIHHH GAK JELAS BGT!!! 😡😡"
    doc = normalizer_feat.process(raw)
    assert doc.text == "parah banget sih tidak jelas banget!! 😡😡"
    assert doc.features["elongation_count"] == 3
    assert doc.features["elongated_tokens"] == ["parah", "banget", "sih"]
    assert doc.features["caps_ratio"] == 1.0
    assert doc.features["exclamation_count"] == 3
    assert doc.features["emoticon_negative_count"] == 2


def test_trace_mode(normalizer):
    doc = normalizer.process("gw mager bgt", trace=True)
    assert len(doc.trace_steps) > 0
    stages = [step.stage for step in doc.trace_steps]
    assert "lexicon" in stages


def test_transform_batch(normalizer):
    texts = [
        "gw mager bgt",
        "produknya bgs bangeeet",
        "pelayanan kureeenggg"
    ]
    batch_out = normalizer.transform_batch(texts)
    assert len(batch_out) == 3
    assert batch_out[0] == "saya malas gerak banget"
    assert batch_out[1] == "produknya bagus banget"
    assert batch_out[2] == "pelayanan kurang"


def test_non_destructive_on_vocab_baku(normalizer):
    """Ensure standard words are not corrupted."""
    sample_baku = ["saya", "makan", "nasi", "di", "rumah", "saat", "pagi", "hari", "bersama", "teman"]
    for word in sample_baku:
        assert normalizer.normalize(word) == word
