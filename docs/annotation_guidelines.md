# ✍️ Pedoman Anotasi Dataset Gold Standard

Dokumen ini menjadi acuan anotator manusia dalam menyusun *Gold Standard Dataset* untuk evaluasi akurasi normalisasi teks Bahasa Indonesia informal.

## 1. Prinsip Dasar
- **Deterministik & Minimal Edit:** Gunakan bentuk baku Bahasa Indonesia (KBBI) dengan seminimal mungkin mengubah struktur kalimat asli.
- **Konservasi Makna:** Jangan mengubah kata slang jika maknanya tidak memiliki padanan kata tunggal baku tanpa merusak konteks (atau gunakan padanan frasa yang paling lazim).

## 2. Aturan Khusus Kasus
- **Singkatan Chat:** Ubah ke kata baku lengkap (`jgn` $\rightarrow$ `jangan`, `bgt` $\rightarrow$ `banget`, `bsk` $\rightarrow$ `besok`).
- **Kata Ganti Orang Gaul:**
  - `gw` / `gue` $\rightarrow$ `saya`
  - `lu` / `lo` $\rightarrow$ `kamu`
- **Kata Reduplikasi Berangka:**
  - `buku2` $\rightarrow$ `buku-buku`
  - `temen2nya` $\rightarrow$ `teman-temannya`
- **Masking PII:**
  - Akun media sosial `@nama_akun` $\rightarrow$ `<USER>`
  - Nomor ponsel $\rightarrow$ `<PHONE>`
  - Email $\rightarrow$ `<EMAIL>`
  - Nomor NIK (16 digit) $\rightarrow$ `<ID_NUMBER>`
  - Rekening/Kartu $\rightarrow$ `<ACCOUNT>`
- **Kata dengan Huruf Rangkap Baku:**
  - `saat`, `maaf`, `taat`, `cemooh`, `massa` **tidak boleh** dipotong hurufnya menjadi 1 karakter.
