"""Naive re.sub per-entry baseline for comparison with Aho-Corasick in IndoSlang-NLP."""

import json
import re
import time
from pathlib import Path

from benchmarks.benchmark_speed import generate_benchmark_dataset


class NaiveReSubNormalizer:
    """Baseline normalizer using sequential re.sub for each dictionary entry."""

    def __init__(self):
        dict_dir = Path("indoslang/data/dictionaries")
        self.rules = []
        for f in dict_dir.glob("*.json"):
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            for word, val in data.items():
                senses = val.get("senses", [])
                if senses:
                    replacement = senses[0]["normalized"]
                    pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
                    self.rules.append((pattern, replacement))

    def normalize(self, text: str) -> str:
        text = text.lower()
        for pattern, replacement in self.rules:
            text = pattern.sub(replacement, text)
        return text


def run_comparison():
    print("=" * 70)
    print(" Naive re.sub Baseline vs IndoSlang-NLP (Aho-Corasick)")
    print("=" * 70)

    dataset_size = 2000
    dataset = generate_benchmark_dataset(dataset_size)

    # 1. Naive re.sub
    print(f"Testing Naive re.sub on {dataset_size} sentences...")
    naive = NaiveReSubNormalizer()
    print(f"Loaded {len(naive.rules)} regex rules.")
    start = time.perf_counter()
    for s in dataset:
        _ = naive.normalize(s)
    naive_time = time.perf_counter() - start
    naive_throughput = dataset_size / naive_time
    print(f"  Naive re.sub: {naive_time:.4f}s ({naive_throughput:,.1f} sentences/sec)")

    # 2. IndoSlang-NLP
    from indoslang import IndoNormalizer
    print(f"\nTesting IndoSlang-NLP on {dataset_size} sentences...")
    normalizer = IndoNormalizer()
    start = time.perf_counter()
    for s in dataset:
        _ = normalizer.normalize(s)
    indo_time = time.perf_counter() - start
    indo_throughput = dataset_size / indo_time
    print(f"  IndoSlang-NLP: {indo_time:.4f}s ({indo_throughput:,.1f} sentences/sec)")

    speedup = naive_time / indo_time
    print("-" * 70)
    print(f"Speedup Factor: {speedup:.2f}x faster than naive re.sub loop!")
    print("=" * 70)


if __name__ == "__main__":
    run_comparison()
