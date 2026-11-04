"""Unit tests for AffectiveFeatureExtractor."""

import pytest
from indoslang.affect import AffectiveFeatureExtractor


def test_caps_ratio():
    # All caps
    feat1 = AffectiveFeatureExtractor.extract_pre_normalization("PARAH BANGET")
    assert feat1.caps_ratio == 1.0

    # Half caps
    feat2 = AffectiveFeatureExtractor.extract_pre_normalization("Parah Banget")
    assert 0.1 < feat2.caps_ratio < 0.3

    # All lowercase
    feat3 = AffectiveFeatureExtractor.extract_pre_normalization("parah banget")
    assert feat3.caps_ratio == 0.0


def test_exclamation_and_question_counts():
    text = "APALAGI INI??? GAK MASUK AKAL!!!!"
    feat = AffectiveFeatureExtractor.extract_pre_normalization(text)
    assert feat.question_count == 3
    assert feat.exclamation_count == 4


def test_negative_emoticons():
    text = "sedih banget 😭 kecewa 😡"
    feat = AffectiveFeatureExtractor.extract_pre_normalization(text)
    assert feat.emoticon_negative_count == 2
