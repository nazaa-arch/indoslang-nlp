"""Unit tests for TokenProtector."""

from indoslang.protect import TokenProtector


def test_protect_placeholders():
    protector = TokenProtector()
    text = "Halo <USER>, nomor anda <PHONE>."
    masked, pmap = protector.protect(text)
    assert "<USER>" not in masked
    assert "<PHONE>" not in masked
    assert len(pmap) == 2

    restored = TokenProtector.restore(masked, pmap)
    assert restored == text


def test_protect_official_acronyms():
    protector = TokenProtector(preserve_acronyms=True)
    text = "Transfer ke rekening BCA dan BNI wilayah DKI"
    masked, pmap = protector.protect(text)
    assert "BCA" not in masked
    assert "BNI" not in masked
    assert "DKI" not in masked

    # After lowercasing the masked text
    lower_masked = masked.lower()
    restored = TokenProtector.restore(lower_masked, pmap)
    assert "BCA" in restored
    assert "BNI" in restored
    assert "DKI" in restored


def test_protect_numeric_exclusions():
    protector = TokenProtector()
    text = "Beli mp4 seharga 100rb tahun 2024 layar 4k covid19"
    masked, pmap = protector.protect(text)
    for token in ["mp4", "100rb", "2024", "4k", "covid19"]:
        assert token not in masked

    restored = TokenProtector.restore(masked.lower(), pmap)
    for token in ["mp4", "100rb", "2024", "4k", "covid19"]:
        assert token in restored
