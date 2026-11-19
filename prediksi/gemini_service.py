
"""
Integrasi Google Gemini (library google-genai).

API Key dibaca dari environment variable GEMINI_API_KEY (file .env).
Pemanggilan hanya dilakukan dari backend Django, tidak pernah dari browser.
"""

import logging
import os

logger = logging.getLogger(__name__)

# Model dapat diganti lewat .env tanpa mengubah kode
MODEL_DEFAULT = 'gemini-3.8-flash'

INSTRUKSI_SISTEM = """Kamu adalah Asisten ListrikSmart, pemandu penghematan listrik rumah tangga di Indonesia.
Aturan:
- Jawab dalam bahasa Indonesia yang sederhana, ramah, dan mudah dipahami.
- Gunakan HANYA angka yang ada pada bagian "DATA PREDIKSI". Jangan mengarang angka biaya, kWh, atau persentase.
- Hasil prediksi berasal dari model Machine Learning yang dilatih dengan data simulasi, jadi sebut hasilnya sebagai estimasi, bukan tagihan resmi PLN.
- Jika ada data prediksi, kaitkan jawaban dengan data tersebut (misalnya perangkat dengan jam pakai terbesar).
- Jika tidak ada data prediksi, beri tips umum dan sarankan pengguna melakukan prediksi dulu.
- Berikan saran praktis dan terukur (misalnya mengatur suhu AC, mematikan perangkat standby, mengganti lampu).
- Jawab ringkas, maksimal sekitar 250 kata. Boleh memakai daftar bertanda "-" dan huruf tebal **seperti ini**.
- Jika pertanyaan tidak berkaitan dengan listrik, energi, atau aplikasi ini, tolak dengan sopan dan arahkan kembali ke topik listrik."""

INSTRUKSI_ANALISIS = """Kamu adalah Asisten ListrikSmart yang menganalisis data penggunaan listrik rumah tangga di Indonesia.
Aturan:
- Tulis dalam bahasa Indonesia yang sederhana dan mudah dipahami.
- Gunakan HANYA angka yang ada pada bagian "DATA". Jangan mengarang angka biaya, kWh, persentase, atau tanggal.
- Semua biaya adalah estimasi dari model Machine Learning yang dilatih dengan data simulasi, bukan tagihan resmi PLN.
- Jika data hanya 1 atau 2 titik, jangan menyimpulkan tren. Katakan bahwa data masih sedikit.
- Jangan mengklaim sebab-akibat yang tidak ada pada data. Angka "jam-perangkat" hanyalah jumlah unit dikali jam pakai, bukan ukuran konsumsi listrik.
- Kamu boleh memakai pengetahuan umum tanpa menyebut angka watt (misalnya AC umumnya lebih boros daripada lampu LED).
- Gunakan persis format ini, dengan judul tebal:
**Ringkasan**
(2 kalimat)
**Temuan Utama**
(3 poin, tiap poin diawali tanda "-")
**Rekomendasi**
(3 poin, tiap poin diawali tanda "-")
- Maksimal sekitar 200 kata."""

TUGAS_ANALISIS = {
    'prediksi': 'Tugas: analisis hasil prediksi di bawah ini. Jelaskan arti kategorinya, perangkat yang berpotensi '
                'membuat biaya tinggi, dan rekomendasi penghematan yang paling berdampak.',
    'grafik': 'Tugas: analisis grafik riwayat estimasi biaya listrik di bawah ini. Jelaskan arah perubahannya '
              '(naik, turun, atau stabil), rentang nilainya, perbandingan antar kategori, dan beri saran.',
}

class GeminiError(Exception):
    """Kesalahan yang pesannya aman ditampilkan ke pengguna."""


def _rupiah(angka):
    return 'Rp' + f'{angka:,.0f}'.replace(',', '.')


def _tarif(angka):
    teks = f'{angka:,.2f}'
    return 'Rp' + teks.replace(',', '#').replace('.', ',').replace('#', '.')


