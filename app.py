# ENDPOIN API DAN FUNGSI 

from flask import Flask, request, jsonify
from database import db
from models.article import Article 
from models.tfidfscore import TfidfScore
# from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)

# Ganti ini ke MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/search_engine_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Langsung buat tabel saat app start
with app.app_context():
    db.create_all()


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

@app.route('/api/articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([a.to_dict() for a in articles])

@app.route('/api/search', methods=['GET'])
def search_articles():
    query = request.args.get('q', '')
    results = Article.query.filter(
        Article.judul.like(f'%{query}%') |
        Article.isi.like(f'%{query}%')
    ).all()
    return jsonify([a.to_dict() for a in results]) 

@app.route('/api/search-tfidf', methods=['GET'])
def search_tfidf():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query kosong"}), 400

    # Ambil seluruh term & score dari DB
    tfidf_data = TfidfScore.query.all()
    if not tfidf_data:
        return jsonify({"error": "TF-IDF belum di-generate"}), 500

    # Susun dictionary: {article_id: {term: score}}
    from collections import defaultdict
    article_vectors = defaultdict(dict)

    for item in tfidf_data:
        article_vectors[item.article_id][item.term] = item.score

    # Susun dokumen ulang dalam format vektor
    terms = list({item.term for item in tfidf_data})
    docs_matrix = []
    article_ids = []

    for article_id, term_scores in article_vectors.items():
        vec = [term_scores.get(term, 0.0) for term in terms]
        docs_matrix.append(vec)
        article_ids.append(article_id)

    # Vektorkan query
    query_vec = [1.0 if term in query.lower().split() else 0.0 for term in terms]

    # Hitung cosine similarity
    similarities = cosine_similarity([query_vec], docs_matrix)[0]

    # Ambil top 5 hasil
    top_indices = similarities.argsort()[::-1][:5]
    top_articles = []

    for idx in top_indices:
        article = Article.query.get(article_ids[idx])
        if article:
            top_articles.append({
                "id": article.id,
                "judul": article.judul,
                "deskripsi": article.deskripsi_singkat,
                "gambar": article.link_gambar,
                "skor": round(float(similarities[idx]), 4)
            })

    return jsonify(top_articles)

if __name__ == '__main__':
    app.run(debug=True)
