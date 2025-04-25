import json
from sentence_transformers import SentenceTransformer
import chromadb
import ollama

# Cargar el archivo JSON
with open("contexto.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Función para dividir contenido en fragmentos manejables
def dividir_texto(texto, max_length=512):
    fragmentos = []
    palabras = texto.split()
    temp = []
    
    for palabra in palabras:
        temp.append(palabra)
        if len(" ".join(temp)) > max_length:
            fragmentos.append(" ".join(temp))
            temp = []
    
    if temp:
        fragmentos.append(" ".join(temp))
    
    return fragmentos

# Cargar el modelo de embeddings
modelo_embeddings = SentenceTransformer("all-MiniLM-L6-v2")

# Inicializar ChromaDB (almacenamiento persistente)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="chatbot_contexto")

# Procesar el JSON en fragmentos más pequeños y almacenarlos en ChromaDB
for item in data:
    titulo = item.get("titulo", "Sin título")
    url = item.get("url", "")
    contenido = item.get("contenido", "")
    
    fragmentos = dividir_texto(contenido)
    
    for i, fragmento in enumerate(fragmentos):
        fragment_id = f"{titulo}_{i}"
        embedding = modelo_embeddings.encode(fragmento).tolist()
        
        collection.add(
            ids=[fragment_id],
            embeddings=[embedding],
            metadatas=[{"titulo": titulo, "url": url}],
            documents=[fragmento]
        )

# Verificar cuántos documentos se almacenaron
print(f"Fragmentos almacenados en ChromaDB: {collection.count()}")


def buscar_en_bd(consulta, top_k=3):
    #convertir la consutla en un embedding
    embedding_consulta= modelo_embeddings.encode(consulta).tolist()
    #buscar en la bd vectorial
    resultados=collection.query(
        query_embeddings=[embedding_consulta],
        n_results=top_k
    )
    
    #extraemos lo que encontramos
    fragmentos_encontrados=[]
    for i in range(len(resultados["documents"][0])):
        fragmentos_encontrados.append({
            "fragmento":resultados["documents"][0][i],
            "titulo":resultados["metadatas"][0][i]["titulo"],
            "url":resultados["metadatas"][0][i]["url"],
        })
    return fragmentos_encontrados

def generar_respuesta(consulta):
    fragmentos = buscar_en_bd(consulta)
    print("📌 Fragmentos encontrados:", fragmentos)
    #contexto para ollama
    if isinstance(fragmentos, list) and all(isinstance(f, dict) for f in fragmentos):
        #contexto = "\n\n".join(["- {}".format(f["fragmento"]) for f in fragmentos])
        contexto = "\n\n".join(["- {}".format(f.get("fragmento", "")) for f in fragmentos])
    else:
        contexto = "No se encontró información relevante en la base de datos."

    # Prompt para Ollama
    #prompt = f"""Actúa como un asistente especializado en información interna.
#    Responde únicamente usando los siguientes fragmentos de información:
   # 
    ##{contexto}
##
    ##Si no hay información relevante en estos fragmentos, responde con "No tengo información sobre eso".
    #
    #Pregunta: {consulta}
    #"""
    prompt = f"""Usa la siguiente información para responder de forma certera y simple la consulta del usuario:
    {contexto}
    
    Pregunta: {consulta}
    Responde de manera clara y precisa, y agrega la fuente de la respuesta
    """

    # Consultar Ollama
    respuesta = ollama.chat(model="llama3.2:1b", messages=[{"role": "user", "content": prompt}])
    
    return respuesta["message"]["content"]
    
while True:
    consulta_usuario=input("📝 Pregunta: ")
    if consulta_usuario.lower() in ["salir", "exit"]:
        break
    respuesta_chatbot = generar_respuesta(consulta_usuario)
    print(f"🤖 Chatbot: {respuesta_chatbot}\n")
    
    
    
    
    
    
    
    
    
    
    
    
# Prueba de búsqueda
#consulta_usuario = "¿Cómo tramitar asignaciones familiares?"
#resultados = buscar_en_bd(consulta_usuario)
#
# Mostrar resultados
#for r in resultados:
#    print(f"📌 {r['titulo']}\n🔗 {r['url']}\n📝 {r['fragmento']}\n")
    
    
