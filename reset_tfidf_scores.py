from app import app
from database import db
from models.tfidfscore import TfidfScore

with app.app_context():
    deleted_rows = TfidfScore.query.delete()
    db.session.commit()
    print(f"🧹 {deleted_rows} baris di tabel tfidf_scores berhasil dihapus.")
