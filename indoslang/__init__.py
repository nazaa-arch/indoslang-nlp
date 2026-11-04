"""IndoSlang-NLP: Fast, deterministic Indonesian slang and informal text normalizer."""

from indoslang.affect import AffectiveFeatures
from indoslang.normalizer import IndoNormalizer, NormalizedDoc, TraceStep
from indoslang.sklearn import IndoSlangTransformer

__version__ = "0.1.0"
__all__ = [
    "AffectiveFeatures",
    "IndoNormalizer",
    "IndoSlangTransformer",
    "NormalizedDoc",
    "TraceStep",
    "__version__",
]
