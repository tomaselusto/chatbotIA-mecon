import ollama
import json
import sqlite3
from selfEducation import respuesta_similar
from log import log_interaction
from vectorizar_contexto import encontrar_seccion_relevante

def conectar_db():
    conn=sqlite3.connect("chatbot.db")
    conn.row_factory=sqlite3.Row #accedemos a las columnas por nombre
    return conn

def cargar_contexto():
    conn=conectar_db()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM CONTEXTO")
    contexto=cursor.fetchall()
    conn.close()
    return contexto

def guardar_interaccion(pregunta,respuesta):
    conn=conectar_db()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO interacciones(pregunta, respuesta) VALUES(?,?)",(pregunta, respuesta))
    conn.commit()
    conn.close()
    

def preguntar(pregunta, archivo_contexto="contexto.json", archivo_interacciones="interaccion.json"):
    
      
    #cargo el contexto desde el JSON
    with open(archivo_contexto,"r",encoding="utf-8") as file:
        data=json.load(file)
    
    # Formatear el contexto con Markdown
    contexto = "\n\n".join([
        f"### 📌 Título: {item['titulo']}\n\n**📖 Contenido:**\n{item['contenido']}\n\n🔗 **Links Relacionados:**\n" +
        "\n".join([f"- [{link['texto']}]({link['url']})" for link in item['links']])
        for item in data
    ])
    #buscar respuesta similar en las interacciones guardadas
    respuesta=respuesta_similar(pregunta, archivo_interacciones)
    if respuesta:
        print(f"🤖 **Respuesta:**\n{respuesta}")
        log_interaction(pregunta, respuesta)
        return
    
    
    seccion_relevante=encontrar_seccion_relevante(pregunta, data)
    contexto_a_usar=seccion_relevante if seccion_relevante else contexto
    
      # Enviar la pregunta a Ollama
    respuesta = ollama.chat(model="llama3.2:1b", messages=[
        {"role": "system", "content": "Eres un asistente que responde preguntas basadas en el siguiente contexto."},
        {"role": "user", "content": contexto_a_usar},
        {"role": "user", "content": pregunta}
    ])
    
    respuesta_texto=respuesta['message']['content']
    respuesta_formateada= f"🤖 **Respuesta:**\n{respuesta_texto}"
    
    print(respuesta_formateada)
    log_interaction(pregunta, respuesta_texto)
    
    #guardar la nueva interacción en el archivo de interacciones
    try:
        with open(archivo_interacciones, "r", encoding="utf-8") as file:
            interacciones=json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        interacciones = []
    
    interacciones.append({"pregunta": pregunta, "respuesta": respuesta_texto})
    
    with open(archivo_interacciones, "w", encoding="utf-8") as file:
        json.dump(interacciones, file, indent=4, ensure_ascii=False)
        
        
def preguntar_desde_bd(pregunta):
    # Cargar el contexto desde la base de datos
    contexto_db = cargar_contexto()
    
    # Formatear el contexto con Markdown
    contexto = "\n\n".join([
        f"### 📌 Título: {item['titulo']}\n\n**📖 Contenido:**\n{item['contenido']}\n\n🔗 **Links Relacionados:**\n" +
        "\n".join([f"- [{link['texto']}]({link['url']})" for link in item['links']])
        for item in contexto_db
    ])
    
    # Buscar respuesta similar en las interacciones guardadas
    respuesta = respuesta_similar(pregunta)
    if respuesta:
        print(f"🤖 **Respuesta (similar):**\n{respuesta}")
        log_interaction(pregunta, respuesta)
        return
    
    # Buscar la sección más relevante del contexto
    seccion_relevante = encontrar_seccion_relevante(pregunta, contexto_db)
    
    # Usar la sección relevante o el contexto completo
    contexto_a_usar = seccion_relevante if seccion_relevante else contexto
    
    # Enviar la pregunta a Ollama
    respuesta = ollama.chat(model="llama3.2:1b", messages=[
        {"role": "system", "content": "Eres un asistente que responde preguntas basadas en el siguiente contexto."},
        {"role": "user", "content": contexto_a_usar},
        {"role": "user", "content": pregunta}
    ])
    
    respuesta_texto = respuesta['message']['content']
    respuesta_formateada = f"🤖 **Respuesta:**\n{respuesta_texto}"
    
    print(respuesta_formateada)
    log_interaction(pregunta, respuesta_texto)
    
    # Guardar la nueva interacción en la base de datos
    guardar_interaccion(pregunta, respuesta_texto)

while True:
    pregunta_usuario=input("\n💬 Escribe tu pregunta (o 'salir' para terminar): ")
    if pregunta_usuario.lower() == "salir":
        print("👋 ¡Hasta luego!")
        break
    preguntar(pregunta_usuario)