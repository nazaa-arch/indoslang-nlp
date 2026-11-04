# 📖 User Guide

## Urutan Pipeline Pemrosesan

IndoSlang-NLP menjalankan pemrosesan dalam urutan tahapan yang saling bergantung:

1. **Sanitasi & Pembersih Teks**: Unicode NFKC, penghapusan karakter Cf tersembunyi, URL, hashtag, dan masking PII.
2. **Proteksi Token**: Penandaan token yang tidak boleh dimutasi (placeholder `<USER>`, `<PHONE>`, akronim resmi `BCA`, dan kode produk numerik `100rb`, `mp4`, `4k`).
3. **Ekstraktor Sinyal Afektif**: Penghitungan rasio huruf kapital, tanda seru/tanya, dan emoticon emosional sebelum lowercasing dan kompresi tanda baca.
4. **Normalisasi Bentuk Huruf**: Case folding terkontrol menjadi huruf kecil.
5. **Dekoder Leetspeak & Algospeak**: Pemulihan kata tersandi dengan validasi perbendaharaan kata.
6. **De-elongation Adaptif**: Pengurangan huruf kembar berlebih berdasarkan kandidat per-run dan daftar putih kata rangkap baku.
7. **Resolusi Reduplikasi Klitik**: Ekspansi pola angka 2 dengan sufiks kepemilikan (`-ku`, `-mu`, `-nya`).
8. **Pencocokan Leksikon Aho-Corasick**: Substitusi kamus gaul multi-kata dalam satu kali lintasan pencarian.
9. **Emoji & Pungtuasi**: Penanganan emoji (ignore, remove, demojize) dan kompresi tanda baca berulang.
10. **Post-Processing & Spasi**: Pemulihan token terproteksi dan pembersihan spasi berlebih.

## Kebijakan Kata Ambigu

Pustaka menyediakan 3 mode untuk kata dengan arti ganda:
- `conservative` (default): Hanya mengganti kata tidak ambigu dengan confidence tinggi ($\ge 0.98$). Frasa terikat konteks (`cm kamu` $\rightarrow$ `cuma kamu`) tetap diterapkan.
- `aggressive`: Mengganti seluruh kata ambigu ke arti informal dominan (`cm` $\rightarrow$ `cuma`).
- `context_aware`: Memanfaatkan petunjuk n-gram kontekstual.
