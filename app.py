import streamlit as st
from logger import guardar_interaccion
import json, datetime
from chat_core import dividir_texto_overlap, modelo_embeddings, collection
import os, fitz, docx
from cargarContexto import cargar_contexto_desde_json

st.set_page_config(page_title="Recursos Humanos - Ministerio de Economía", page_icon="🤖")


# Cargar automáticamente el contexto si la base está vacía
if collection.count() == 0:
    st.warning("⚠️ Base vacía. Cargando contexto.json automáticamente...")
    cargados = cargar_contexto_desde_json()
    st.success(f"📄 Se cargaron {cargados} fragmentos.")

st.sidebar.markdown("### ℹ️ Estado de la colección")
try:
    from chat_core import collection
    total_docs = collection.count()
    st.sidebar.success(f"📄 Fragmentos cargados: {total_docs}")
except Exception as e:
    st.sidebar.error(f"❌ Error al consultar ChromaDB: {e}")

modo= st.sidebar.radio("📋 Modo", ["Chat", "Ver Logs"]) #seleccionamos el modo
debug_mode = st.sidebar.checkbox("🪛 Modo debug", value=False)


# Intentar importar el chatbot
try:
    from chat_core import generar_respuesta
    st.success("✅ Backend cargado correctamente.")
except Exception as e:
    st.error(f"❌ Error al cargar el backend: {e}")
    st.stop()

#modo log:
if modo == "Ver Logs":
    st.title("📊 Historial de Interacciones")
    try:
        with open("logs_chat.jsonl", "r", encoding="utf-8") as f:
            lineas = f.readlines()
            if not lineas:
                st.info("Aún no hay interacciones guardadas.")
            else:
                for linea in reversed(lineas[-50:]):  # Mostrar los últimos 50
                    log = json.loads(linea)
                    st.markdown(f"**🕒** {log['timestamp']}")
                    st.markdown(f"**🧑 Usuario:** {log['pregunta']}")
                    st.markdown(f"**🤖 Chatbot:** {log['respuesta']}")
                    st.markdown(f"**📌 Feedback:** {log.get('resultado', 'sin feedback')}")
                    st.markdown("---")
    except FileNotFoundError:
        st.warning("El archivo de logs aún no existe.")
    st.stop()  # No seguimos con el modo chat   

# Modo Chat
   
st.title("🤖 Maranito - Recursos Humanos - Ministerio de Economía")
st.write("Consultá sobre la información interna de Recursos Humanos.")
#subida de documentos
st.subheader("📁 Subir nuevo documento PDF, DOCX o JSON")
archivo_subido = st.file_uploader("Seleccioná un archivo JSON válido", type=["json","pdf","docx"]) #Esto te permite subir archivos .json como el original, y el chatbot los va "entrenando" en tiempo real
if archivo_subido is not None:
    try:
        total_fragmentos = 0
        now = datetime.datetime.now().timestamp()

        # JSON
        if archivo_subido.name.endswith(".json"):
            data = json.load(archivo_subido)
            for item in data:
                titulo = item.get("titulo", "Sin título")
                url = item.get("url", "")
                contenido = item.get("contenido", "")
                fragmentos = dividir_texto_overlap(contenido)

                for i, fragmento in enumerate(fragmentos):
                    fragment_id = f"{titulo}_{i}_{now}"
                    embedding = modelo_embeddings.encode(fragmento).tolist()
                    collection.add(
                        ids=[fragment_id],
                        embeddings=[embedding],
                        metadatas=[{"titulo": titulo, "url": url}],
                        documents=[fragmento]
                    )
                    total_fragmentos += 1

        # PDF
        elif archivo_subido.name.endswith(".pdf"):
            pdf = fitz.open(stream=archivo_subido.read(), filetype="pdf")
            texto_pdf = ""
            for page in pdf:
                texto_pdf += page.get_text()
            pdf.close()

            fragmentos = dividir_texto_overlap(texto_pdf)
            for i, fragmento in enumerate(fragmentos):
                fragment_id = f"PDF_{i}_{now}"
                embedding = modelo_embeddings.encode(fragmento).tolist()
                collection.add(
                    ids=[fragment_id],
                    embeddings=[embedding],
                    metadatas=[{"titulo": archivo_subido.name, "url": ""}],
                    documents=[fragmento]
                )
                total_fragmentos += 1

        # DOCX
        elif archivo_subido.name.endswith(".docx"):
            doc = docx.Document(archivo_subido)
            texto_doc = "\n".join([p.text for p in doc.paragraphs])
            fragmentos = dividir_texto_overlap(texto_doc)
            for i, fragmento in enumerate(fragmentos):
                fragment_id = f"DOCX_{i}_{now}"
                embedding = modelo_embeddings.encode(fragmento).tolist()
                collection.add(
                    ids=[fragment_id],
                    embeddings=[embedding],
                    metadatas=[{"titulo": archivo_subido.name, "url": ""}],
                    documents=[fragmento]
                )
                total_fragmentos += 1

        st.success(f"✅ Documento indexado correctamente. Fragmentos añadidos: {total_fragmentos}")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
