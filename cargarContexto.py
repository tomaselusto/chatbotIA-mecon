import json
import datetime
from sentence_transformers import SentenceTransformer
import chromadb

# Inicializar embeddings y base vectorial
modelo_embeddings = SentenceTransformer("all-mpnet-base-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="chatbot_contexto")

# Función de chunking con solapamiento
def dividir_texto_overlap(texto, max_length=512, overlap=100):
    palabras = texto.split()
    fragmentos = []
    i = 0
    while i < len(palabras):
        chunk = palabras[i:i + max_length]
        fragmento = " ".join(chunk)
        fragmentos.append(fragmento)
        i += max_length - overlap
    return fragmentos

# Procesar y cargar el JSON
def cargar_contexto_desde_json(ruta="contexto.json"):
    with open(ruta, "r", encoding="utf-8") as file:
        data = json.load(file)

    total_fragmentos = 0
    timestamp = datetime.datetime.now().timestamp()

    for item in data:
        titulo = item.get("titulo", "Sin título")
        url = item.get("url", "")
        contenido = item.get("contenido", "")

        fragmentos = dividir_texto_overlap(contenido)

        for i, fragmento in enumerate(fragmentos):
            fragment_id = f"{titulo}_{i}_{timestamp}"
            embedding = modelo_embeddings.encode(fragmento).tolist()
            collection.add(
                ids=[fragment_id],
                embeddings=[embedding],
                documents=[fragmento],
                metadatas=[{"titulo": titulo, "url": url}]
            )
            total_fragmentos += 1

    print(f"✅ Se indexaron {total_fragmentos} fragmentos en ChromaDB.")
    return total_fragmentos
