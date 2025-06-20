# ENDPOIN API DAN FUNGSI 

from flask import Flask, request, jsonify
from database import db
from models.article import Article 
from models.tfidfscore import TfidfScore


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

if __name__ == '__main__':
    app.run(debug=True)
