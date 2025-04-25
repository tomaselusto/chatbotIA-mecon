from sentence_transformers import SentenceTransformer
import chromadb
import ollama



# Función para inicializar solo cuando haga falta
def inicializar_embeddings():
    return SentenceTransformer("all-mpnet-base-v2")

def inicializar_chromadb():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="chatbot_contexto")
    return collection

modelo_embeddings = inicializar_embeddings()
collection = inicializar_chromadb()
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

# Las funciones usan los inicializadores arriba
def buscar_en_chromadb(consulta, top_k=5):
    modelo_embeddings = inicializar_embeddings()
    collection = inicializar_chromadb()
    
    embedding_consulta = modelo_embeddings.encode(consulta).tolist()
    resultados = collection.query(
        query_embeddings=[embedding_consulta],
        n_results=top_k
    )
    
    #para ver qué encuentra
    print(f"🧠 Resultados para: {consulta}")
    for doc in resultados["documents"][0]:
        print(f"🔹 {doc[:100]}...")

    fragmentos_encontrados = []
    for i in range(len(resultados["documents"][0])):
        fragmentos_encontrados.append({
            "fragmento": resultados["documents"][0][i],
            "titulo": resultados["metadatas"][0][i]["titulo"],
            "url": resultados["metadatas"][0][i]["url"]
        })
    return fragmentos_encontrados
def generar_respuesta(consulta):
    fragmentos = buscar_en_chromadb(consulta)

    if not fragmentos:
        return "No encontré información relevante sobre eso."

    contexto = "\n\n".join(["- {}".format(f["fragmento"]) for f in fragmentos])

    # 🔍 Debug
    print("------ CONTEXTO ENVIADO A OLLAMA ------")
    print(contexto)
    print("------ FIN CONTEXTO ------")

    prompt = f"""Respondé como un asistente del Ministerio de Economía.
Respondé solamente con la siguiente información. No inventes datos.

{contexto}

Pregunta del usuario: {consulta}

Si no hay información suficiente para responder, decí: "No tengo información sobre eso".
"""

    respuesta = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": prompt}]
    )
    return respuesta["message"]["content"]




#def generar_respuesta(consulta):
#    fragmentos = buscar_en_chromadb(consulta)
#    if not fragmentos:
#        return "No encontré información relevante sobre eso."
#    
#    print("Fragmentos encontrados:")
#    for f in fragmentos:
#        print(f"- {f['fragmento'][:100]}...")
#
#    contexto = "\n\n".join(["- {}".format(f["fragmento"]) for f in fragmentos])
#
#    prompt = f"""Actuás como un asistente del Ministerio de Economía.
# Respondé solamente con la siguiente información:
#{contexto}
#
#Si no hay información, decí "No tengo información sobre eso".
#
#Pregunta: {consulta}
#"""
#
#    respuesta = ollama.chat(
#        model="llama3.2:1b",
#        messages=[{"role": "user", "content": prompt}]
#    )
#    return respuesta["message"]["content"]
