# SmartStunting — Migrasi ke Django

Project ini merupakan migrasi dari aplikasi Streamlit ke Django. Mesin inferensi fuzzy Mamdani (`core/fuzzy_engine.py`) dan loader dataset dipertahankan dari project sumber.

## Kebutuhan
- Windows 10/11
- Python 3.10 atau lebih baru
- VS Code (opsional)

## Struktur folder
- `manage.py`: perintah Django (berada langsung di folder root project)
- `smartstunting/`: konfigurasi project, URL, ASGI, dan WSGI
- `core/`: views, URL, mesin fuzzy, pembaca dataset, dan template tags
- `templates/`: base template dan halaman HTML Django
- `static/core/style.css`: stylesheet aplikasi
- `data/Data Stunting Indonesia.csv`: dataset sumber
- `db.sqlite3`: database lokal Django
- `requirements.txt`: dependensi Python

## Setup di Windows / VS Code

1. Ekstrak ZIP ini ke folder yang mudah ditemukan, misalnya `C:\Users\Lenovo\Downloads\SmartStunting_Django`.
2. Buka folder root `SmartStunting_Django` melalui VS Code (**File > Open Folder**). Folder ini berisi `manage.py`, `requirements.txt`, `core/`, dan `smartstunting/`.
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
   $env:DJANGO_DEBUG = "True"
   python manage.py runserver
   ```

   `DJANGO_DEBUG=True` diperlukan saat pengembangan lokal agar Django menyajikan file CSS dan file statis lainnya. Jangan gunakan nilai ini di deployment produksi.

9. Buka browser ke:

   `http://127.0.0.1:8000/`

## Deploy ke Vercel

Vercel mendeteksi Django dari `manage.py` di root proyek, menggunakan entry point WSGI/ASGI yang dikonfigurasi, dan mengumpulkan file statis dari `STATIC_ROOT`. Karena itu, proyek ini tidak memerlukan `vercel.json` atau build command khusus. Pastikan **Root Directory** proyek Vercel menunjuk ke folder yang berisi `manage.py` dan `requirements.txt`.

Sebelum deploy, atur environment variables berikut di **Vercel > Project Settings > Environment Variables** untuk Production, Preview, dan Development:

| Nama | Nilai |
|---|---|
| `DJANGO_SECRET_KEY` | Secret key acak; buat dengan perintah di bawah |
| `DJANGO_DEBUG` | `False` |

Buat secret key di terminal lokal:

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Salin hasilnya sebagai nilai `DJANGO_SECRET_KEY` di Vercel; jangan commit nilainya ke Git. Aktifkan juga **System Environment Variables** agar Vercel menyediakan hostname deployment. Settings akan memakai `VERCEL_URL`, `VERCEL_BRANCH_URL`, dan `VERCEL_PROJECT_PRODUCTION_URL` untuk host serta origin CSRF.

Jika memakai domain kustom, tambahkan:

- `DJANGO_ALLOWED_HOSTS`: hostname dipisah koma, tanpa `https://` (contoh: `contoh.com,www.contoh.com`).
- `DJANGO_CSRF_TRUSTED_ORIGINS`: origin lengkap dipisah koma (contoh: `https://contoh.com,https://www.contoh.com`).

Setelah variables tersimpan, deploy repository melalui dashboard Vercel. Fitur kuis menyimpan state kecil menggunakan signed cookie, sehingga tidak bergantung pada file SQLite yang tidak persisten di Vercel. `db.sqlite3` tetap hanya untuk lokal. Database terkelola belum dikonfigurasi; jika aplikasi memerlukan penyimpanan data permanen atau admin yang bisa menulis data, tambahkan integrasi database (misalnya PostgreSQL) ke `requirements.txt` dan settings sebelum menggunakannya.

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
