from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

def encontrar_seccion_relevante(pregunta, contexto):
    #encontrar la sección más relevante en el contexto para la pregunta dada
       # Preprocesar el contexto en secciones
    secciones = [
        f"{item['titulo']}\n{item['contenido']}\n" +
        "\n".join([f"{link['texto']} {link['url']}" for link in item['links']])
        for item in contexto
    ]
    
    #vectorizar las secciones y las preguntas
    vectorizer = TfidfVectorizer()
    Tfidf_matrix = vectorizer.fit_transform([pregunta] + secciones)
    
    #calcular la similitud
    similitudes = cosine_similarity(Tfidf_matrix[0:1], Tfidf_matrix[1:])
    
    #encontrar la sección más similar
    indice_mas_similar = similitudes.argmax()
    if similitudes[0, indice_mas_similar]>0.2: #umbral de similitud
        return secciones[indice_mas_similar]
    else:
        return None

def dividir_en_parrafos(texto):
    #dividir el texto en párrafos basado en los saltos de linea, eliminando párrafos vacíos
    parrafos= [p.strip() for p in texto.split("\n") if p.strip()]
    return parrafos    
    
def vectorizar_contexto(archivo_contexto="contexto.json"):
    with open (archivo_contexto, "r", encoding="utf-8") as file:
        contexto=json.load(file)
    
    documentos=[]
    metadata=[]
    
    for item in contexto:
        print(f"Dividiendo: {item['contenido']} ")
        parrafos= dividir_en_parrafos(item['contenido'])
        for parrafo in parrafos:
            documentos.append(parrafo)
            metadata.append({
                "titulo": item["titulo"],
                "url": item["url"],
                "parrafo": parrafo,
                "links": item["links"]  # Guardar los links asociados
            })
    #creamos el vectorizador TF-IDF
    vectorizador= TfidfVectorizer()
    matriz_tfidf=vectorizador.fit_transform(documentos)
    
    return vectorizador,matriz_tfidf,metadata


def econtrar_parrafo_mas_relevante(pregunta, vectorizador,matriz_tfidf, metada):
    #vectorizamos la pregunta
    pregunta_vectorizada=vectorizador.transform([pregunta])
    
    #calculamos la similitud entre pregunta y parrafos
    similitudes=cosine_similarity(pregunta_vectorizada, matriz_tfidf)
    
    #econtramos el índice del parrafo más relevante
    indice_mas_relevante= similitudes.argmax()
    
    #devolvemos el parrafo más relevante junto con su metadata
    return metada[indice_mas_relevante]

#vectorizador, matriz_tfidf,metada= vectorizar_contexto()
#pregunta="¿cómo puedo afiliarme a la Obra Social OSME?"
#parrafo_relevante= econtrar_parrafo_mas_relevante(pregunta,vectorizador,matriz_tfidf, metada)
#print("
# Párrafo más relevnate: ", parrafo_relevante)
    