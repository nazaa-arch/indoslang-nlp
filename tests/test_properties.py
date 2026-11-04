"""Property-based testing with Hypothesis for IndoSlang-NLP."""

from hypothesis import given, settings, strategies as st
from indoslang.normalizer import IndoNormalizer

normalizer = IndoNormalizer()


@settings(max_examples=50, deadline=None)
@given(st.text())
def test_property_always_returns_str_and_never_crashes(text: str):
    """Normalizer should accept arbitrary string input and always return a str without crashing."""
    result = normalizer.normalize(text)
    assert isinstance(result, str)


@settings(max_examples=50, deadline=None)
@given(st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=100))
def test_property_idempotence(text: str):
    """Applying normalize twice must produce the same result as applying it once."""
    first_pass = normalizer.normalize(text)
    second_pass = normalizer.normalize(first_pass)
    assert second_pass == first_pass
