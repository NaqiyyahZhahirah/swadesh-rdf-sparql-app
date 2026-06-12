# Swadesh RDF Explorer

> Jelajahi kosakata lintas budaya dengan teknologi Semantic Web — Bahasa Indonesia, Sunda, dan Melayu dalam satu platform interaktif.

---

## Deskripsi

**Swadesh RDF Explorer** adalah aplikasi web berbasis *Semantic Web* yang mengeksplorasi **Daftar Swadesh** — sekumpulan kosakata dasar yang digunakan dalam linguistik komparatif — untuk tiga bahasa serumpun: **Bahasa Indonesia**, **Bahasa Sunda**, dan **Bahasa Melayu**.

Data kosakata dimodelkan menggunakan **ontologi OWL/RDF** dan disimpan di **Apache Jena Fuseki** sebagai *triplestore*. Backend Flask mengirimkan query **SPARQL** ke Fuseki untuk mengambil data secara semantik, lalu menyajikannya lewat API REST yang dikonsumsi oleh frontend web.

### Fitur Utama

| Fitur | Deskripsi |
|---|---|
| **Dashboard Kosakata** | Tabel interaktif seluruh data Swadesh (hingga 200 entri) dengan pencarian lokal dan pagination via DataTables |
| **Pencarian Semantik** | Cari kata di semua bahasa sekaligus (case-insensitive) atau filter per bahasa tertentu |
| **Knowledge Graph** | Visualisasi interaktif relasi konsep–kata menggunakan Cytoscape.js |
| **Multi-bahasa** | Mendukung Bahasa Indonesia (`id`), Bahasa Sunda (`su`), dan Bahasa Melayu (`mel`) |

---

## Struktur Proyek

```
swadesh-rdf-sparql-app/
├── backend/
│   └── app.py                  # Flask API (SPARQL endpoints)
├── data/
│   └── Dataset_Swadesh.csv     # Dataset kosakata Swadesh (sumber)
├── frontend/
│   ├── index.html              # Halaman utama aplikasi
│   ├── app.js                  # Logika frontend (fetch API, Cytoscape.js)
│   ├── styles.css              # Tampilan antarmuka
│   └── serve_frontend.py       # Server statis sederhana (port 8000)
└── ontology/
    ├── generate_ontology.py    # Script konversi CSV → RDF/TTL
    ├── swadesh_ontology.owl    # Skema ontologi (kelas & properti OWL)
    ├── swadesh_ontology.ttl    # Skema ontologi dalam format Turtle
    └── swadesh_data.ttl        # Data RDF hasil konversi (di-load ke Fuseki)
```

---

## Teknologi

- **Backend:** Python, Flask, Flask-CORS
- **Triplestore:** Apache Jena Fuseki
- **Query Language:** SPARQL
- **Ontologi:** OWL / RDF (Turtle format)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Visualisasi Graf:** [Cytoscape.js](https://js.cytoscape.org/)
- **Tabel Interaktif:** [DataTables](https://datatables.net/)

---

## Cara Menjalankan

### Prasyarat

- Python 3.x
- `pip install flask flask-cors requests`
- [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) (sudah terinstal dan bisa dijalankan)

---

### Langkah 1 — Siapkan Triplestore (Apache Jena Fuseki)

1. Jalankan Fuseki:
   ```bash
   ./fuseki-server --update --mem /swadesh
   ```
   Fuseki akan berjalan di `http://localhost:3030`.

2. Buka antarmuka Fuseki di browser: `http://localhost:3030`

3. Buat dataset baru bernama **`swadesh`** (jika belum ada).

4. Upload file data RDF ke dataset tersebut:
   - Pergi ke tab **Upload data**
   - Cari folder `ontology`
   - Pilih file `swadesh_data.ttl` dan `swadesh_ontology.ttl` 
   - Klik **Upload**

---

### Langkah 2 — Jalankan Backend Flask

```bash
cd backend
python app.py
```

Backend akan berjalan di `http://localhost:5000`.

---

### Langkah 3 — Jalankan Frontend

```bash
cd frontend
python serve_frontend.py
```

Browser akan otomatis membuka `http://127.0.0.1:8000/index.html`.

Alternatif manual:
```bash
cd frontend
python -m http.server 8000
```
Lalu buka `http://127.0.0.1:8000/index.html` di browser.

---

### Health Check

Untuk memastikan backend dan koneksi ke Fuseki berjalan dengan benar:

```
GET http://localhost:5000/health
```

Response sukses:
```json
{
  "backend": "ok",
  "fuseki": "ok"
}
```

---

## API Endpoints

| Method | Endpoint | Deskripsi |
|---|---|---|
| `GET` | `/get-data` | Ambil seluruh kosakata (maks. 200) |
| `GET` | `/search?keyword=<kata>` | Cari kata di semua bahasa |
| `GET` | `/filter?lang=<kode>` | Filter per bahasa (`id` / `su` / `mel`) |
| `GET` | `/graph-data` | Data node & edge untuk Knowledge Graph |
| `GET` | `/concepts` | Daftar semua konsep yang tersedia |
| `GET` | `/languages` | Daftar bahasa yang didukung |
| `GET` | `/health` | Health check backend & Fuseki |

---

## Anggota Proyek
 
Proyek Tugas Akhir Mata Kuliah **Semantic Web** — Universitas Padjadjaran
 
| NPM | Nama |
|---|---|
| 140810230025 | Kresna Bayu Wicaksono |
| 140810230039 | Naqiyyah Zhahirah |
| 140810230063 | Shofy Aliya |

---

## Repository

[https://github.com/NaqiyyahZhahirah/swadesh-rdf-sparql-app](https://github.com/NaqiyyahZhahirah/swadesh-rdf-sparql-app)