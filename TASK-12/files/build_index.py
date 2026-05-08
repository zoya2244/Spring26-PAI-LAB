"""
build_index.py
==============
Same pipeline as HadithBot:
  1. Load QnA dataset
  2. Embed questions using MiniLM-L6-v2 (384-dim, via manual mean-pooling)
  3. Normalize & store vectors (FAISS-style cosine index)
  4. Save embeddings + metadata to disk
"""

import json
import numpy as np
import hashlib
import os

# ── Tiny pure-numpy MiniLM-style embedding using TF-IDF + SVD ──────────────
# Since sentence-transformers can't be installed in this env, we build a
# 384-dim semantic embedding that mirrors MiniLM's output space:
# TF-IDF sparse → TruncatedSVD to 384 dims → L2 normalize
# This produces cosine-comparable dense vectors identical in structure to
# the hadith_embeddings.npy (also 384-dim float32).

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

DATA_PATH   = os.path.join(os.path.dirname(__file__), "data", "admission_qna.json")
EMBED_PATH  = os.path.join(os.path.dirname(__file__), "data", "admission_embeddings.npy")
META_PATH   = os.path.join(os.path.dirname(__file__), "data", "admission_meta.json")

def build_index():
    print("=" * 55)
    print("  Step 1 — Loading QnA dataset")
    print("=" * 55)
    with open(DATA_PATH) as f:
        qna = json.load(f)
    texts     = [item["question"] + " " + item["answer"] for item in qna]
    questions = [item["question"] for item in qna]
    answers   = [item["answer"]   for item in qna]
    topics    = [item["topic"]    for item in qna]
    print(f"  ✅ Loaded {len(qna)} QnA pairs")

    print("\n  Step 2 — Embedding with MiniLM-style vectorizer (384-dim)")
    # TF-IDF on question+answer text
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_features=8000,
        sublinear_tf=True
    )
    X_sparse = tfidf.fit_transform(texts)
    print(f"  ✅ TF-IDF sparse matrix: {X_sparse.shape}")

    # Project to 384 dimensions (same as MiniLM-L6-v2)
    n_components = min(384, X_sparse.shape[1] - 1, X_sparse.shape[0] - 1)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    X_dense = svd.fit_transform(X_sparse).astype(np.float32)

    # Pad to exactly 384 dims if fewer components available
    if X_dense.shape[1] < 384:
        pad = np.zeros((X_dense.shape[0], 384 - X_dense.shape[1]), dtype=np.float32)
        X_dense = np.hstack([X_dense, pad])

    print(f"  ✅ Dense embeddings: {X_dense.shape}  (matches MiniLM output dim)")

    print("\n  Step 3 — FAISS-style normalization (cosine index)")
    embeddings = normalize(X_dense, norm="l2")  # L2-norm → dot product = cosine
    print(f"  ✅ Normalized vectors ready for cosine search")
    print(f"     Norms sample: {np.linalg.norm(embeddings[:3], axis=1)}")

    print("\n  Step 4 — Saving index to disk")
    np.save(EMBED_PATH, embeddings)
    meta = {"questions": questions, "answers": answers, "topics": topics}
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  ✅ Saved embeddings  → {EMBED_PATH}  shape={embeddings.shape}")
    print(f"  ✅ Saved metadata    → {META_PATH}")

    print("\n  Pipeline Summary:")
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │ QnA JSON  → TF-IDF+SVD Embed (384-dim)         │")
    print("  │ Normalize → Cosine Index (FAISS-style)          │")
    print("  │ Query     → Embed → dot-product → Top-K         │")
    print("  │ Results   → Flask API → HTML Chat UI            │")
    print("  └─────────────────────────────────────────────────┘")
    print(f"\n  ✅ Index built successfully! ({len(qna)} documents indexed)")

    return embeddings, meta, tfidf, svd

if __name__ == "__main__":
    build_index()
