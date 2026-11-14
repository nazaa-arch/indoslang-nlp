<div align="center">

<h1>🇮🇩 IndoSlang-NLP</h1>

### Fast, deterministic &amp; modular Indonesian social-media text normalization

Normalize slang, abbreviations, leetspeak, and word elongation deterministically — while preserving affective emotion signals and protecting acronyms, numbers, and PII.
Built for Indonesian NLP preprocessing pipelines, sentiment/toxicity classification, and reproducible Scikit-Learn workflows.

<br>

[![Version](https://img.shields.io/badge/version-v0.1.0-3B82F6?style=flat-square)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Engine](https://img.shields.io/badge/matcher-Aho--Corasick%20O(N%2BZ)-009688?style=flat-square)](docs/user_guide.md)
[![Tests](https://img.shields.io/badge/tests-50%20passed-22C55E?style=flat-square)](tests/)
[![Throughput](https://img.shields.io/badge/throughput-~2%2C295%20sent%2Fs-F59E0B?style=flat-square)](benchmarks/benchmark_speed.py)
[![License](https://img.shields.io/badge/license-MIT-3B82F6?style=flat-square)](LICENSE)

[**Quickstart**](#quickstart) · [**Pipeline**](#10-stage-pipeline) · [**Features**](#features) · [**Benchmarks**](#benchmarks--verification) · [**Docs**](#documentation) · [**Support**](#support)

</div>

---

## What IndoSlang-NLP is

**IndoSlang-NLP** is a deterministic Python normalization library engineered specifically for noisy Indonesian social-media text. Unlike naive regex replacement scripts that break official acronyms (`BCA`), quantitative tokens (`100rb`, `2024`, `mp4`), or valid doubled-letter words (`saat`, `maaf`), IndoSlang-NLP runs an **order-dependent 10-stage pipeline** backed by `ahocorasick-rs` and schema-validated lexicons.

**Built for production ML &amp; research.** Extract affective signals (`caps_ratio`, `elongation_count`, emoticon polarity) before lowercasing, mask Indonesian PII (`NIK`, phone numbers, `@mentions`), audit every token mutation via `trace=True`, and drop directly into `sklearn.pipeline.Pipeline`.

> **Looking for detailed pipeline rules and parameter options?** See the [user guide](docs/user_guide.md) and [API reference](docs/api_reference.md).

---

## Features

- **Aho-Corasick multi-pattern matching (`O(N + Z)`)**: powered by `ahocorasick-rs` with a pure-Python trie fallback across 1,000+ schema-validated entries (`abbreviations`, `slang_base`, `indoglish`, `regional_slang`). [→ user guide](docs/user_guide.md)
- **Whitelist-aware de-elongation**: collapses expressive stretching (`bangeeettt` → `banget`) without corrupting valid Indonesian doubled-letter words (`saat`, `maaf`, `cemooh`). [→ API reference](docs/api_reference.md)
- **Vocabulary-validated leetspeak/algospeak decoder**: restores obfuscated tokens (`g!la` → `gila`, `b0d0h` → `bodoh`) while protecting numeric tokens (`2024`, `100rb`, `4k`). [→ user guide](docs/user_guide.md)
- **Morphological reduplication &amp; clitics**: resolves numeral-2 shorthand with possessive suffixes (`temen2nya` → `teman-temannya`).
- **Pre-normalization affective feature extraction**: captures `elongation_count`, `caps_ratio`, exclamation/question counts, and negative emoticon counts before case-folding.
- **Built-in PII masking &amp; token protection**: masks Indonesian mobile numbers, emails, `@mentions`, 16-digit NIK, and Luhn-validated card numbers (`PIIMasker`, `TokenProtector`).
- **Native Scikit-Learn &amp; CLI support**: plug into `Pipeline` / `GridSearchCV` via `IndoSlangTransformer` or batch-process CSVs via `indoslang normalize`. [→ notebooks](notebooks/)

---

## 10-Stage Pipeline

```mermaid
flowchart LR
    A[Raw Text] --> B[1. TextCleaner &amp; PII Mask]
    B --> C[2. TokenProtector]
    C --> D[3. Affective Extractor]
    D --> E[4. Case Folding]
    E --> F[5. LeetspeakDecoder]
    F --> G[6. DeElongator]
    G --> H[7. ReduplicationResolver]
    H --> I[8. Aho-Corasick Lexicon]
    I --> J[9. Emoji &amp; Punctuation]
    J --> K[10. Restore &amp; Output]
```

Three ambiguity policies are supported (`ambiguity_mode`): `conservative` (default, confidence ≥ 0.98 + context-bound phrases), `aggressive`, and `context_aware`.

---

## Quickstart

### Prerequisites

- **Python** `3.10+` (`3.10`, `3.11`, `3.12`, or `3.13`)

### Installation (from source)

```powershell
git clone https://github.com/nazaa-arch/indoslang-nlp.git
Set-Location .\indoslang-nlp

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

*(If published to your environment/PyPI index: `pip install indoslang-nlp`)*

### 1. Basic Normalization

```python
from indoslang import IndoNormalizer

normalizer = IndoNormalizer()
print(normalizer.normalize("gw mager bangeeet, bsk ktmuan yaa"))
# Output: "saya malas gerak banget, besok ketemuan ya"
```

### 2. Affective Feature Extraction

```python
normalizer = IndoNormalizer(extract_features=True)
doc = normalizer.process("PARAHHH BANGEEETTT SIHHH GAK JELAS BGT!!! 😡😡")

print(doc.text)
# Output: "parah banget sih tidak jelas banget!! 😡😡"

print(doc.features)
# {
#   "elongation_count": 3,
#   "elongated_tokens": ["parah", "banget", "sih"],
#   "caps_ratio": 1.0,
#   "exclamation_count": 3,
#   "question_count": 0,
#   "emoticon_negative_count": 2
# }
```

### 3. Scikit-Learn Pipeline Integration

```python
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from indoslang.sklearn import IndoSlangTransformer

pipeline = Pipeline([
    ("normalizer", IndoSlangTransformer(fix_elongation=True, ambiguity_mode="conservative")),
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB()),
])
```

### 4. Command-Line Interface (CLI)

```bash
indoslang normalize --input dataset.csv --output cleaned.csv --column teks --workers 4
```

---

## Benchmarks &amp; Verification

Executed on **Python 3.13.7 (Windows 11, AMD64)** against the bundled evaluation &amp; benchmark scripts:

| Check | Command | Measured Result |
|---|---|---|
| **Test Suite** | `python -m pytest tests/ -q` | **50 passed** (unit, Hypothesis property-based &amp; JSON schema tests) |
| **Speed &amp; Throughput** | `python benchmarks/benchmark_speed.py` | Median **2,295.6 sentences/sec** (`0.4356 ms/sentence` over 20,000 sentences, 5 passes) |
| **Gold-Standard Sample** | `python benchmarks/gold_standard_eval.py` | **94.2% token-level accuracy** (`66.7%` exact sentence match across 15 annotated cases) |

---

## Documentation

Everything detailed lives in [`docs/`](docs/) and [`notebooks/`](notebooks/):

- [**Documentation Overview**](docs/index.md)
- [**User Guide &amp; Ambiguity Modes**](docs/user_guide.md)
- [**API Reference (`IndoNormalizer`, `IndoSlangTransformer`)**](docs/api_reference.md)
- [**Lexicon Annotation Guidelines**](docs/annotation_guidelines.md)
- [**Notebooks: Tutorial, Sklearn &amp; Sentiment Benchmark**](notebooks/)
- [**Dictionary Licenses**](DATA_LICENSES.md) · [**Changelog**](CHANGELOG.md) · [**Security Policy**](SECURITY.md) · [**Contributing**](CONTRIBUTING.md)

---

## Support

<div align="center">

| Channel | Link |
| :--- | :--- |
| **Portfolio** | [portofolionaza.steamcraft.online](https://portofolionaza.steamcraft.online) |
| **LinkedIn** | [linkedin.com/in/nazafirman](https://www.linkedin.com/in/nazafirman) |
| **Email** | [firmannaza307@gmail.com](mailto:firmannaza307@gmail.com) |

</div>

---

## Credits

<div align="center">

<a href="https://github.com/nazaa-arch">
  <img src="https://avatars.githubusercontent.com/u/190960433" width="88" height="88" alt="Muhammad Naza Firmansyah" style="border-radius:50%;">
</a>

**[Muhammad Naza Firmansyah](https://www.linkedin.com/in/nazafirman)** — Author &amp; Maintainer  
Data Science, Universitas Negeri Surabaya (UNESA)

</div>

---

## Notes &amp; Scope

> [!NOTE]
> Under `ambiguity_mode="conservative"` (the default), intentionally ambiguous shorthand tokens without high-confidence context remain unexpanded to prevent false-positive substitutions in downstream NLP models. Switch to `context_aware` or `aggressive` depending on your task recall/precision trade-off.

---

## License

IndoSlang-NLP is distributed under the **[MIT License](LICENSE)**. Dictionary source attributions are documented in [DATA_LICENSES.md](DATA_LICENSES.md).

<br>

<div align="center">

**IndoSlang-NLP: Deterministic Indonesian Social-Media Text Normalization.**<br>
*Fast Aho-Corasick matching. Signal-preserving NLP preprocessing.*

</div>
