# 📚 API Reference

## `IndoNormalizer`

Kelas orkestrator utama untuk melakukan normalisasi teks informal.

```python
from indoslang import IndoNormalizer

normalizer = IndoNormalizer(
    ambiguity_mode="conservative",     # 'conservative' | 'aggressive' | 'context_aware'
    fix_elongation=True,               # De-elongasi huruf berulang
    fix_leetspeak=True,                # Dekode angka/simbol pengganti huruf
    expand_reduplication=True,         # Resolusi kata2 -> kata-kata
    clean_social_tags=True,            # Bersihkan URL, @mention, #hashtag
    mask_pii=True,                     # Samarkan nomor ponsel, email, NIK
    emoji="ignore",                    # 'ignore' | 'remove' | 'demojize'
    preserve_acronyms=True,            # Lindungi akronim resmi all-caps (BCA, DKI)
    lowercase=True,                    # Case folding teks
    translate_indoglish=False,         # Padanan bahasa Indonesia untuk istilah Jaksel
    extract_features=False,            # Hitung sinyal afektif
    extra_lexicons=None,               # Jalur berkas kamus kustom tambahan
    dict_version="2026.11"             # Versi kamus yang digunakan
)
```

### Metode Utama

#### `normalize(text: Any) -> str`
Mengembalikan string hasil normalisasi secara konsisten. Menerima string, None, atau tipe lain (di-cast secara aman).

#### `process(text: Any, trace: bool = False) -> NormalizedDoc`
Mengembalikan objek `NormalizedDoc` yang memuat:
- `text: str`: Teks bersih hasil normalisasi.
- `features: dict`: Fitur afektif (caps ratio, tanda seru, dll.).
- `trace_steps: list[TraceStep]`: Jejak audit tiap mutasi kata jika `trace=True`.
- `meta: dict`: Informasi versi pustaka, versi kamus, dan config hash.

#### `transform_batch(texts: list[str], n_jobs: int = 1, batch_size: int = 1000) -> list[str]`
Memproses kumpulan teks secara massal dengan multiprocessing paralel.

#### `from_config(config_path: str | Path) -> IndoNormalizer`
Menginstansiasi normalizer dari berkas konfigurasi `.toml` atau `.json`.

---

## `IndoSlangTransformer`

Transformer scikit-learn untuk digunakan dalam `sklearn.pipeline.Pipeline`.

```python
from indoslang.sklearn import IndoSlangTransformer

transformer = IndoSlangTransformer(
    fix_elongation=True,
    ambiguity_mode="conservative"
)
```

### Metode

- `fit(X, y=None)`: Menyiapkan estimator (no-op).
- `transform(X) -> list[str]`: Mentransformasi koleksi teks.
