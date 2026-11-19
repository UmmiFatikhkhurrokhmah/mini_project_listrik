from django.contrib import admin
from .models import RiwayatPrediksi


@admin.register(RiwayatPrediksi)
class RiwayatPrediksiAdmin(admin.ModelAdmin):
    list_display = ('id', 'tanggal_prediksi', 'jumlah_penghuni', 'daya_listrik',
                    'hasil_regresi', 'hasil_klasifikasi')
    list_filter = ('hasil_klasifikasi',)
