"""
app.py  —  University Admission QnA Bot
========================================
Pipeline (identical to HadithBot):
  • Load pre-built embeddings (admission_embeddings.npy)
  • Embed incoming query using same TF-IDF + SVD + L2-norm
  • Dot-product similarity → Top-K results  (FAISS-style)
  • Return best answer via Flask JSON API
"""

from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
import numpy as np
import json, os, re

app = Flask(__name__)

BASE = os.path.dirname(__file__)

# ── Load pre-built index (same as hadith_embeddings.npy pattern) ───────────
print("Loading admission index …")
embeddings = np.load(os.path.join(BASE, "data", "admission_embeddings.npy"))
with open(os.path.join(BASE, "data", "admission_meta.json")) as f:
    meta = json.load(f)
with open(os.path.join(BASE, "data", "admission_qna.json")) as f:
    qna_raw = json.load(f)

questions = meta["questions"]
answers   = meta["answers"]
topics    = meta["topics"]

# ── Fit vectorizer on same corpus (restore pipeline state) ─────────────────
corpus = [q + " " + a for q, a in zip(questions, answers)]
tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=8000, sublinear_tf=True)
X_sparse = tfidf.fit_transform(corpus)

n_components = min(384, X_sparse.shape[1] - 1, X_sparse.shape[0] - 1)
svd = TruncatedSVD(n_components=n_components, random_state=42)
svd.fit(X_sparse)

print(f"✅ Index loaded: {embeddings.shape[0]} documents, {embeddings.shape[1]}-dim vectors")


def embed_query(text: str) -> np.ndarray:
    """Embed a query using same pipeline as index construction."""
    vec = tfidf.transform([text])
    dense = svd.transform(vec).astype(np.float32)
    if dense.shape[1] < 384:
        pad = np.zeros((1, 384 - dense.shape[1]), dtype=np.float32)
        dense = np.hstack([dense, pad])
    return normalize(dense, norm="l2")   # L2 norm → cosine via dot product


def search(query: str, top_k: int = 3):
    """
    FAISS-style cosine search:
      dot(query_norm, doc_norm) == cosine_similarity  (both L2-normalized)
    """
    q_vec  = embed_query(query)               # (1, 384)
    scores = (embeddings @ q_vec.T).flatten() # dot product = cosine
    top_idx = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in top_idx:
        results.append({
            "question": questions[idx],
            "answer":   answers[idx],
            "topic":    topics[idx],
            "score":    float(scores[idx])
        })
    return results


# ── Topic badge colours ─────────────────────────────────────────────────────
TOPIC_COLORS = {
    "Computer Science":      "#3b82f6",
    "Business Administration":"#8b5cf6",
    "Data Science":          "#06b6d4",
    "Mechanical Engineering":"#f59e0b",
    "Medicine":              "#ef4444",
    "Psychology":            "#ec4899",
    "Financial Aid":         "#10b981",
    "Deadlines":             "#f97316",
    "Requirements":          "#6366f1",
    "Application Process":   "#14b8a6",
    "International":         "#0ea5e9",
    "Contact":               "#84cc16",
    "Tuition":               "#a855f7",
    "Campus Life":           "#fb923c",
    "Admission Statistics":  "#64748b",
    "Programs":              "#2563eb",
}

TOPIC_ICONS = {
    "Computer Science":       "💻",
    "Business Administration":"📊",
    "Data Science":           "📈",
    "Mechanical Engineering": "⚙️",
    "Medicine":               "🏥",
    "Psychology":             "🧠",
    "Financial Aid":          "💰",
    "Deadlines":              "📅",
    "Requirements":           "📋",
    "Application Process":    "📝",
    "International":          "🌍",
    "Contact":                "📞",
    "Tuition":                "💵",
    "Campus Life":            "🏛️",
    "Admission Statistics":   "📊",
    "Programs":               "🎓",
}


@app.route("/")
def index():
    topic_list = sorted(set(topics))
    return render_template("index.html",
                           topic_list=topic_list,
                           topic_colors=TOPIC_COLORS,
                           topic_icons=TOPIC_ICONS)


@app.route("/search", methods=["POST"])
def search_api():
    data  = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    results = search(query, top_k=3)

    # Attach colors and icons
    for r in results:
        r["color"] = TOPIC_COLORS.get(r["topic"], "#64748b")
        r["icon"]  = TOPIC_ICONS.get(r["topic"], "🎓")
        # Confidence label
        s = r["score"]
        r["confidence"] = "High" if s > 0.6 else "Medium" if s > 0.3 else "Low"

    return jsonify({"query": query, "results": results})


@app.route("/topics", methods=["GET"])
def get_topics():
    topic = request.args.get("topic", "")
    filtered = [
        {"question": q, "answer": a, "topic": t,
         "color": TOPIC_COLORS.get(t, "#64748b"),
         "icon":  TOPIC_ICONS.get(t, "🎓")}
        for q, a, t in zip(questions, answers, topics)
        if topic.lower() in t.lower()
    ]
    return jsonify({"topic": topic, "results": filtered})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
