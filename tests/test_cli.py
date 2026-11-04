"""Unit tests for the CLI."""

import tempfile
from pathlib import Path
import pytest
from indoslang.cli import main


def test_cli_normalize_txt():
    with tempfile.TemporaryDirectory() as tmpdir:
        in_file = Path(tmpdir) / "input.txt"
        out_file = Path(tmpdir) / "output.txt"
        in_file.write_text("gw mager bgt\nbsk ktmuan yaa\n", encoding="utf-8")

        exit_code = main(["normalize", "--input", str(in_file), "--output", str(out_file)])
        assert exit_code == 0
        assert out_file.exists()

        lines = out_file.read_text(encoding="utf-8").splitlines()
        assert lines[0] == "saya malas gerak banget"
        assert lines[1] == "besok ketemuan ya"


def test_cli_normalize_csv():
    with tempfile.TemporaryDirectory() as tmpdir:
        in_file = Path(tmpdir) / "dataset.csv"
        out_file = Path(tmpdir) / "cleaned.csv"
        in_file.write_text("id,teks\n1,gw mager bgt\n2,produknya bgs bangeeet\n", encoding="utf-8")

        exit_code = main(["normalize", "--input", str(in_file), "--output", str(out_file), "--column", "teks"])
        assert exit_code == 0
        assert out_file.exists()

        content = out_file.read_text(encoding="utf-8")
        assert "saya malas gerak banget" in content
        assert "produknya bagus banget" in content


def test_cli_update_dicts_offline():
    exit_code = main(["update-dicts", "--offline"])
    assert exit_code == 0
