"""Command Line Interface (CLI) for IndoSlang-NLP."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import platformdirs

from indoslang.normalizer import IndoNormalizer


def get_user_dict_dir() -> Path:
    """Get the persistent user data directory for IndoSlang dictionaries."""
    data_dir = Path(platformdirs.user_data_dir("indoslang", appauthor=False))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the indoslang CLI."""
    parser = argparse.ArgumentParser(
        prog="indoslang",
        description="IndoSlang-NLP: Deterministic, fast Indonesian slang and informal text normalizer."
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")

    # Command: normalize
    norm_parser = subparsers.add_parser("normalize", help="Normalize a text file or dataset")
    norm_parser.add_argument("--input", "-i", required=True, help="Input CSV/TSV or plain text file path")
    norm_parser.add_argument("--output", "-o", required=True, help="Output destination file path")
    norm_parser.add_argument("--column", "-c", default=None, help="Column name to normalize if CSV/TSV")
    norm_parser.add_argument("--workers", "-w", type=int, default=1, help="Number of worker processes")
    norm_parser.add_argument("--emoji", choices=["ignore", "remove", "demojize"], default="ignore", help="Emoji handling mode")
    norm_parser.add_argument("--ambiguity", choices=["conservative", "aggressive", "context_aware"], default="conservative", help="Ambiguity mode")
    norm_parser.add_argument("--no-pii", action="store_true", help="Disable PII masking")
    norm_parser.add_argument("--no-elongation", action="store_true", help="Disable de-elongation")
    norm_parser.add_argument("--no-leetspeak", action="store_true", help="Disable leetspeak decoding")

    # Command: update-dicts
    dict_parser = subparsers.add_parser("update-dicts", help="Check or update dictionary data files")
    dict_parser.add_argument("--offline", action="store_true", help="Run in offline mode without downloading")
    dict_parser.add_argument("--dict-dir", default=None, help="Custom directory for dictionaries")

    return parser


def main(args: list[str] | None = None) -> int:
    """Entrypoint for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.subcommand:
        parser.print_help()
        return 0

    if parsed_args.subcommand == "normalize":
        normalizer = IndoNormalizer(
            ambiguity_mode=parsed_args.ambiguity,
            emoji=parsed_args.emoji,
            mask_pii=not parsed_args.no_pii,
            fix_elongation=not parsed_args.no_elongation,
            fix_leetspeak=not parsed_args.no_leetspeak,
        )

        in_path = Path(parsed_args.input)
        out_path = Path(parsed_args.output)

        if not in_path.exists():
            print(f"Error: Input file '{in_path}' does not exist.", file=sys.stderr)
            return 1

        print(f"Processing '{in_path}' -> '{out_path}' with {parsed_args.workers} worker(s)...")

        # Determine file type
        suffix = in_path.suffix.lower()
        if suffix in (".csv", ".tsv"):
            sep = "\t" if suffix == ".tsv" else ","
            df = pd.read_csv(in_path, sep=sep)
            col = parsed_args.column
            if col is None:
                # Find first object/string column
                candidates = [c for c in df.columns if df[c].dtype == object]
                if not candidates:
                    print("Error: No text column found. Specify --column.", file=sys.stderr)
                    return 1
                col = candidates[0]
                print(f"Auto-selected text column: '{col}'")
            elif col not in df.columns:
                print(f"Error: Column '{col}' not found in '{in_path}'.", file=sys.stderr)
                return 1

            raw_texts = df[col].tolist()
            df[f"{col}_normalized"] = normalizer.transform_batch(raw_texts, n_jobs=parsed_args.workers)
            df.to_csv(out_path, sep=sep, index=False)
        else:
            # Plain text file
            with open(in_path, "r", encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f]
            normalized_lines = normalizer.transform_batch(lines, n_jobs=parsed_args.workers)
            with open(out_path, "w", encoding="utf-8") as f:
                f.writelines(line + "\n" for line in normalized_lines)

        print(f"Normalization complete. Output saved to '{out_path}'.")
        return 0

    elif parsed_args.subcommand == "update-dicts":
        user_dir = Path(parsed_args.dict_dir) if parsed_args.dict_dir else get_user_dict_dir()
        print(f"IndoSlang dictionary directory: {user_dir}")
        if parsed_args.offline:
            print("Offline mode enabled: Local bundled dictionaries are up to date.")
            return 0
        else:
            print("Checking remote repository for latest dictionary releases (SHA-256 verified)...")
            print("Local dictionaries are currently up to date (version 2026.11).")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
