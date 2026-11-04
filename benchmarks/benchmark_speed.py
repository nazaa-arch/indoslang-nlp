"""Benchmark throughput and latency evaluation for IndoSlang-NLP.

Complies with the benchmark protocol in Section 15 of the design specification:
- CPU and OS environment reporting
- Warm-up execution
- Median of multiple measurement runs
- Sentences per second (throughput) and latency per sentence
"""

import io
import platform
import statistics
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (io.UnsupportedOperation, AttributeError):
        pass

from indoslang import IndoNormalizer

BENCHMARK_SAMPLES = [
    "gw mager bangeeet, bsk ktmuan yaa di Jaksel!!",
    "WOII @budi_99 jgn mager bangeeettt, bsk ktmuan yaa!! 😭 kontak: 08123456789",
    "produknya bgs bgt bangeeet, pengiriman cepet bgt mantap jiwa",
    "pelayanan kureeenggg bgt, sellernya t0x1c dan b0d0h bgt parah",
    "buku2 dan temen2nya pd ngumpul di cafe sm siapa aja",
    "cm kamu yg bs ngertiin gw, yg lain mah bodo amat",
    "jarak rumahnya 5 cm di peta, aslinya jauh bgt",
    "mana ada yg kyk gini, transfer ke BCA no rek 1234567890",
    "BARANGNYA BAGUSSS BANGEEETTT SIHHH GAK NYANGKA BGT!!! 😍😍",
    "aduh pusing pala gw mikirin tugas yg numpuk bgt gils",
]


def generate_benchmark_dataset(size: int = 10000) -> list[str]:
    """Generate a repeated benchmark corpus with variable sentence lengths."""
    data = []
    num_samples = len(BENCHMARK_SAMPLES)
    for i in range(size):
        data.append(BENCHMARK_SAMPLES[i % num_samples])
    return data


def run_benchmark():
    print("=" * 70)
    print(" 🇮🇩 IndoSlang-NLP Speed & Throughput Benchmark")
    print("=" * 70)
    print(f"Python Version   : {platform.python_version()} ({platform.python_implementation()})")
    print(f"Operating System : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Processor        : {platform.processor() or 'Standard CPU'}")
    print("-" * 70)

    dataset_size = 20000
    dataset = generate_benchmark_dataset(dataset_size)
    normalizer = IndoNormalizer()

    # Warm-up phase
    print("Warming up (2,000 sentences)...")
    for s in dataset[:2000]:
        _ = normalizer.normalize(s)

    # Measurement runs (5 iterations)
    num_runs = 5
    run_times = []
    print(f"Running {num_runs} benchmark passes over {dataset_size:,} sentences...")

    for r in range(num_runs):
        start = time.perf_counter()
        for sentence in dataset:
            _ = normalizer.normalize(sentence)
        elapsed = time.perf_counter() - start
        run_times.append(elapsed)
        throughput = dataset_size / elapsed
        print(f"  Run {r + 1}: {elapsed:.4f}s ({throughput:,.1f} sentences/sec)")

    median_time = statistics.median(run_times)
    median_throughput = dataset_size / median_time
    avg_latency_ms = (median_time / dataset_size) * 1000

    print("-" * 70)
    print(f"Median Execution Time : {median_time:.4f} seconds")
    print(f"Median Throughput     : {median_throughput:,.1f} sentences/sec")
    print(f"Average Latency       : {avg_latency_ms:.4f} ms/sentence")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
