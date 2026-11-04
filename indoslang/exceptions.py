"""Custom exceptions for IndoSlang-NLP."""

class IndoSlangError(Exception):
    """Base exception for all IndoSlang-NLP errors."""
    pass


class InvalidDictionaryError(IndoSlangError):
    """Raised when a dictionary file is invalid or corrupted."""
    pass


class ConfigurationError(IndoSlangError):
    """Raised when an invalid configuration is provided to IndoNormalizer."""
    pass


class ProtectionError(IndoSlangError):
    """Raised when token protection fails or encounters an invalid state."""
    pass
