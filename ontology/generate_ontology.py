import csv
import os

# Nama file sesuai dokumenmu
csv_file_path = "../data/Dataset_Swadesh.csv"
owl_file_path = "swadesh_ontology.owl"
ttl_file_path = "swadesh_data.ttl"

if not os.path.exists(csv_file_path):
    print(f"Error: File '{csv_file_path}' tidak ditemukan!")
    exit()

# 1. STRUKTUR ONTOLOGI (Disimpan ke file .owl)
# Menggunakan sintaks Turtle (.ttl) namun dengan ekstensi .owl karena isinya murni skema kelas dan properti
ontology_schema = """@prefix : <http://www.semanticweb.org/ontologies/swadesh#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://www.semanticweb.org/ontologies/swadesh> rdf:type owl:Ontology .

# =================================================================
# Classes (Kelas)
# =================================================================
:Language rdf:type owl:Class .
:Concept rdf:type owl:Class .
:Word rdf:type owl:Class .

# =================================================================
# Object Properties (Properti Objek)
# =================================================================
:belongsToLanguage rdf:type owl:ObjectProperty ;
                   rdfs:domain :Word ;
                   rdfs:range :Language .

:represents rdf:type owl:ObjectProperty ;
            rdfs:domain :Word ;
            rdfs:range :Concept .

# =================================================================
# Data Properties (Properti Data)
# =================================================================
:wordValue rdf:type owl:DatatypeProperty ;
           rdfs:domain :Word ;
           rdfs:range xsd:string .

:conceptName rdf:type owl:DatatypeProperty ;
             rdfs:domain :Concept ;
             rdfs:range xsd:string .
"""

# 2. HEADER UNTUK FILE DATA (Disimpan ke file .ttl)
data_header = """@prefix : <http://www.semanticweb.org/ontologies/swadesh#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# =================================================================
# Individuals: Languages (Data Bahasa Tetap)
# =================================================================
:id rdf:type :Language , owl:NamedIndividual ; rdfs:label "Indonesian" .
:su rdf:type :Language , owl:NamedIndividual ; rdfs:label "Sundanese" .
:mel rdf:type :Language , owl:NamedIndividual ; rdfs:label "Malay" .

# =================================================================
# Individuals: Concepts & Words (Generated otomatis dari CSV)
# =================================================================
"""

print("Memproses pemisahan ontologi (.owl) dan data instans (.ttl)...")

try:
    concepts_seen = set()
    concept_triples = []
    word_triples = []
    
    with open(csv_file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        
        word_counter = 1
        header_found = False
        idx_concept, idx_name, idx_lang, idx_word = 0, 0, 0, 0
        
        for row in reader:
            row = [col.strip() for col in row]
            
            # Deteksi Header CSV
            if not header_found:
                if 'concept_id' in row and 'word' in row:
                    header_found = True
                    idx_concept = row.index('concept_id')
                    idx_name = row.index('concept_name')
                    idx_lang = row.index('language_code')
                    idx_word = row.index('word')
                continue
            
            if len(row) <= max(idx_concept, idx_name, idx_lang, idx_word):
                continue
                
            concept_id = row[idx_concept]
            concept_name = row[idx_name]
            lang_code = row[idx_lang]
            word_value = row[idx_word]
            
            if not concept_id or not lang_code or not word_value:
                continue
            
            # Kelompokkan data Konsep unik
            if concept_id not in concepts_seen:
                concepts_seen.add(concept_id)
                concept_triples.append(f':{concept_id} rdf:type :Concept , owl:NamedIndividual ; :conceptName "{concept_name}" .\n')
            
            # Kelompokkan data Kata Swadesh
            word_triples.append(
                f':W{word_counter} rdf:type :Word , owl:NamedIndividual ; '
                f':wordValue "{word_value}" ; '
                f':represents :{concept_id} ; '
                f':belongsToLanguage :{lang_code} .\n'
            )
            word_counter += 1

    # FILE 1: Tulis Skema ke (.owl)
    with open(owl_file_path, mode='w', encoding='utf-8') as owl_file:
        owl_file.write(ontology_schema)
        
    # FILE 2: Tulis Data Individu ke (.ttl)
    with open(ttl_file_path, mode='w', encoding='utf-8') as ttl_file:
        ttl_file.write(data_header)
        ttl_file.write("\n# --- Daftar Konsep ---\n")
        ttl_file.writelines(concept_triples)
        ttl_file.write("\n# --- Daftar Kata Swadesh ---\n")
        ttl_file.writelines(word_triples)

    print("\n[SUKSES BERHASIL]")
    print(f"1. File Skema dibuat -> '{owl_file_path}'")
    print(f"2. File Data dibuat   -> '{ttl_file_path}' (Berisi {word_counter - 1} kosakata)")

except Exception as e:
    print(f"Gagal memproses pemisahan file: {e}")