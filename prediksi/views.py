import hashlib
import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from .forms import PrediksiForm
from .analisis import konteks_grafik
from .gemini_service import GeminiError, analisis_gemini, susun_data_prediksi, tanya_gemini
from .models import RiwayatPrediksi

logger = logging.getLogger(__name__)

# Memuat model Machine Learning (tidak berubah dari versi sebelumnya)
BASE_DIR = Path(__file__).resolve().parent
folder_model = BASE_DIR / 'models_ml'

model_regresi = joblib.load(folder_model / 'model_regresi.pkl')
model_klasifikasi = joblib.load(folder_model / 'model_klasifikasi.pkl')
fitur = joblib.load(folder_model / 'fitur_model.pkl')

KATEGORI = ['HEMAT', 'NORMAL', 'TINGGI']

KETERANGAN = {
    'HEMAT': 'Pola penggunaan listrik rumahmu tergolong hemat. Pertahankan kebiasaan yang sudah baik.',
    'NORMAL': 'Pola penggunaan listrik rumahmu tergolong normal. Masih ada peluang menghemat dengan mengatur jam pakai perangkat.',
    'TINGGI': 'Pola penggunaan listrik rumahmu tergolong tinggi. Periksa perangkat dengan jam pakai terlama, terutama AC.',
}

SAPAAN_JAM = [(11, 'Selamat pagi'), (15, 'Selamat siang'), (18, 'Selamat sore'), (24, 'Selamat malam')]


def _sapaan():
    jam = timezone.localtime().hour
    for batas, teks in SAPAAN_JAM:
        if jam < batas:
            return teks
    return 'Selamat malam'


def _label_waktu(dt):
    return timezone.localtime(dt).strftime('%d/%m %H:%M')


# ---------------------------------------------------------------- Dashboard
def index(request):
    semua = RiwayatPrediksi.objects.all()
    total = semua.count()
    terbaru = list(semua.order_by('-tanggal_prediksi')[:5])
    terakhir = terbaru[0] if terbaru else None

    grafik = None
    rata_rata = None
    if total:
        sepuluh = list(semua.order_by('-tanggal_prediksi')[:10])[::-1]
        grafik = {
            'labels': [_label_waktu(r.tanggal_prediksi) for r in sepuluh],
            'values': [round(r.hasil_regresi) for r in sepuluh],
        }
        rata_rata = semua.aggregate(r=Avg('hasil_regresi'))['r']

    return render(request, 'prediksi/index.html', {
        'sapaan': _sapaan(),
        'total': total,
        'terakhir': terakhir,
        'terbaru': terbaru,
        'rata_rata': rata_rata,
        'grafik': grafik,
    })


# ------------------------------------------------------------ Prediksi biaya

def prediksi(request):
    hasil = None

    if request.method == 'POST':
        form = PrediksiForm(request.POST)

        if form.is_valid():
            c = form.cleaned_data

            # Menyesuaikan input dengan fitur dataset Kaggle
            data = {
                'Fan': c['fan'],
                'Refrigerator': c['refrigerator'],
                'AirConditioner': c['air_conditioner'],
                'Television': c['television'],
                'Monitor': c['monitor'],
                'MotorPump': 0,
                'Month': c['month'],
                'City': c['city'],
                'Company': c['company'],
                'MonthlyHours': c['monthly_hours'],
                'TariffRate': c['tariff_rate'],
            }

            try:
                data_input = pd.DataFrame([data], columns=fitur)

                hasil_regresi = float(
                    model_regresi.predict(data_input)[0]
                )

                hasil_klasifikasi = str(
                    model_klasifikasi.predict(data_input)[0]
                )

            except Exception:
                logger.exception('Prediksi gagal')
                messages.error(
                    request,
                    'Prediksi gagal diproses. Periksa kembali data yang dimasukkan.'
                )

            else:
                hasil = RiwayatPrediksi.objects.create(
                    fan=data['Fan'],
                    refrigerator=data['Refrigerator'],
                    air_conditioner=data['AirConditioner'],
                    television=data['Television'],
                    monitor=data['Monitor'],
                    motor_pump=data['MotorPump'],
                    month=data['Month'],
                    city=data['City'],
                    company=data['Company'],
                    monthly_hours=data['MonthlyHours'],
                    tariff_rate=data['TariffRate'],
                    hasil_regresi=hasil_regresi,
                    hasil_klasifikasi=hasil_klasifikasi,
                )

        else:
            messages.error(
                request,
                'Data belum valid. Periksa kolom yang ditandai di bawah.'
            )

    else:
        form = PrediksiForm()

    return render(request, 'prediksi/prediksi.html', {
        'form': form,
        'hasil': hasil,
        'keterangan': KETERANGAN.get(
            hasil.hasil_klasifikasi, ''
        ) if hasil else '',
    })



