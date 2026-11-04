"""Unit tests for PIIMasker."""

import pytest
from indoslang.pii import PIIMasker, luhn_checksum_valid


def test_mask_phone_numbers():
    masker = PIIMasker()
    assert masker.mask("hubungi 08123456789 ya") == "hubungi <PHONE> ya"
    assert masker.mask("kontak +6281234567890 segera") == "kontak <PHONE> segera"
    assert masker.mask("wa ke 0812-3456-7890 ya") == "wa ke <PHONE> ya"


def test_mask_email():
    masker = PIIMasker()
    assert masker.mask("kirim ke user@example.com terima kasih") == "kirim ke <EMAIL> terima kasih"
    assert masker.mask("kontak: budi.santoso99@gmail.co.id") == "kontak: <EMAIL>"


def test_mask_user_mention():
    masker = PIIMasker()
    assert masker.mask("halo @budi_99 apa kabar") == "halo <USER> apa kabar"
    assert masker.mask("@jokowi @prabowo") == "<USER> <USER>"


def test_mask_nik():
    masker = PIIMasker()
    # 16-digit ID
    assert masker.mask("NIK: 3201234567890123 terdaftar") == "NIK: <ID_NUMBER> terdaftar"
    # Less than 16 digits should not match NIK
    assert masker.mask("angka: 12345678") == "angka: 12345678"


def test_luhn_and_card_masking():
    # Valid Luhn dummy card number: 4532015112830366
    valid_card = "4532015112830366"
    assert luhn_checksum_valid(valid_card) is True
    assert luhn_checksum_valid("1234567812345678") is False

    masker = PIIMasker()
    text = f"bayar kartu {valid_card} ya"
    assert masker.mask(text) == "bayar kartu <ACCOUNT> ya"
