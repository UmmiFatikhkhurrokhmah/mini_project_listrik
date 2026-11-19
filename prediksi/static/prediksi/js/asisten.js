// Chatbot Asisten AI. Pemanggilan Gemini dilakukan oleh backend Django (tanpa API Key di browser).
(function () {
    var chat = document.getElementById('chatBox');
    if (!chat) { return; }

    var form = document.getElementById('chatForm');
    var input = document.getElementById('chatInput');
    var tombol = document.getElementById('chatKirim');
    var pilih = document.getElementById('pilihPrediksi');
    var token = form.querySelector('[name=csrfmiddlewaretoken]').value;
    var url = chat.dataset.url;
    var prediksiId = chat.dataset.prediksi || '';
    var riwayat = [];
    var sibuk = false;

    if (pilih) {
        pilih.addEventListener('change', function () {
            window.location.href = window.location.pathname + '?id=' + encodeURIComponent(pilih.value);
        });
    }

    function esc(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    function inline(s) { return s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>'); }

    // Mengubah teks AI menjadi HTML aman (paragraf, daftar, huruf tebal)
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

    function tambah(kelas, teks, html) {
        var d = document.createElement('div');
        d.className = 'bubble ' + kelas;
        if (html) { d.innerHTML = html; } else { d.textContent = teks; }
        chat.appendChild(d);
        chat.scrollTop = chat.scrollHeight;
        return d;
    }

    function atur(aktif) {
        sibuk = !aktif;
        tombol.disabled = !aktif;
        input.disabled = !aktif;
        if (aktif) { input.focus(); }
    }

    async function kirim(pertanyaan) {
        if (sibuk || !pertanyaan) { return; }
        tambah('bubble-user', pertanyaan);
        input.value = '';
        input.style.height = 'auto';
        atur(false);
        var tunggu = tambah('bubble-ai bubble-loading', 'Asisten sedang menulis jawaban...');

        try {
            var res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
                body: JSON.stringify({ pertanyaan: pertanyaan, prediksi_id: prediksiId, riwayat: riwayat.slice(-6) })
            });
            var data = await res.json().catch(function () { return {}; });
            tunggu.remove();
            if (!res.ok || data.error) {
                tambah('bubble-error', data.error || 'Terjadi kesalahan. Silakan coba lagi.');
            } else {
                tambah('bubble-ai', '', format(data.jawaban));
                riwayat.push({ role: 'user', text: pertanyaan });
                riwayat.push({ role: 'assistant', text: data.jawaban });
            }
        } catch (e) {
            tunggu.remove();
            tambah('bubble-error', 'Tidak dapat terhubung ke server. Periksa koneksi lalu coba lagi.');
        }
        atur(true);
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        kirim(input.value.trim());
    });

    // Enter = kirim, Shift+Enter = baris baru
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            form.requestSubmit();
        }
    });
    input.addEventListener('input', function () {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 140) + 'px';
    });

    document.querySelectorAll('.chip').forEach(function (c) {
        c.addEventListener('click', function () { kirim(c.dataset.q); });
    });
})();
