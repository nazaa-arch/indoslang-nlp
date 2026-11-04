import json
from pathlib import Path

def create_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.13"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

def code_cell(code):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip().split("\n")]
    }

def md_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")]
    }

# 1. Tutorial Dasar
nb1 = create_notebook([
    md_cell("# 🇮🇩 IndoSlang-NLP: Tutorial Dasar Normalisasi Teks\n\nTutorial ini mendemonstrasikan cara menggunakan `indoslang-nlp` untuk menormalkan teks gaul, singkatan, leetspeak, reduplikasi, dan masking PII."),
    code_cell("from indoslang import IndoNormalizer\n\nnormalizer = IndoNormalizer()\ntext = 'gw mager bangeeet, bsk ktmuan yaa di Jaksel!!'\nprint('Input:', text)\nprint('Output:', normalizer.normalize(text))"),
    md_cell("## 1. De-elongasi dan Leetspeak\nMengatasi huruf berulang (*elongation*) dan penggantian karakter (*leetspeak*) secara deterministik."),
    code_cell("sample = 'b0d0h bgt sih lu, parahhh bangeeettt!'\nprint(normalizer.normalize(sample))"),
    md_cell("## 2. Pelestarian Sinyal Emosi (*Affective Features*)\nMempertahankan sinyal kapitalisasi, tanda baca seru/tanya, dan emoticon untuk model sentimen."),
    code_cell("norm_affect = IndoNormalizer(extract_features=True)\ndoc = norm_affect.process('PARAHHH BANGEEETTT SIHHH GAK JELAS BGT!!! 😡😡')\nprint('Teks Bersih:', doc.text)\nprint('Fitur Afektif:', doc.features)"),
    md_cell("## 3. Mode Jejak Transparan (*Explainability Trace*)\nMenelusuri setiap mutasi kata langkah demi langkah."),
    code_cell("doc_trace = normalizer.process('gw mager bgt', trace=True)\nfor step in doc_trace.trace_steps:\n    print(f'[{step.stage}] {step.original_token} -> {step.transformed_token} ({step.rule_source})')")
])
Path("notebooks/01_tutorial_dasar.ipynb").write_text(json.dumps(nb1, indent=2), encoding="utf-8")

# 2. Integrasi Sklearn Pipeline
nb2 = create_notebook([
    md_cell("# 🤖 Integrasi IndoSlang-NLP dengan Scikit-Learn Pipeline\n\nTutorial ini menunjukkan integrasi `IndoSlangTransformer` ke dalam `sklearn.pipeline.Pipeline`."),
    code_cell("from sklearn.pipeline import Pipeline\nfrom sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.naive_bayes import MultinomialNB\nfrom indoslang.sklearn import IndoSlangTransformer\n\nX_train = [\n    'produknya bgs bgt bangeeet, suka bgt!',\n    'pelayanan kureeenggg bgt jelek parah',\n    'mantul gan barang cpt sampai',\n    'kecewa bgt t0x1c sellernya gak ramah'\n]\ny_train = [1, 0, 1, 0]\n\npipeline = Pipeline([\n    ('normalizer', IndoSlangTransformer(fix_elongation=True, ambiguity_mode='conservative')),\n    ('tfidf', TfidfVectorizer()),\n    ('classifier', MultinomialNB())\n])\n\npipeline.fit(X_train, y_train)\nprint('Model berhasil dilatih dengan IndoSlang-NLP preprocessing!')\n\nX_test = ['barangnya bgs bangeeet']\npred = pipeline.predict(X_test)\nprint(f'Prediksi untuk \"{X_test[0]}\":', 'Positif' if pred[0] == 1 else 'Negatif')")
])
Path("notebooks/02_integrasi_sklearn_pipeline.ipynb").write_text(json.dumps(nb2, indent=2), encoding="utf-8")

# 3. Analisis Sentimen Benchmark
nb3 = create_notebook([
    md_cell("# 📊 Analisis Sentimen: Pengaruh Normalisasi IndoSlang-NLP\n\nMembandingkan representasi fitur teks sebelum dan sesudah normalisasi slang/singkatan."),
    code_cell("import pandas as pd\nfrom indoslang import IndoNormalizer\n\nreviews = [\n    'gw suka bgt sma produk ini, mantul bangeeet',\n    'jgn beli disini, nyesel parah kureng bgt',\n    'packing rapih, respon cepet, makasih bnyk yaa',\n    'b0d0h bgt pelayanannya, gak rekomen blass'\n]\n\ndf = pd.DataFrame({'ulasan_mentah': reviews})\nnormalizer = IndoNormalizer()\ndf['ulasan_bersih'] = normalizer.transform_batch(df['ulasan_mentah'].tolist())\nprint(df.to_string())")
])
Path("notebooks/03_analisis_sentimen_benchmark.ipynb").write_text(json.dumps(nb3, indent=2), encoding="utf-8")
print("Successfully created 3 notebooks in notebooks/")
