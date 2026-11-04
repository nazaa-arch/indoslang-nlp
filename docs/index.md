# 🇮🇩 IndoSlang-NLP Documentation

Selamat datang di dokumentasi resmi **IndoSlang-NLP**, pustaka Python berkinerja tinggi, modular, dan deterministik untuk normalisasi bahasa gaul, singkatan percakapan, kata leetspeak/algospeak, dan elongasi kata pada teks media sosial Bahasa Indonesia.

## 🌟 Fitur Unggulan

- **Matching Cepat Aho-Corasick:** Kompleksitas $O(N + Z)$ berbasis `ahocorasick-rs` dengan cadangan trie murni Python.
- **De-elongation Kontekstual Berbasis Whitelist:** Mengurangi perpanjangan karakter berulang (`bangeeettt` $\rightarrow$ `banget`) tanpa merusak kata baku dengan huruf kembar (`saat`, `maaf`, `cemooh`).
- **Dekoder Leetspeak Cerdas:** Mengubah leetspeak (`g!la` $\rightarrow$ `gila`, `b0d0h` $\rightarrow$ `bodoh`) dengan validasi kosakata agar angka kuantitatif (`2024`, `100rb`) tidak rusak.
- **Resolusi Reduplikasi Klitik:** Mendukung angka 2 bersambung afiks (`temen2nya` $\rightarrow$ `teman-temannya`).
- **Pelestarian Sinyal Emosi:** Ekstraksi fitur afektif (caps ratio, tanda seru, intensitas elongasi) untuk analisis sentimen.
- **Integrasi Scikit-Learn Native:** Mendukung `Pipeline` dan `GridSearchCV` melalui `IndoSlangTransformer`.

## 📦 Panduan Cepat

```bash
pip install indoslang-nlp
```

```python
from indoslang import IndoNormalizer

normalizer = IndoNormalizer()
print(normalizer.normalize("gw mager bangeeet, bsk ktmuan yaa"))
# Output: "saya malas gerak banget, besok ketemuan ya"
```
