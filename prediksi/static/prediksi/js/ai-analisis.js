// Tombol Analisis AI. Pemanggilan Gemini dilakukan oleh backend Django (tanpa API Key di browser).
(function () {
    function esc(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    function inline(s) { return s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>'); }

    // Teks AI menjadi HTML aman: paragraf, daftar, dan huruf tebal
    function format(teks) {
        var html = '', dalamList = false;
        esc(teks).split('\n').forEach(function (baris) {
            var t = baris.trim();
            var li = /^[*-]\s+(.*)$/.exec(t);
            if (li) {
                if (!dalamList) { html += '<ul>'; dalamList = true; }
                html += '<li>' + inline(li[1]) + '</li>';
            } else {
                if (dalamList) { html += '</ul>'; dalamList = false; }
                if (t) { html += '<p>' + inline(t) + '</p>'; }
            }
        });
        if (dalamList) { html += '</ul>'; }
        return html;
    }

    document.querySelectorAll('.ai-panel').forEach(function (panel) {
        var tombol = panel.querySelector('.ai-btn');
        var ulang = panel.querySelector('.ai-ulang');
        var hasil = panel.querySelector('.ai-hasil');
        var footer = panel.querySelector('.ai-footer');
        var token = panel.querySelector('[name=csrfmiddlewaretoken]').value;
        var sibuk = false;

        async function jalankan(minta_ulang) {
            if (sibuk) { return; }
            sibuk = true;
            tombol.disabled = true;
            ulang.disabled = true;
            footer.hidden = true;
            hasil.hidden = false;
            hasil.className = 'ai-hasil ai-loading';
            hasil.textContent = 'AI sedang menganalisis data...';

            try {
                var res = await fetch(panel.dataset.url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
                    body: JSON.stringify({
                        jenis: panel.dataset.jenis,
                        id: panel.dataset.id,
                        lingkup: panel.dataset.lingkup,
                        ulang: !!minta_ulang
                    })
                });
                var data = await res.json().catch(function () { return {}; });
                if (!res.ok || data.error) {
                    hasil.className = 'ai-hasil ai-error';
                    hasil.textContent = data.error || 'Terjadi kesalahan. Silakan coba lagi.';
                    tombol.hidden = false;
                } else {
                    hasil.className = 'ai-hasil';
                    hasil.innerHTML = format(data.jawaban);
                    tombol.hidden = true;
                    footer.hidden = false;
                }
            } catch (e) {
                hasil.className = 'ai-hasil ai-error';
                hasil.textContent = 'Tidak dapat terhubung ke server. Periksa koneksi lalu coba lagi.';
                tombol.hidden = false;
            }
            tombol.disabled = false;
            ulang.disabled = false;
            sibuk = false;
        }

        tombol.addEventListener('click', function () { jalankan(false); });
        ulang.addEventListener('click', function () { jalankan(true); });
    });
})();