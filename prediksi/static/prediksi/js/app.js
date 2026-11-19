// Membuka dan menutup sidebar pada layar kecil (HP)
(function () {
    var body = document.body;
    var tombol = document.getElementById('menuToggle');
    var overlay = document.getElementById('overlay');

    function tutup() { body.classList.remove('sidebar-open'); }

    if (tombol) {
        tombol.addEventListener('click', function () {
            body.classList.toggle('sidebar-open');
        });
    }
    if (overlay) { overlay.addEventListener('click', tutup); }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { tutup(); }
    });
})();
