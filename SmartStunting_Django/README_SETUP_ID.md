# SmartStunting — Migrasi ke Django

Project ini merupakan migrasi dari aplikasi Streamlit ke Django. Mesin inferensi fuzzy Mamdani (`core/fuzzy_engine.py`) dan loader dataset dipertahankan dari project sumber.

## Kebutuhan
- Windows 10/11
- Python 3.10 atau lebih baru
- VS Code (opsional)

## Struktur folder
- `manage.py`: perintah Django
- `smartstunting/`: konfigurasi project Django
- `core/`: views, URL, mesin fuzzy, dan pembaca dataset
- `templates/`: halaman HTML Django
- `static/core/style.css`: desain
- `data/Data Stunting Indonesia.csv`: dataset asli

## Setup di Windows / VS Code

1. Ekstrak ZIP ini ke folder yang mudah ditemukan, misalnya `C:\Users\Lenovo\Downloads\SmartStunting_Django`.
2. Buka folder `SmartStunting_Django` melalui VS Code (**File > Open Folder**). Pastikan yang dibuka adalah folder yang berisi `manage.py`.
3. Buka terminal VS Code (**Terminal > New Terminal**).
4. Buat virtual environment:

   ```powershell
   py -3 -m venv .venv
   ```

   Jika perintah `py` tidak tersedia tetapi `python --version` berfungsi, gunakan:

   ```powershell
   python -m venv .venv
   ```

5. Aktifkan environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Jika PowerShell menolak aktivasi karena kebijakan skrip, jalankan untuk terminal saat ini:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

6. Instal dependensi:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

7. Buat tabel internal Django:

   ```powershell
   python manage.py migrate
   ```

8. Jalankan server:

   ```powershell
   python manage.py runserver
   ```

9. Buka browser ke:

   `http://127.0.0.1:8000/`

## Halaman
- `/` Beranda
- `/konsultasi/` Konsultasi fuzzy
- `/basis-pengetahuan/` Basis pengetahuan
- `/uji-dugaan/` Uji dugaan
- `/dashboard/` Dashboard statistik
- `/dataset/` Dataset dan filter
- `/dataset/unduh/` Unduh CSV hasil analisis

## Catatan
- Project sumber adalah Streamlit. Migrasi ini mengubah lapisan antarmuka dan routing ke Django; fungsi inferensi fuzzy dan dataset sumber dipertahankan.
- Grafik dashboard menggunakan Plotly.js dari CDN, sehingga grafik memerlukan koneksi internet saat halaman dibuka.
- Label prioritas merupakan hasil model fuzzy untuk tujuan edukasi/akademik, bukan diagnosis medis atau keputusan kebijakan.
- `DEBUG=True` dan `SECRET_KEY` bawaan hanya untuk pengembangan lokal. Ubah sebelum deployment publik.