# ------------------------------------------------------------------ Riwayat
def riwayat(request):
    qs = RiwayatPrediksi.objects.all().order_by('-tanggal_prediksi')

    q = request.GET.get('q', '').strip()
    kategori = request.GET.get('kategori', '').strip().upper()
    dari_teks = request.GET.get('dari', '').strip()
    sampai_teks = request.GET.get('sampai', '').strip()

    if q:
        kondisi = Q(hasil_klasifikasi__icontains=q)
        if q.isdigit():
            kondisi |= Q(jumlah_penghuni=int(q)) | Q(daya_listrik=int(q))
        qs = qs.filter(kondisi)
    if kategori in KATEGORI:
        qs = qs.filter(hasil_klasifikasi=kategori)
    dari = parse_date(dari_teks) if dari_teks else None
    sampai = parse_date(sampai_teks) if sampai_teks else None
    if dari:
        qs = qs.filter(tanggal_prediksi__date__gte=dari)
    if sampai:
        qs = qs.filter(tanggal_prediksi__date__lte=sampai)

    halaman = Paginator(qs, 10).get_page(request.GET.get('page'))

    parameter = request.GET.copy()
    parameter.pop('page', None)

    return render(request, 'prediksi/riwayat.html', {
        'riwayat': halaman,
        'halaman': halaman,
        'nomor_awal': halaman.start_index() if halaman.paginator.count else 0,
        'jumlah_total': halaman.paginator.count,
        'q': q, 'kategori': kategori, 'dari': dari_teks, 'sampai': sampai_teks,
        'kategori_pilihan': KATEGORI,
        'qs_filter': parameter.urlencode(),
        'ada_filter': bool(q or kategori or dari_teks or sampai_teks),
    })


def riwayat_detail(request, pk):
    data = get_object_or_404(RiwayatPrediksi, pk=pk)
    return render(request, 'prediksi/riwayat_detail.html', {
        'd': data,
        'keterangan': KETERANGAN.get(data.hasil_klasifikasi, ''),
    })


# -------------------------------------------------------------- Visualisasi
def visualisasi(request):
    semua = RiwayatPrediksi.objects.all()
    total = semua.count()
    data = None
    ringkasan = []

    if total:
        per = {k: {'jumlah': 0, 'rata': 0} for k in KATEGORI}
        for baris in semua.values('hasil_klasifikasi').annotate(n=Count('id'), rata=Avg('hasil_regresi')):
            kunci = baris['hasil_klasifikasi']
            if kunci in per:
                per[kunci] = {'jumlah': baris['n'], 'rata': round(baris['rata'] or 0)}

        tiga_puluh = list(semua.order_by('-tanggal_prediksi')[:30])[::-1]
        data = {
            'kategori_label': KATEGORI,
            'kategori_jumlah': [per[k]['jumlah'] for k in KATEGORI],
            'kategori_rata': [per[k]['rata'] for k in KATEGORI],
            'waktu_label': [_label_waktu(r.tanggal_prediksi) for r in tiga_puluh],
            'waktu_nilai': [round(r.hasil_regresi) for r in tiga_puluh],
        }
        ringkasan = [{'nama': k, 'jumlah': per[k]['jumlah'], 'rata': per[k]['rata']} for k in KATEGORI]

    return render(request, 'prediksi/visualisasi.html', {
        'total': total, 'data': data, 'ringkasan': ringkasan,
    })


