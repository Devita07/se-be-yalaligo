import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app               # 🟢 Import langsung objek Flask app dari app.py
from database import db
from models.article import Article
from models.tfidfscore import TfidfScore

from sklearn.feature_extraction.text import TfidfVectorizer

with app.app_context():
    articles = Article.query.all()

    docs = [a.deskripsi_singkat for a in articles]  # atau 'isi' → sesuai field kamu
    ids = [a.id for a in articles]

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(docs)
    feature_names = vectorizer.get_feature_names_out()

    for i, article_id in enumerate(ids):
        row = tfidf_matrix[i]
        for col_idx in row.nonzero()[1]:
            term = feature_names[col_idx]
            score = row[0, col_idx]
            tfidf_entry = TfidfScore(article_id=article_id, term=term, score=score)
            db.session.add(tfidf_entry)

    db.session.commit()
    print("✅ TF-IDF scores berhasil disimpan ke database!")
