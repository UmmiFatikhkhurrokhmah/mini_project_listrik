
from django.db import models


class RiwayatPrediksi(models.Model):
    tanggal_prediksi = models.DateTimeField(auto_now_add=True)

    # Kolom dataset lama (dipertahankan untuk riwayat sebelumnya)
    jumlah_penghuni = models.IntegerField(null=True, blank=True)
    jumlah_kipas = models.IntegerField(null=True, blank=True)
    jumlah_kulkas = models.IntegerField(null=True, blank=True)
    jumlah_ac = models.IntegerField(null=True, blank=True)
    jumlah_tv = models.IntegerField(null=True, blank=True)
    jumlah_lampu = models.IntegerField(null=True, blank=True)

    jam_kipas = models.FloatField(null=True, blank=True)
    jam_ac = models.FloatField(null=True, blank=True)
    jam_tv = models.FloatField(null=True, blank=True)
    jam_lampu = models.FloatField(null=True, blank=True)

    daya_listrik = models.IntegerField(null=True, blank=True)
    tarif_listrik = models.FloatField(null=True, blank=True)

    # Kolom dataset baru
    fan = models.IntegerField(null=True, blank=True)
    refrigerator = models.IntegerField(null=True, blank=True)
    air_conditioner = models.IntegerField(null=True, blank=True)
    television = models.IntegerField(null=True, blank=True)
    monitor = models.IntegerField(null=True, blank=True)
    motor_pump = models.IntegerField(null=True, blank=True)

    month = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=200, null=True, blank=True)

    monthly_hours = models.FloatField(null=True, blank=True)
    tariff_rate = models.FloatField(null=True, blank=True)

    # Hasil prediksi
    hasil_regresi = models.FloatField()
    hasil_klasifikasi = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.tanggal_prediksi} - {self.hasil_klasifikasi}"