# -------------------------------------------------------------- Asisten AI
def asisten(request):
    pilihan = list(RiwayatPrediksi.objects.order_by('-tanggal_prediksi')[:10])
    dipilih = None
    pid = request.GET.get('id', '')
    if pid.isdigit():
        dipilih = RiwayatPrediksi.objects.filter(pk=int(pid)).first()
    if dipilih is None and pilihan:
        dipilih = pilihan[0]

    return render(request, 'prediksi/asisten.html', {
        'pilihan': pilihan,
        'dipilih': dipilih,
    })


@require_POST
def asisten_kirim(request):
    try:
        isi = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error': 'Permintaan tidak valid.'}, status=400)

    pertanyaan = str(isi.get('pertanyaan', '')).strip()
    if not pertanyaan:
        return JsonResponse({'error': 'Pertanyaan tidak boleh kosong.'}, status=400)
    if len(pertanyaan) > 1000:
        return JsonResponse({'error': 'Pertanyaan terlalu panjang (maksimal 1000 karakter).'}, status=400)

    prediksi_obj = None
    pid = str(isi.get('prediksi_id', '')).strip()
    if pid.isdigit():
        prediksi_obj = RiwayatPrediksi.objects.filter(pk=int(pid)).first()

    riwayat_chat = []
    for item in (isi.get('riwayat') or [])[-6:]:
        if isinstance(item, dict) and item.get('role') in ('user', 'assistant'):
            riwayat_chat.append({'role': item['role'], 'text': str(item.get('text', ''))[:1500]})

    try:
        jawaban = tanya_gemini(pertanyaan, prediksi_obj, riwayat_chat)
    except GeminiError as e:
        return JsonResponse({'error': str(e)}, status=502)

    return JsonResponse({'jawaban': jawaban})

@require_POST
def ai_analisis(request):
    """Analisis otomatis lewat tombol: hasil satu prediksi atau grafik riwayat."""
    try:
        isi = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error': 'Permintaan tidak valid.'}, status=400)

    jenis = isi.get('jenis')
    if jenis == 'prediksi':
        pid = str(isi.get('id', '')).strip()
        obj = RiwayatPrediksi.objects.filter(pk=int(pid)).first() if pid.isdigit() else None
        if obj is None:
            return JsonResponse({'error': 'Data prediksi tidak ditemukan.'}, status=404)
        konteks = susun_data_prediksi(obj)
    elif jenis == 'grafik':
        batas = 30 if isi.get('lingkup') == 'visualisasi' else 10
        konteks = konteks_grafik(batas)
        if konteks is None:
            return JsonResponse({'error': 'Belum ada data prediksi untuk dianalisis.'}, status=400)
    else:
        return JsonResponse({'error': 'Jenis analisis tidak dikenal.'}, status=400)

    # Data yang sama menghasilkan analisis yang sama; disimpan sementara agar hemat kuota API.
    kunci = 'ai-analisis:' + hashlib.sha256((jenis + konteks).encode('utf-8')).hexdigest()
    jawaban = None if isi.get('ulang') else cache.get(kunci)
    if jawaban is None:
        try:
            jawaban = analisis_gemini(jenis, konteks)
        except GeminiError as e:
            return JsonResponse({'error': str(e)}, status=502)
        cache.set(kunci, jawaban, 1800)

    return JsonResponse({'jawaban': jawaban})

# ------------------------------------------------------------------- Tentang
def tentang(request):
    return render(request, 'prediksi/tentang.html')
