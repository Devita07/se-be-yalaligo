# INI MODEL UNTUK INISIALISASI KOLOM DI TABEL DATABSESNYA

from database import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(255), nullable=False)
    sumber = db.Column(db.String(100), nullable=False)
    link_gambar = db.Column(db.String(255), nullable=True)
    deskripsi_singkat = db.Column(db.Text, nullable=True)
    isi = db.Column(db.Text, nullable=False)
    cleaned_content = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "judul": self.judul,
            "sumber": self.sumber,
            "link_gambar": self.link_gambar,
            "deskripsi_singkat": self.deskripsi_singkat,
            "isi": self.isi
        }
    

