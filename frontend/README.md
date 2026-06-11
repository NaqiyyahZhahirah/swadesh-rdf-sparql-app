# Swadesh RDF Explorer — Frontend

Quick static frontend to explore the Swadesh backend API.

How to run

1. Jalankan backend Flask di `http://localhost:5000`.
2. Buka terminal di folder `frontend`.
3. Jalankan server frontend:

```bash
python serve_frontend.py
```

4. Browser akan otomatis membuka `http://127.0.0.1:8000/index.html`.

Jika ingin jangan pakai server otomatis, Anda juga bisa menggunakan:

```bash
python -m http.server 8000
```

Notes

- Uses Cytoscape.js (CDN) for graph rendering and DataTables for the dashboard table.
- Backend CORS sudah di-handle oleh Flask app, jadi frontend dapat memanggil API `http://localhost:5000`.
- Jika backend berjalan di host/port lain, ubah `API` di `app.js`.
