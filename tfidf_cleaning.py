from flask_sqlalchemy import SQLAlchemy
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer

# Inisialisasi Flask dan DB
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/search_engine_db'
db = SQLAlchemy(app)

# Model contoh
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isi = db.Column(db.Text)
    cleaned_content = db.Column(db.Text)  # kolom buat nyimpan hasil bersih (optional)

# Fungsi cleaning
def clean_text(text):
    text = text.lower()  # lowercase
    text = re.sub(r'\d+', '', text)  # hapus angka
    text = re.sub(r'http\S+', '', text)  # hapus link
    text = text.translate(str.maketrans('', '', string.punctuation))  # hapus tanda baca
    text = re.sub(r'\s+', ' ', text).strip()  # hapus spasi berlebih
    return text

# Pembersihan data
with app.app_context():
    articles = Article.query.all()
    for article in articles:
        article.cleaned_content = clean_text(article.isi)
    db.session.commit()

print("Data berhasil dibersihkan dan disimpan ke kolom 'cleaned_content' ✨")

# Misalnya kita ambil data bersihnya
with app.app_context():
    texts = [a.cleaned_content for a in Article.query.all()]

# Hitung TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform([a.cleaned_content for a in articles])