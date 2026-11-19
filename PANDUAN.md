# ListrikSmart: Panduan Instalasi dari Nol

Zip ini adalah proyek **lengkap** (kode, tampilan, model Machine Learning `.pkl`, migration).
Satu-satunya yang tidak ada: folder `venv` (dibuat ulang) dan file `.env` (kamu isi sendiri).

## 0. Sebelum mulai
- Data riwayat prediksi ada di **PostgreSQL** (`db_listrik`), bukan di folder proyek. Selama database itu tidak kamu hapus, data lamamu tetap ada.
- Pastikan PostgreSQL berjalan dan database `db_listrik` masih ada.
- Saran: jangan hapus folder proyek lama dulu. Simpan sebagai cadangan sampai versi baru berjalan.
- Hentikan server lama (Ctrl+C) bila masih berjalan.

## 1. Ekstrak
Ekstrak zip ke lokasi yang kamu mau, misalnya `C:\Users\mici\`. Hasilnya folder `mini_project_listrik`.
Kalau folder lama bernama sama, ganti nama folder lama lebih dulu (misalnya `mini_project_listrik_lama`).

## 2. Buat virtual environment dan pasang paket
```powershell
cd C:\Users\mici\mini_project_listrik
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Kalau ada paket yang gagal terpasang, kirim pesan errornya.

## 3. Buat file .env
```powershell
copy .env.example .env
```
Buka `.env` di VS Code lalu isi:

| Isian | Cara mengisi |
|---|---|
| `DB_PASSWORD` | Password PostgreSQL kamu |
| `DJANGO_SECRET_KEY` | Jalankan perintah di bawah, tempel hasilnya di antara tanda kutip tunggal |
| `GEMINI_API_KEY` | Nilai secret `P09` di Colab (cara di bawah) |

```powershell
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

### Memindahkan API Key dari Colab (secret `P09`)
1. Di Colab, klik ikon kunci di sisi kiri (**Secrets**).
2. Pada baris `P09`, klik ikon mata, lalu salin nilainya.
3. Tempel di `.env`: `GEMINI_API_KEY=nilai_yang_disalin` (tanpa spasi dan tanpa tanda kutip).
4. Jangan kirim nilai itu ke siapa pun. Kalau pernah terlanjur terbagikan, buat kunci baru di Google AI Studio.

## 4. Siapkan database dan jalankan
```powershell
python manage.py check
python manage.py migrate
python manage.py runserver
```
- Kalau memakai database `db_listrik` yang lama: `migrate` tidak menghapus apa pun. Data riwayat lama tetap tampil.
- Kalau database baru atau kosong: `migrate` membuat semua tabel, termasuk `RiwayatPrediksi`.
- Opsional, untuk membuka `/admin/`: `python manage.py createsuperuser`

Buka http://127.0.0.1:8000/

## 5. Daftar uji (berurutan)
1. **Dashboard** `/`: sapaan, kartu angka, grafik, dan aktivitas terbaru.
2. **Prediksi Biaya** `/prediksi/`: isi form lalu kirim. Coba juga kolom kosong atau jam AC = 99, harus muncul error dan tidak tersimpan.
3. **Riwayat** `/riwayat/`: cari, filter kategori, filter tanggal, dan buka detail.
4. **Visualisasi** `/visualisasi/`: tiga grafik (butuh internet untuk Chart.js).
5. **Asisten AI** `/asisten/`: klik "Analisis hasil prediksi". Jawaban harus menyebut angka dari prediksimu.
6. **Tentang** `/tentang/`.
7. **HP**: kecilkan jendela browser sampai di bawah 900 px, sidebar berubah menjadi tombol menu.

## 6. Kalau ada masalah
| Gejala | Penyebab dan solusi |
|---|---|
| `password authentication failed for user "postgres"` | `DB_PASSWORD` di `.env` salah atau kosong |
| `database "db_listrik" does not exist` | Buat database `db_listrik` di pgAdmin, lalu jalankan `migrate` |
| `connection refused` | Layanan PostgreSQL belum berjalan |
| Chat: "GEMINI_API_KEY belum diisi" | `.env` belum terisi, atau server belum di-restart |
| Chat: "API Key ... ditolak" | Nilai kunci salah atau sudah dicabut |
| Chat: "Batas penggunaan ... tercapai" | Kuota Gemini habis. Cek di Google AI Studio |
| Chat: "Model Gemini tidak ditemukan" | Ganti `GEMINI_MODEL` di `.env` dengan model yang tersedia di akunmu |
| Peringatan versi scikit-learn saat memuat model | Pastikan memakai `requirements.txt` (scikit-learn 1.9.1) |
| Grafik kosong | Tidak ada internet, atau CDN Chart.js terblokir |

## 7. Catatan
- Model Gemini bawaan: `gemini-3.8-flash` (stabil di dokumentasi Gemini API per November 2026). `gemini-2.5-flash` dijadwalkan dimatikan 1 Desember 2026. Kuota gratis tergantung akun Google AI Studio kamu.
- Jangan unggah `.env` ke GitHub (sudah ada di `.gitignore`).
- Hasil model berasal dari data sintetis, jadi tampilkan sebagai **estimasi**, bukan tagihan PLN.
