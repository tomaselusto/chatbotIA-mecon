import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import archivo_json

#cargamos modelo embedding
model=SentenceTransformer("all-MiniLM-L6-v2")

#cargamos el JSON con la info
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        datos= json.load(f)
    return datos
    
#extraemos los datos a vectorizar
def extraer_texto(datos):
    textos=[]
    urls=[]
    for entry in datos:
        content=entry.get("contenido","")
        title=entry.get("titulo","")
        url=entry.get("url","")
        full_text=f"{title}\n{content}"
        textos.append(full_text)
        urls.append(url)
    return textos, urls

#convertimos texto en vectores con sentencetrasnformers
def vectorizar_texto(texto):
    return model.encode(texto, convert_to_numpy=True)

#guardamos los vectores y las url en un archivo npz para usar en FAISS
def guardar_vectores(vectors,urls,output_path):
    np.savez(output_path, vectores=vectors, urls=np.array(urls))
    
if __name__=="__main__":
    
    output_file= "vectors.npz"
    
    datos=load_json(archivo_json)
    textos, urls=extraer_texto(datos)
    vectores=vectorizar_texto(textos)
    guardar_vectores(vectores,urls,output_file)
    
    
    print(f"Vectorización completada. Se guardaron {len(vectores)} vectores en '{output_file}'")