#Interfaz del chatbot
if "historial" not in st.session_state:
    st.session_state.historial = []

consulta = st.text_input("✍️ Escribí tu consulta:")

if st.button("Enviar") and consulta.strip():
    with st.spinner("🤖 Generando respuesta..."):
        try:
            from chat_core import buscar_en_chromadb  # solo para modo debug

            fragmentos = buscar_en_chromadb(consulta, top_k=5)
            if not fragmentos:
                respuesta = "No encontré información relevante sobre eso."
            else:
                contexto = "\n\n".join([
                    f"Título: {f['titulo']}\nContenido: {f['fragmento']}"
                    for f in fragmentos
                ])
                
                if debug_mode:
                    st.subheader("🧩 Fragmentos encontrados")
                    for i, f in enumerate(fragmentos):
                        st.markdown(f"**{i+1}. {f['titulo']}**")
                        st.code(f["fragmento"][:700] + "...")

                    st.subheader("🧠 Contexto enviado a Ollama")
                    st.code(contexto[:3000] + "...")

                from chat_core import ollama
                prompt = f"""Sos un asistente del Ministerio de Economía.
Respondé solamente con la siguiente información. No inventes datos.

{contexto}

Pregunta del usuario: {consulta}

Si no hay información suficiente para responder, decí: "No tengo información sobre eso".
"""             
                respuesta_obj = ollama.chat(
                    model="llama3.2:1b",
                    messages=[{"role": "user", "content": prompt}]
                )

                respuesta = respuesta_obj["message"]["content"]

            st.session_state.historial.append((consulta, respuesta))
            guardar_interaccion(consulta, respuesta)
        except Exception as e:
            st.error(f"❌ Error al generar respuesta: {e}")
            
                
        try:
            respuesta = generar_respuesta(consulta)
            guardar_interaccion(consulta, respuesta)  # Guardar la interacción en el log
            st.session_state.historial.append((consulta, respuesta)) #feedback sin valor aún
        except Exception as e:
            st.error(f"❌ Error al generar respuesta: {e}")
            
#mostrar historial
st.divider()
st.subheader("💬 Historial de conversación")
for idx, (pregunta, respuesta) in enumerate(reversed(st.session_state.historial)):
    st.markdown(f"🧑 **Usuario:** {pregunta}")
    st.markdown(f"🤖 **Chatbot:** {respuesta}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("👍 Útil", key=f"like_{idx}"):
            guardar_interaccion(pregunta, respuesta, resultado="👍")
            st.success("¡Gracias por tu feedback!")
    with col2:
        if st.button("👎 No fue útil", key=f"dislike_{idx}"):
            guardar_interaccion(pregunta, respuesta, resultado="👎")
            st.warning("Gracias, lo tendremos en cuenta.")

    st.markdown("---")

#for pregunta, respuesta in reversed(st.session_state.historial):
#    st.markdown(f"**🧑 Usuario:** {pregunta}")
#    st.markdown(f"**🤖 Chatbot:** {respuesta}")
#    st.markdown("---")
