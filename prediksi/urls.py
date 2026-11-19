from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('prediksi/', views.prediksi, name='prediksi'),
    path('riwayat/', views.riwayat, name='riwayat'),
    path('riwayat/<int:pk>/', views.riwayat_detail, name='riwayat_detail'),
    path('visualisasi/', views.visualisasi, name='visualisasi'),
    path('asisten/', views.asisten, name='asisten'),
    path('asisten/kirim/', views.asisten_kirim, name='asisten_kirim'),
    path('ai/analisis/', views.ai_analisis, name='ai_analisis'),
    path('tentang/', views.tentang, name='tentang'),
]
