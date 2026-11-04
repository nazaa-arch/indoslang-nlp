"""Unit tests for Scikit-Learn transformer integration."""

import pickle

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

from indoslang.sklearn import IndoSlangTransformer


def test_sklearn_transformer_fit_transform():
    transformer = IndoSlangTransformer()
    raw_texts = ["gw mager bgt", "bsk ktmuan yaa"]
    transformed = transformer.fit_transform(raw_texts)
    assert transformed[0] == "saya malas gerak banget"
    assert transformed[1] == "besok ketemuan ya"


def test_pipeline_integration():
    pipe = Pipeline([
        ("normalizer", IndoSlangTransformer()),
        ("vectorizer", CountVectorizer())
    ])

    raw_texts = ["gw mager bgt", "kamu rajin bgt", "dia malas gerak"]
    _ = pipe.fit_transform(raw_texts)
    vocab = pipe.named_steps["vectorizer"].vocabulary_
    assert "malas" in vocab
    assert "gerak" in vocab
    assert "mager" not in vocab


def test_transformer_pickleability():
    transformer = IndoSlangTransformer(ambiguity_mode="aggressive")
    data = pickle.dumps(transformer)
    loaded = pickle.loads(data)
    assert loaded.ambiguity_mode == "aggressive"
    out = loaded.transform(["gw mager bgt"])
    assert out[0] == "saya malas gerak banget"
