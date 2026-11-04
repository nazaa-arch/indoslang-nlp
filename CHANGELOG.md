# 📝 Changelog

Semua perubahan penting pada proyek **IndoSlang-NLP** dicatat di dokumen ini sesuai standar [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) dan [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-04

### Ditambahkan (*Added*)
- Implementasi arsitektur pipeline 10 tahap berurutan (*order-dependent*).
- Mesin sanitasi teks `TextCleaner` dengan normalisasi Unicode NFKC dan pembersihan karakter `Cf`.
- Deteksi dan masking privasi PII (`PIIMasker`) untuk ponsel Indonesia, email, mention `@user`, NIK (16 digit), dan kartu/rekening dengan validasi algoritma Luhn.
- Mekanisme perlindungan token `TokenProtector` untuk placeholder sistem, akronim resmi, dan pengecualian numerik (`100rb`, `2024`, `mp4`, `4k`, `3x`).
- Ekstraktor sinyal afektif `AffectiveFeatureExtractor` (caps ratio, tanda seru/tanya, emoticon negatif, dan elongasi).
- Mesin de-elongation adaptif `DeElongator` dengan kandidat per-run dan daftar putih kata baku rangkap.
- Dekoder leetspeak dan algospeak `LeetspeakDecoder` berbasis validasi kosakata.
- Resolusi reduplikasi dan klitik morfologis `ReduplicationResolver` (`temen2nya` $\rightarrow$ `teman-temannya`).
- Automaton pencocokan leksikon `LexiconMatcher` berbasis Aho-Corasick dengan fallback pure-Python trie.
- Pustaka kamus bawaan 1.000+ entri tervalidasi JSON schema (`abbreviations.json`, `slang_base.json`, `indoglish.json`, `regional_slang.json`).
- Integrasi Scikit-Learn Pipeline melalui `IndoSlangTransformer`.
- Antarmuka baris perintah (`indoslang normalize` dan `indoslang update-dicts`).
- Rangkaian pengujian unit, properti (Hypothesis), dan validasi skema (50 pengujian lulus).
- Skrip benchmark kecepatan dan pembanding baseline naif `re.sub`.
