"""Menyusun teks data grafik dari database untuk dianalisis AI."""

from django.db.models import Avg, Count
from django.utils import timezone

from .gemini_service import _rupiah
from .models import RiwayatPrediksi


def konteks_grafik(batas):
    """Data grafik riwayat (maksimal `batas` prediksi terbaru). None jika belum ada data."""
    semua = RiwayatPrediksi.objects.all()
    total = semua.count()
    if not total:
        return None

    data = list(semua.order_by('-tanggal_prediksi')[:batas])[::-1]  # urut dari lama ke baru
    nilai = [r.hasil_regresi for r in data]
    pertama, terakhir = nilai[0], nilai[-1]

    baris = '\n'.join(
        f'{i}. {timezone.localtime(r.tanggal_prediksi).strftime("%d/%m %H:%M")}: '
        f'{_rupiah(r.hasil_regresi)} ({r.hasil_klasifikasi})'
        for i, r in enumerate(data, 1)
    )

    jumlah_kategori = {}
    for r in data:
        jumlah_kategori[r.hasil_klasifikasi] = jumlah_kategori.get(r.hasil_klasifikasi, 0) + 1
    teks_kategori = ', '.join(f'{k}: {v}' for k, v in sorted(jumlah_kategori.items()))

    teks = (
        'DATA GRAFIK RIWAYAT ESTIMASI BIAYA LISTRIK (urut dari terlama ke terbaru):\n'
        f'- Total prediksi tersimpan: {total}\n'
        f'- Jumlah titik pada grafik: {len(data)}\n'
        f'- Estimasi terendah: {_rupiah(min(nilai))}\n'
        f'- Estimasi tertinggi: {_rupiah(max(nilai))}\n'
        f'- Rata-rata estimasi pada grafik: {_rupiah(sum(nilai) / len(nilai))}\n'
        f'- Titik pertama: {_rupiah(pertama)}, titik terakhir: {_rupiah(terakhir)}\n'
        f'- Selisih titik terakhir terhadap titik pertama: {_rupiah(abs(terakhir - pertama))} '
        f'({"naik" if terakhir > pertama else "turun" if terakhir < pertama else "tetap"})\n'
        f'- Jumlah per kategori pada grafik: {teks_kategori}\n'
        f'Daftar titik:\n{baris}\n'
    )

    if total > len(data):
        rata = semua.values('hasil_klasifikasi').annotate(n=Count('id'), r=Avg('hasil_regresi'))
        teks += '\nRingkasan seluruh data tersimpan per kategori:\n'
        teks += '\n'.join(
            f'- {b["hasil_klasifikasi"]}: {b["n"]} prediksi, rata-rata {_rupiah(b["r"] or 0)}'
            for b in sorted(rata, key=lambda x: x['hasil_klasifikasi'])
        ) + '\n'
    return teks