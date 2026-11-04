# 🤝 Panduan Kontribusi (Contributing Guide)

Terima kasih atas ketertarikan Anda untuk berkontribusi pada pengembangan **IndoSlang-NLP**!

## Alur Kontribusi

1. **Fork Repositori:** Buat branch fitur dari `main` (misal: `feat/tambah-kata-slang-baru`).
2. **Setup Lingkungan Pengembang:**
   ```bash
   pip install -e ".[dev]"
   ```
3. **Menambahkan Kosakata Baru ke Kamus:**
   - Masukkan entri ke berkas yang sesuai di `indoslang/data/dictionaries/`.
   - Pastikan entri memiliki format yang valid:
     ```json
     "kata": {
       "senses": [
         {"normalized": "kata baku", "category": "slang", "confidence": 1.0}
       ],
       "ambiguous": false,
       "source": "sumber_rujukan",
       "license": "MIT"
     }
     ```
   - Pastikan aturan **anti-chaining** terpenuhi (nilai `normalized` tidak boleh menjadi kata kunci di kamus).
4. **Jalankan Pengujian Unit & Validasi Skema:**
   ```bash
   pytest
   ```
5. **Kirim Pull Request (PR):** Cantumkan deskripsi jelas mengenai perubahan dan contoh penggunaannya.
