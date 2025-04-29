from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

def respuesta_similar(preguntas, interation_file= "interaccion.json"):
    #buscamos una respuesta similar en las interacciones guardadas
    try:
        with open(interation_file, "r", encoding="utf-8") as file:
            interacciones = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error al cargar el archivo de interacciones: {e}")
        return None
    #extraigo preguntas y respuestas
    preguntas=[interacciones["pregunta"] for interaccion in interacciones]
    respuesta=[interacciones["respuesta"] for interaccion in interacciones]
    
    # Calcular similitud entre la entrada del usuario y las entradas guardadas
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([preguntas] + preguntas)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

    most_similar_index = similarities.argmax()
    if similarities[0, most_similar_index] > 0.7:  # Umbral de similitud
        return respuesta[most_similar_index]
    return None
