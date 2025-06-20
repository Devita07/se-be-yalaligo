import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import db  # atau sesuaikan dengan path db-mu

class TfidfScore(db.Model):
    __tablename__ = 'tfidf_scores'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, nullable=False)
    term = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Float, nullable=False)

    def __init__(self, article_id, term, score):
        self.article_id = article_id
        self.term = term
        self.score = score
