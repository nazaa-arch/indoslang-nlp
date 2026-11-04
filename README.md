# 🇮🇩 IndoSlang-NLP

> **Pustaka Python Cepat, Deterministik, dan Modular untuk Normalisasi Bahasa Gaul, Singkatan, *Leetspeak*, dan Elongasi Kata pada Teks Media Sosial Indonesia.**

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚡ Instalasi

```bash
pip install indoslang-nlp
```

Atau instal dari repositori lokal:
```bash
git clone https://github.com/indoslang/indoslang-nlp.git
cd indoslang-nlp
pip install -e .
```

---

## 🚀 Penggunaan Cepat

```python
from indoslang import IndoNormalizer

normalizer = IndoNormalizer()
print(normalizer.normalize("gw mager bangeeet, bsk ktmuan yaa"))
# Output: "saya malas gerak banget, besok ketemuan ya"
```

### Ekstraksi Fitur Afektif (Sinyal Emosi)

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

### Integrasi Scikit-Learn Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from indoslang.sklearn import IndoSlangTransformer

pipeline = Pipeline([
    ("normalizer", IndoSlangTransformer(fix_elongation=True, ambiguity_mode="conservative")),
    ("tfidf", TfidfVectorizer()),
    ("classifier", MultinomialNB())
])

# pipeline.fit(X_train, y_train)
```

### Antarmuka Baris Perintah (CLI)

```bash
indoslang normalize --input dataset.csv --output cleaned.csv --column teks --workers 4
```

---

## 📜 Lisensi
MIT License - lihat [LICENSE](LICENSE) untuk detail.
