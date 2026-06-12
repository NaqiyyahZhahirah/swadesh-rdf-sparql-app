from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

FUSEKI_URL = "http://localhost:3030/swadesh/query"
PREFIX = "http://www.semanticweb.org/ontologies/swadesh#"

LANGUAGE_MAP = {
    "id": "Bahasa Indonesia",
    "su": "Bahasa Sunda",
    "mel": "Bahasa Melayu"
}


def format_sparql_results(results):
    """Menyederhanakan format JSON dari Fuseki menjadi list of dict."""
    formatted = []
    for row in results['results']['bindings']:
        item = {var: row[var]['value'] for var in results['head']['vars'] if var in row}
        formatted.append(item)
    return formatted


def sparql_query(query: str):
    """Mengirim query SPARQL ke Fuseki dan mengembalikan hasil yang sudah diformat."""
    try:
        response = requests.post(
            FUSEKI_URL,
            data={'query': query},
            headers={'Accept': 'application/sparql-results+json'},
            timeout=10
        )
        response.raise_for_status()
        return format_sparql_results(response.json()), None
    except requests.exceptions.ConnectionError:
        return None, "Tidak dapat terhubung ke Fuseki. Pastikan Apache Jena Fuseki sedang berjalan."
    except requests.exceptions.Timeout:
        return None, "Request ke Fuseki timeout."
    except Exception as e:
        return None, str(e)


def sanitize_keyword(keyword: str) -> str:
    """
    Membersihkan keyword untuk mencegah SPARQL Injection.
    Menghapus karakter yang bisa merusak SPARQL regex literal.
    """
    # Escape karakter spesial regex SPARQL: \ . * + ? | { } [ ] ( ) ^ $
    return re.sub(r'([\\.\*\+\?\|\{\}\[\]\(\)\^\$"])', r'\\\1', keyword)


# ---------------------------------------------------------------------------
# Route: GET /get-data
# Mengambil seluruh data kosakata (Indonesia, Sunda, Melayu) - max 200 baris
# ---------------------------------------------------------------------------
@app.route('/get-data', methods=['GET'])
def get_data():
    query = """
    PREFIX : <http://www.semanticweb.org/ontologies/swadesh#>
    SELECT ?konsep ?bahasaIndo ?bahasaSunda ?bahasaMelayu
    WHERE {
      ?wordId  :represents ?concept ; :belongsToLanguage :id  ; :wordValue ?bahasaIndo .
      ?wordSu  :represents ?concept ; :belongsToLanguage :su  ; :wordValue ?bahasaSunda .
      ?wordMel :represents ?concept ; :belongsToLanguage :mel ; :wordValue ?bahasaMelayu .
      ?concept :conceptName ?konsep .
    }
    ORDER BY ?konsep
    LIMIT 200
    """
    data, error = sparql_query(query)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(data)


# ---------------------------------------------------------------------------
# Route: GET /search?keyword=<kata>
# Mencari kata di semua bahasa (case-insensitive)
# ---------------------------------------------------------------------------
@app.route('/search', methods=['GET'])
def search_word():
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"error": "Parameter 'keyword' tidak boleh kosong."}), 400

    safe_keyword = sanitize_keyword(keyword)

    query = f"""
    PREFIX : <http://www.semanticweb.org/ontologies/swadesh#>
    SELECT ?konsep ?bahasaIndo ?bahasaSunda ?bahasaMelayu
    WHERE {{
      ?wordId  :represents ?concept ; :belongsToLanguage :id  ; :wordValue ?bahasaIndo .
      ?wordSu  :represents ?concept ; :belongsToLanguage :su  ; :wordValue ?bahasaSunda .
      ?wordMel :represents ?concept ; :belongsToLanguage :mel ; :wordValue ?bahasaMelayu .
      ?concept :conceptName ?konsep .
      FILTER (
        regex(?bahasaIndo,  "{safe_keyword}", "i") ||
        regex(?bahasaSunda, "{safe_keyword}", "i") ||
        regex(?bahasaMelayu,"{safe_keyword}", "i") ||
        regex(?konsep,      "{safe_keyword}", "i")
      )
    }}
    ORDER BY ?konsep
    """
    data, error = sparql_query(query)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(data)


