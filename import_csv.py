# INI FUNGSI UNTUK IMPORT CV MENJADI DATA DI TABEL SESUAI NAMA KOLOM

import csv
from app import app, db
from models.article import Article

def import_csv(file_path):
    with app.app_context():
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                article = Article(
                    judul=row['Judul'],
                    sumber=row['Sumber'],
                    link_gambar=row.get('Gambar'),
                    deskripsi_singkat=row.get('Deskripsi_Singkat'),
                    isi=row['Isi']
                )
                db.session.add(article)
            db.session.commit()
            print("Import selesai ke database MySQL!")

if __name__ == "__main__":
    import_csv('gabungan.csv')