def susun_data_prediksi(p):
    """Mengubah satu baris RiwayatPrediksi menjadi teks konteks untuk AI."""
    if p is None:
        return 'DATA PREDIKSI: pengguna belum melakukan prediksi.'

    def beban(jumlah, jam):
        return f'{jumlah} unit x {jam:g} jam/hari = {jumlah * jam:g} jam-perangkat/hari'

    return (
        'DATA PREDIKSI (hasil model Machine Learning):\n'
        f'- Estimasi biaya listrik per bulan: {_rupiah(p.hasil_regresi)}\n'
        f'- Kategori biaya: {p.hasil_klasifikasi}\n'
        f'- Jumlah penghuni: {p.jumlah_penghuni}\n'
        f'- Daya listrik: {p.daya_listrik} VA\n'
        f'- Tarif: {_tarif(p.tarif_listrik)} per kWh\n'
        f'- Kipas: {beban(p.jumlah_kipas, p.jam_kipas)}\n'
        f'- AC: {beban(p.jumlah_ac, p.jam_ac)}\n'
        f'- TV: {beban(p.jumlah_tv, p.jam_tv)}\n'
        f'- Lampu: {beban(p.jumlah_lampu, p.jam_lampu)}\n'
        f'- Kulkas: {p.jumlah_kulkas} unit (menyala sepanjang hari)\n'
    )


def _panggil_gemini(instruksi, isi):
    """Satu-satunya tempat yang memanggil Gemini. Galat diubah menjadi pesan ramah."""
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        raise GeminiError('Asisten AI belum diaktifkan: GEMINI_API_KEY belum diisi pada file .env.')

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise GeminiError('Paket google-genai belum terpasang. Jalankan: pip install google-genai')

    model = os.environ.get('GEMINI_MODEL', '').strip() or MODEL_DEFAULT

    try:
        client = genai.Client(api_key=api_key)
        respons = client.models.generate_content(
            model=model,
            contents=isi,
            config=types.GenerateContentConfig(system_instruction=instruksi, temperature=0.4),
        )
        teks = (respons.text or '').strip()
    except Exception as e:  # noqa: BLE001 - semua galat API diubah menjadi pesan ramah
        logger.exception('Gagal memanggil Gemini API')
        kode = getattr(e, 'code', None)
        if kode == 429:
            raise GeminiError('Batas penggunaan API Gemini sedang tercapai. Coba lagi beberapa saat lagi.')
        if kode in (400, 401, 403):
            raise GeminiError('API Key Gemini ditolak atau tidak valid. Periksa nilai GEMINI_API_KEY pada file .env.')
        if kode == 404:
            raise GeminiError('Model Gemini tidak ditemukan. Periksa nilai GEMINI_MODEL pada file .env.')
        raise GeminiError('Asisten AI sedang tidak dapat dihubungi. Silakan coba lagi nanti.')

    if not teks:
        raise GeminiError('Asisten AI tidak memberikan jawaban. Coba lagi dengan kalimat atau data yang berbeda.')
    return teks


def tanya_gemini(pertanyaan, prediksi=None, riwayat_chat=None):
    """Chatbot bebas (halaman Asisten AI)."""
    percakapan = ''
    for item in (riwayat_chat or []):
        siapa = 'Pengguna' if item['role'] == 'user' else 'Asisten'
        percakapan += f'{siapa}: {item["text"]}\n'
    isi = (percakapan + '\n' if percakapan else '') + f'Pertanyaan pengguna: {pertanyaan}'
    return _panggil_gemini(INSTRUKSI_SISTEM + '\n\n' + susun_data_prediksi(prediksi), isi)


def analisis_gemini(jenis, konteks):
    """Analisis otomatis lewat tombol (hasil prediksi atau grafik)."""
    return _panggil_gemini(INSTRUKSI_ANALISIS, TUGAS_ANALISIS[jenis] + '\n\n' + konteks)