# ---------------------------------------------------------------------------
# Route: GET /filter?lang=<kode_bahasa>
# Filter kosakata berdasarkan bahasa (id / su / mel)
# ---------------------------------------------------------------------------
@app.route('/filter', methods=['GET'])
def filter_by_language():
    lang = request.args.get('lang', '').strip().lower()
    if lang not in LANGUAGE_MAP:
        return jsonify({
            "error": f"Kode bahasa tidak valid. Gunakan salah satu: {', '.join(LANGUAGE_MAP.keys())}"
        }), 400

    query = f"""
    PREFIX : <http://www.semanticweb.org/ontologies/swadesh#>
    SELECT ?konsep ?kata
    WHERE {{
      ?word :represents ?concept ;
            :belongsToLanguage :{lang} ;
            :wordValue ?kata .
      ?concept :conceptName ?konsep .
    }}
    ORDER BY ?konsep
    """
    data, error = sparql_query(query)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({
        "bahasa": LANGUAGE_MAP[lang],
        "kode": lang,
        "jumlah": len(data),
        "data": data
    })


# ---------------------------------------------------------------------------
# Route: GET /graph-data
# Mengembalikan data dalam format nodes & edges untuk Cytoscape.js
# ---------------------------------------------------------------------------
@app.route('/graph-data', methods=['GET'])
def get_graph_data():
    # Opsional: filter per konsep tertentu via query param ?concept=HOW
    concept_filter = request.args.get('concept', '').strip().upper()

    concept_clause = f'FILTER(?konsep = "{concept_filter}")' if concept_filter else ""

    query = f"""
    PREFIX : <http://www.semanticweb.org/ontologies/swadesh#>
    SELECT ?konsep ?bahasaIndo ?bahasaSunda ?bahasaMelayu
    WHERE {{
      ?wordId  :represents ?concept ; :belongsToLanguage :id  ; :wordValue ?bahasaIndo .
      ?wordSu  :represents ?concept ; :belongsToLanguage :su  ; :wordValue ?bahasaSunda .
      ?wordMel :represents ?concept ; :belongsToLanguage :mel ; :wordValue ?bahasaMelayu .
      ?concept :conceptName ?konsep .
      {concept_clause}
    }}
    LIMIT 50
    """
    data, error = sparql_query(query)
    if error:
        return jsonify({"error": error}), 500

    nodes = []
    edges = []
    added_nodes = set()

    for row in data:
        konsep = row.get('konsep', '')
        if not konsep:
            continue

        # Node: Concept
        if konsep not in added_nodes:
            nodes.append({"data": {"id": konsep, "label": konsep, "type": "concept"}})
            added_nodes.add(konsep)

        # Node & Edge: tiap kata ke konsepnya
        lang_fields = {
            "id":  ("bahasaIndo",  "ID"),
            "su":  ("bahasaSunda", "SU"),
            "mel": ("bahasaMelayu","MEL"),
        }
        for lang_code, (field, flag) in lang_fields.items():
            kata = row.get(field, '')
            if not kata:
                continue
            node_id = f"{lang_code}:{kata}"
            if node_id not in added_nodes:
                nodes.append({
                    "data": {
                        "id": node_id,
                        "label": f"{flag} {kata}",
                        "type": "word",
                        "language": lang_code,
                        "languageName": LANGUAGE_MAP[lang_code]
                    }
                })
                added_nodes.add(node_id)
            edges.append({
                "data": {
                    "source": node_id,
                    "target": konsep,
                    "label": "represents"
                }
            })

    return jsonify({"nodes": nodes, "edges": edges})


# ---------------------------------------------------------------------------
# Route: GET /concepts
# Mengambil daftar semua konsep yang tersedia
# ---------------------------------------------------------------------------
@app.route('/concepts', methods=['GET'])
def get_concepts():
    query = """
    PREFIX : <http://www.semanticweb.org/ontologies/swadesh#>
    SELECT DISTINCT ?konsep
    WHERE {
      ?concept a :Concept ; :conceptName ?konsep .
    }
    ORDER BY ?konsep
    """
    data, error = sparql_query(query)
    if error:
        return jsonify({"error": error}), 500
    return jsonify([row['konsep'] for row in data])


# ---------------------------------------------------------------------------
# Route: GET /languages
# Mengembalikan daftar bahasa yang didukung
# ---------------------------------------------------------------------------
@app.route('/languages', methods=['GET'])
def get_languages():
    return jsonify([
        {"kode": k, "nama": v} for k, v in LANGUAGE_MAP.items()
    ])


# ---------------------------------------------------------------------------
# Route: GET /health
# Health check — untuk memastikan backend & koneksi Fuseki berjalan
# ---------------------------------------------------------------------------
@app.route('/health', methods=['GET'])
def health_check():
    try:
        resp = requests.get(
            "http://localhost:3030/$/ping",
            timeout=5
        )
        fuseki_ok = resp.status_code == 200
    except Exception:
        fuseki_ok = False

    return jsonify({
        "backend": "ok",
        "fuseki": "ok" if fuseki_ok else "tidak terhubung"
    }), 200 if fuseki_ok else 503


if __name__ == '__main__':
    app.run(debug=True, port=5000)