"""Unit tests for ReduplicationResolver."""

import pytest
from indoslang.reduplication import ReduplicationResolver


def test_basic_reduplication():
    resolver = ReduplicationResolver()
    assert resolver.expand("buku2") == "buku-buku"
    assert resolver.expand("anak2") == "anak-anak"
    assert resolver.expand("orang2") == "orang-orang"


def test_reduplication_with_clitics():
    base_map = {"temen": "teman", "org": "orang"}
    resolver = ReduplicationResolver(base_map=base_map)

    assert resolver.expand("buku2ku") == "buku-bukuku"
    assert resolver.expand("temen2nya") == "teman-temannya"
    assert resolver.expand("mobil2ku") == "mobil-mobilku"
    assert resolver.expand("org2nya") == "orang-orangnya"


def test_casing_preserved():
    resolver = ReduplicationResolver()
    assert resolver.expand("BUKU2") == "BUKU-BUKU"
    assert resolver.expand("Buku2") == "Buku-buku"
