"""Gold Standard evaluation script for IndoSlang-NLP accuracy and OOV reduction."""

import io
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (io.UnsupportedOperation, AttributeError):
        pass

from indoslang import IndoNormalizer

# Sample annotated gold dataset (raw informal text -> reference target)
GOLD_DATASET = [
    ("gw mager bangeeet, bsk ktmuan yaa", "saya malas gerak banget, besok ketemuan ya"),
    ("WOII @budi_99 jgn mager bangeeettt", "woi <USER> jangan malas gerak banget"),
    ("produknya bgs bgt bangeeet", "produknya bagus banget"),
    ("pelayanan kureeenggg bgt", "pelayanan kurang banget"),
    ("buku2 dan temen2nya pd ngumpul", "buku-buku dan teman-temannya pada ngumpul"),
    ("cm kamu yg bs ngertiin gw", "cuma kamu yang bisa mengerti saya"),
    ("jarak 5 cm", "jarak 5 cm"),
    ("transfer BCA no wa 08123456789", "transfer BCA nomor whatsapp <PHONE>"),
    ("saat itu maaaaf bgt", "saat itu maaf banget"),
    ("g!la sih b0d0h bgt t0x1c", "gila sih bodoh banget toxic"),
    ("100rb tahun 2024 mp4", "100rb tahun 2024 mp4"),
    ("BARANGNYA BAGUS BGT!!", "barangnya bagus banget!"),
    ("mana ada yg kek gini", "mana ada yang seperti ini"),
    ("gapapa bsk aja yaa", "tidak apa-apa besok saja ya"),
    ("makasih bnyk atas infonya", "terima kasih banyak atas informasinya"),
]


def evaluate():
    normalizer = IndoNormalizer()
    print("=" * 70)
    print(" 🇮🇩 IndoSlang-NLP Gold Standard Evaluation")
    print("=" * 70)

    total_sentences = len(GOLD_DATASET)
    sentence_matches = 0
    total_tokens = 0
    correct_tokens = 0

    for raw, expected in GOLD_DATASET:
        pred = normalizer.normalize(raw)
        if pred.strip() == expected.strip():
            sentence_matches += 1

        pred_toks = pred.split()
        exp_toks = expected.split()

        total_tokens += len(exp_toks)
        # Token-level overlap
        for pt, et in zip(pred_toks, exp_toks):
            if pt == et:
                correct_tokens += 1

    sentence_acc = (sentence_matches / total_sentences) * 100
    token_acc = (correct_tokens / total_tokens) * 100

    print(f"Total Sentences Evaluated : {total_sentences}")
    print(f"Exact Sentence Accuracy   : {sentence_acc:.1f}%")
    print(f"Token-Level Accuracy      : {token_acc:.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    evaluate()
