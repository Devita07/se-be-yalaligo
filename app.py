# ENDPOIN API DAN FUNGSI 

from flask import Flask, request, jsonify
from database import db
from models.article import Article 
from models.tfidfscore import TfidfScore
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
import re
import string

app = Flask(__name__)
CORS(app)

# Setup DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/search_engine_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# 💡 Fungsi preprocessing query biar nyocok ke cleaned_content
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'http\S+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Endpoint tambah artikel
@app.route('/api/articles', methods=['POST'])
def add_article():
    data = request.json
    article = Article(
        judul=data['judul'],
        sumber=data['sumber'],
        link_gambar=data.get('link_gambar'),
        deskripsi_singkat=data.get('deskripsi_singkat'),
        isi=data['isi']
    )
    db.session.add(article)
    db.session.commit()
    return jsonify({"message": "Artikel berhasil ditambahkan!"})

# ✅ Endpoint ambil semua artikel (dengan optional paginasi)
@app.route('/api/articles', methods=['GET'])
def get_articles():
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    articles = Article.query.offset(offset).limit(limit).all()
    return jsonify([a.to_dict() for a in articles])

# ✅ Endpoint detail artikel by ID (untuk klik detail dari FE)
@app.route('/api/articles/<int:id>', methods=['GET'])
def get_article_detail(id):
    article = Article.query.get_or_404(id)
    return jsonify(article.to_dict())

# ✅ Endpoint pencarian dengan TF-IDF
@app.route('/api/search-tfidf', methods=['GET'])
def search_tfidf():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query kosong"}), 400

    query = clean_text(query)  # 💡 bersihin query dari user!

    # Ambil seluruh term & score dari DB
    tfidf_data = TfidfScore.query.all()
    if not tfidf_data:
        return jsonify({"error": "TF-IDF belum di-generate"}), 500

    # Buat vektor per artikel: {article_id: {term: score}}
    from collections import defaultdict
    article_vectors = defaultdict(dict)

    for item in tfidf_data:
        article_vectors[item.article_id][item.term] = item.score

    # Semua term yang ada
    terms = list({item.term for item in tfidf_data})

    # Vektor untuk dokumen
    docs_matrix = []
    article_ids = []

    for article_id, term_scores in article_vectors.items():
        vec = [term_scores.get(term, 0.0) for term in terms]
        docs_matrix.append(vec)
        article_ids.append(article_id)

    # Vektor query
    query_vec = [1.0 if term in query.lower().split() else 0.0 for term in terms]

    # Hitung cosine similarity
    similarities = cosine_similarity([query_vec], docs_matrix)[0]

    # Ambil top 5
    top_indices = similarities.argsort()[::-1][:5]
    top_articles = []

    for idx in top_indices:
        article = Article.query.get(article_ids[idx])
        if article:
            top_articles.append({
                "id": article.id,
                "judul": article.judul,
                "deskripsi": article.deskripsi_singkat,
                "link_gambar": article.link_gambar,  # 🔁 konsisten nama key-nya
                "skor": round(float(similarities[idx]), 4)
            })

    return jsonify(top_articles)

if __name__ == '__main__':
    app.run(debug=True)
