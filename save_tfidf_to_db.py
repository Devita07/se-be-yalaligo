from app import db
from models.article import Article
from models.tfidfscore import TfidfScore

from sklearn.feature_extraction.text import TfidfVectorizer

# Ambil semua artikel dari database
articles = Article.query.all()

# Simpan ID dan teksnya
article_ids = []
documents = []

for article in articles:
    if article.cleaned_content:  # Pastikan udah ada cleaned content
        article_ids.append(article.id)
        documents.append(article.cleaned_content)
    else:
        print(f"Artikel ID {article.id} tidak punya cleaned_content")

# Hitung TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)
feature_names = vectorizer.get_feature_names_out()

# Simpan ke database
for doc_idx, article_id in enumerate(article_ids):
    tfidf_scores = tfidf_matrix[doc_idx].toarray()[0]
    for term_idx, score in enumerate(tfidf_scores):
        if score > 0:
            term = feature_names[term_idx]
            tfidf_entry = TfidfScore(article_id=article_id, term=term, score=score)
            db.session.add(tfidf_entry)

# Commit semua
db.session.commit()
print("TF-IDF berhasil disimpan ke database! 💖")
