from sentence_transformers import SentenceTransformer
from fragmentar import fragmentos_procesados
import chromadb

#cargamos el modelo de embeddings
modelo_embeddings=SentenceTransformer("all-mpnet-base-v2")

#inicializamos ChromaDB
chroma_client= chromadb.PersistentClient("chroma_db")
collection= chroma_client.get_or_create_collection(name="chatbot_rrhh")

#procesamos y almacenamos los fragmentos en bd
for fragmento in fragmentos_procesados:
    embedding= modelo_embeddings.encode(fragmento["fragmento"]).tolist()
    collection.add(
        ids=[fragmento["id_fragmento"]],
        embeddings=[embedding],
        metadatas=[{"titulo": fragmento["titulo"], "url": fragmento["url"]}],
        documents=[fragmento["fragmento"]]
    )
    
#verificamos cuánto se almacenó de los docs
num_docs=collection.count()
num_docs

    