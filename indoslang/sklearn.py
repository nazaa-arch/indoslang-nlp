"""Scikit-Learn native transformer integration for IndoSlang-NLP."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from sklearn.base import BaseEstimator, TransformerMixin

from indoslang.normalizer import IndoNormalizer


class IndoSlangTransformer(BaseEstimator, TransformerMixin):
    """Scikit-Learn compatible text normalizer transformer.
    
    Can be used inside `sklearn.pipeline.Pipeline` and tuned using `GridSearchCV`.
    """

    def __init__(
        self,
        ambiguity_mode: str = "conservative",
        fix_elongation: bool = True,
        fix_leetspeak: bool = True,
        expand_reduplication: bool = True,
        clean_social_tags: bool = True,
        mask_pii: bool = True,
        emoji: str = "ignore",
        preserve_acronyms: bool = True,
        lowercase: bool = True,
        translate_indoglish: bool = False,
        extract_features: bool = False,
        extra_lexicons: list[str | Path] | None = None,
        dict_version: str = "2026.11",
    ) -> None:
        self.ambiguity_mode = ambiguity_mode
        self.fix_elongation = fix_elongation
        self.fix_leetspeak = fix_leetspeak
        self.expand_reduplication = expand_reduplication
        self.clean_social_tags = clean_social_tags
        self.mask_pii = mask_pii
        self.emoji = emoji
        self.preserve_acronyms = preserve_acronyms
        self.lowercase = lowercase
        self.translate_indoglish = translate_indoglish
        self.extract_features = extract_features
        self.extra_lexicons = extra_lexicons
        self.dict_version = dict_version

        # Normalizer is created lazily or initialized
        self._init_normalizer()

    def _init_normalizer(self) -> None:
        self._normalizer = IndoNormalizer(
            ambiguity_mode=self.ambiguity_mode,
            fix_elongation=self.fix_elongation,
            fix_leetspeak=self.fix_leetspeak,
            expand_reduplication=self.expand_reduplication,
            clean_social_tags=self.clean_social_tags,
            mask_pii=self.mask_pii,
            emoji=self.emoji,
            preserve_acronyms=self.preserve_acronyms,
            lowercase=self.lowercase,
            translate_indoglish=self.translate_indoglish,
            extract_features=self.extract_features,
            extra_lexicons=self.extra_lexicons,
            dict_version=self.dict_version,
        )

    def fit(self, X: Any, y: Any = None) -> IndoSlangTransformer:
        """Fit estimator (no-op for rule-based normalizer)."""
        self._init_normalizer()
        return self

    def transform(self, X: Iterable[Any]) -> list[str]:
        """Transform an iterable of texts into normalized texts."""
        if hasattr(X, "tolist"):
            texts = X.tolist()
        elif hasattr(X, "__iter__") and not isinstance(X, (str, bytes)):
            texts = list(X)
        else:
            texts = [X]

        return [self._normalizer.normalize(t) for t in texts]

    def set_params(self, **params: Any) -> IndoSlangTransformer:
        """Set parameters and reinitialize normalizer."""
        super().set_params(**params)
        self._init_normalizer()
        return self
