"""Main pipeline orchestrator for IndoSlang-NLP."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from indoslang.affect import AffectiveFeatureExtractor, AffectiveFeatures
from indoslang.cleaner import TextCleaner
from indoslang.elongation import DeElongator, load_whitelist_elongation
from indoslang.emoji_punct import compress_punctuation, handle_emoji
from indoslang.exceptions import ConfigurationError
from indoslang.leetspeak import LeetspeakDecoder
from indoslang.lexicon import LexiconMatcher
from indoslang.pii import PIIMasker
from indoslang.protect import TokenProtector, load_official_acronyms
from indoslang.reduplication import ReduplicationResolver

logger = logging.getLogger("indoslang")


@dataclass
class TraceStep:
    """Audit trace step representing an individual transformation."""
    stage: str
    original_token: str
    transformed_token: str
    rule_source: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class NormalizedDoc:
    """Normalized document container with text, affective features, trace, and metadata."""
    text: str
    features: dict[str, Any]
    trace_steps: list[TraceStep]
    meta: dict[str, Any]


def load_vocab_baku(path: str | None = None) -> set[str]:
    """Load standard Indonesian vocabulary from file."""
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "data", "vocab", "id_vocab_baku.txt")

    vocab: set[str] = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                if w and not w.startswith("#"):
                    vocab.add(w)
    return vocab


class IndoNormalizer:
    """Indonesian social media and informal text normalizer.
    
    Provides deterministic, high-throughput text normalization with support for
    de-elongation, leetspeak decoding, reduplication resolution, Aho-Corasick lexicon
    matching, PII masking, and affective feature extraction.
    """

    LIB_VERSION = "0.1.0"

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
        if ambiguity_mode not in ("conservative", "aggressive", "context_aware"):
            raise ConfigurationError(
                f"Invalid ambiguity_mode: '{ambiguity_mode}'. Must be 'conservative', 'aggressive', or 'context_aware'."
            )
        if emoji not in ("ignore", "remove", "demojize"):
            raise ConfigurationError(
                f"Invalid emoji mode: '{emoji}'. Must be 'ignore', 'remove', or 'demojize'."
            )

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
        self.extra_lexicons = extra_lexicons or []
        self.dict_version = dict_version

        # Config hash for experiment reproducibility
        cfg_str = f"{ambiguity_mode}_{fix_elongation}_{fix_leetspeak}_{expand_reduplication}_{emoji}_{lowercase}_{dict_version}"
        self.config_hash = hashlib.sha256(cfg_str.encode("utf-8")).hexdigest()[:8]

        # 1. Vocab and Whitelists
        self.vocab = load_vocab_baku()
        self.whitelist_elongation = load_whitelist_elongation()
        self.official_acronyms = load_official_acronyms()

        # 2. Pipeline Sub-engines
        self.cleaner = TextCleaner(clean_social_tags=clean_social_tags)
        self.pii_masker = PIIMasker(
            mask_phone=mask_pii,
            mask_email=mask_pii,
            mask_user=mask_pii,
            mask_id=mask_pii,
            mask_account=mask_pii
        )
        self.token_protector = TokenProtector(
            official_acronyms=self.official_acronyms,
            preserve_acronyms=preserve_acronyms
        )
        # 3. Lexicon Matcher (Aho-Corasick)
        self.lexicon_matcher = LexiconMatcher(
            ambiguity_mode=ambiguity_mode,
            translate_indoglish=translate_indoglish,
            extra_lexicons=self.extra_lexicons
        )

        slang_keys = set(self.lexicon_matcher.entries.keys())
        base_map = {k: e.normalized for k, e in self.lexicon_matcher.entries.items() if not e.is_multiword}
        self.reduplication_resolver = ReduplicationResolver(base_map=base_map)

        # 4. Leetspeak & Elongation Engines
        self.leetspeak_decoder = LeetspeakDecoder(
            vocab=self.vocab,
            slang_keys=slang_keys
        )
        self.de_elongator = DeElongator(
            vocab=self.vocab,
            whitelist=self.whitelist_elongation,
            slang_keys=slang_keys
        )

    def normalize(self, text: Any) -> str:
        """Normalize raw informal Indonesian text to standard clean text.
        
        Contract: Always returns str.
        """
        doc = self.process(text, trace=False)
        return doc.text

    def process(self, text: Any, trace: bool = False) -> NormalizedDoc:
        """Process text through the 10-stage pipeline and return NormalizedDoc.
        
        Contract: Always returns NormalizedDoc.
        """
        trace_steps: list[TraceStep] = []

        # 0. Non-string safety & check
        sanitized = self.cleaner.sanitize_input(text)
        if not sanitized.strip():
            features = AffectiveFeatures().to_dict() if self.extract_features else {}
            meta = {
                "lib_version": self.LIB_VERSION,
                "dict_version": self.dict_version,
                "config_hash": self.config_hash
            }
            return NormalizedDoc(text="", features=features, trace_steps=trace_steps, meta=meta)

        # Stage 1: Sanitasi & PII Masking
        current_text = self.cleaner.clean(sanitized)
        if self.mask_pii:
            current_text = self.pii_masker.mask(current_text)

        # Stage 2: Proteksi Token (placeholders, official acronyms, product codes, units, years)
        current_text, protected_map = self.token_protector.protect(current_text)

        # Stage 3: Ekstraktor Sinyal Afektif (pre-casefold & pre-compression)
        affect_features = None
        if self.extract_features:
            affect_features = AffectiveFeatureExtractor.extract_pre_normalization(current_text)

        # Stage 4: Normalisasi Bentuk Huruf (Case folding)
        if self.lowercase:
            current_text = current_text.lower()

        # Stage 5: Dekoder Leetspeak & Algospeak
        if self.fix_leetspeak:
            orig_before_leet = current_text
            current_text = self.leetspeak_decoder.decode_text(current_text)
            if trace and current_text != orig_before_leet:
                trace_steps.append(TraceStep(
                    stage="leetspeak",
                    original_token=orig_before_leet,
                    transformed_token=current_text,
                    rule_source="leetspeak_map"
                ))

        # Stage 6: De-elongation Adaptif
        if self.fix_elongation:
            current_text, elongated_tokens = self.de_elongator.process_text(current_text)
            if affect_features is not None:
                affect_features.elongation_count = len(elongated_tokens)
                affect_features.elongated_tokens = elongated_tokens

        # Stage 7: Resolusi Reduplikasi & Klitik
        if self.expand_reduplication:
            orig_before_redup = current_text
            current_text = self.reduplication_resolver.expand(current_text)
            if trace and current_text != orig_before_redup:
                trace_steps.append(TraceStep(
                    stage="reduplication",
                    original_token=orig_before_redup,
                    transformed_token=current_text,
                    rule_source="reduplication_clitic_rule"
                ))

        # Stage 8: Pencocokan Leksikon Aho-Corasick
        trace_lexicon: list[dict[str, str]] | None = [] if trace else None
        current_text = self.lexicon_matcher.replace(current_text, trace_records=trace_lexicon)
        if trace and trace_lexicon:
            for item in trace_lexicon:
                trace_steps.append(TraceStep(
                    stage=item["stage"],
                    original_token=item["original_token"],
                    transformed_token=item["transformed_token"],
                    rule_source=item["rule_source"]
                ))

        # Stage 9: Emoji & Pungtuasi
        current_text = handle_emoji(current_text, mode=self.emoji)
        # Punctuation compression: max 2 if extract_features else 1
        punct_repeats = 2 if self.extract_features else 1
        current_text = compress_punctuation(current_text, max_repeats=punct_repeats)

        # Stage 10: Post-Processing & Perapihan Spasi & Restore Protected Tokens
        current_text = TokenProtector.restore(current_text, protected_map)
        current_text = re.sub(r" +", " ", current_text).strip()

        features_dict = affect_features.to_dict() if affect_features is not None else {}
        meta = {
            "lib_version": self.LIB_VERSION,
            "dict_version": self.dict_version,
            "config_hash": self.config_hash
        }

        return NormalizedDoc(
            text=current_text,
            features=features_dict,
            trace_steps=trace_steps,
            meta=meta
        )

    def transform_batch(
        self,
        texts: list[Any],
        n_jobs: int = 1,
        batch_size: int = 1000
    ) -> list[str]:
        """Normalize a collection of texts efficiently.
        
        Args:
            texts: List or iterable of raw texts.
            n_jobs: Number of parallel worker processes (1 for sequential).
            batch_size: Chunk size per batch.
            
        Returns:
            List of normalized strings.
        """
        if not texts:
            return []

        # If single worker or small list, process sequentially for low overhead
        if n_jobs == 1 or len(texts) < 500:
            return [self.normalize(t) for t in texts]

        # Multiprocessing batch execution
        import multiprocessing
        from concurrent.futures import ProcessPoolExecutor

        max_workers = min(n_jobs if n_jobs > 0 else multiprocessing.cpu_count(), multiprocessing.cpu_count())

        # Divide into chunks
        chunks = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        results: list[str] = []

        # Global worker helper function
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            chunk_results = executor.map(_batch_worker_task, [(chunk, self) for chunk in chunks])
            for sublist in chunk_results:
                results.extend(sublist)

        return results

    @classmethod
    def from_config(cls, config_path: str | Path) -> IndoNormalizer:
        """Create an IndoNormalizer instance from a TOML or JSON config file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise ConfigurationError(f"Config file not found: {config_path}")

        content = config_path.read_text(encoding="utf-8")
        if config_path.suffix.lower() == ".json":
            cfg = json.loads(content)
        elif config_path.suffix.lower() == ".toml":
            try:
                import tomllib
                cfg = tomllib.loads(content)
            except ImportError:
                import toml
                cfg = toml.loads(content)
        else:
            raise ConfigurationError(f"Unsupported config format: {config_path.suffix}")

        return cls(**cfg)


def _batch_worker_task(args: tuple[list[Any], IndoNormalizer]) -> list[str]:
    """Top-level helper function for multiprocessing batch execution."""
    chunk, normalizer = args
    return [normalizer.normalize(t) for t in chunk]
