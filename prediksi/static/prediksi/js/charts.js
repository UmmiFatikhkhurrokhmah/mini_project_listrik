// Grafik Chart.js. Data dibaca dari json_script Django (data asli dari PostgreSQL).
(function () {
    function baca(id) {
        var el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : null;
    }
    function rupiah(v) { return 'Rp ' + Number(v).toLocaleString('id-ID'); }

    if (typeof Chart === 'undefined') {
        var err = document.getElementById('chartError');
        if (err) { err.hidden = false; }
        return;
    }

    var BIRU = '#2878c8', HIJAU = '#15803d', KUNING = '#d97706', MERAH = '#b91c1c';
    var skalaRupiah = {
        y: { beginAtZero: true, ticks: { callback: function (v) { return rupiah(v); } } }
    };
    var tooltipRupiah = {
        callbacks: { label: function (c) { return ' ' + rupiah(c.parsed.y); } }
    };

    function garis(canvasId, labels, nilai) {
        var c = document.getElementById(canvasId);
        if (!c) { return; }
        new Chart(c, {
            type: 'line',
            data: { labels: labels, datasets: [{
                label: 'Estimasi biaya', data: nilai, borderColor: BIRU,
                backgroundColor: 'rgba(40,120,200,.15)', fill: true, tension: 0.3, pointRadius: 4
            }] },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: tooltipRupiah }, scales: skalaRupiah }
        });
    }

    // Dashboard
    var g = baca('data-grafik');
    if (g) { garis('grafikBiaya', g.labels, g.values); }

    // Halaman Visualisasi
    var v = baca('data-visualisasi');
    if (v) {
        garis('grafikWaktu', v.waktu_label, v.waktu_nilai);

        var warna = [HIJAU, KUNING, MERAH];
        var k = document.getElementById('grafikKategori');
        if (k) {
            new Chart(k, {
                type: 'doughnut',
                data: { labels: v.kategori_label, datasets: [{ data: v.kategori_jumlah, backgroundColor: warna }] },
                options: { responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } } }
            });
        }
        var r = document.getElementById('grafikRata');
        if (r) {
            new Chart(r, {
                type: 'bar',
                data: { labels: v.kategori_label, datasets: [{ label: 'Rata-rata biaya', data: v.kategori_rata, backgroundColor: warna }] },
                options: { responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false }, tooltip: tooltipRupiah }, scales: skalaRupiah }
            });
        }
    }
})();
