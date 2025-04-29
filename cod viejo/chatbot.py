import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class ChatbotFAISS:
    def __init__(self, json_path: str, index_path: str = "faiss_index.idx"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.json_path = json_path
        self.index_path = index_path
        self.data = self.load_json()
        self.index = None
        self.init_faiss()
    
    def load_json(self):
        with open(self.json_path, "r", encoding="utf-8") as file:
            return json.load(file)
    
    def init_faiss(self):
        """Inicializa FAISS y carga los embeddings si existen, sino los crea."""
        try:
            self.index = faiss.read_index(self.index_path)
        except:
            self.create_faiss_index()
    
    def create_faiss_index(self):
        """Vectoriza el contenido y crea un índice FAISS."""
        texts = [entry["contenido"] for entry in self.data]
        embeddings = np.array(self.model.encode(texts), dtype=np.float32)
        
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        faiss.write_index(self.index, self.index_path)
    
    def search(self, query: str, top_k: int = 3) -> List[dict]:
        """Busca en FAISS los documentos más relevantes para la consulta."""
        query_embedding = np.array(self.model.encode([query]), dtype=np.float32)
        distances, indices = self.index.search(query_embedding, top_k)
        return [self.data[i] for i in indices[0]]
    
    def chat(self, query: str) -> str:
        """Genera una respuesta basada en los documentos recuperados."""
        results = self.search(query)
        return "\n\n".join([f"Título: {res['titulo']}\nURL: {res['url']}\nContenido: {res['contenido']}" for res in results]) if results else "No encontré información relevante."

if __name__ == "__main__":
    chatbot = ChatbotFAISS("contexto.json")
    while True:
        query = input("Usuario: ")
        if query.lower() in ["salir", "exit"]:
            break
        response = chatbot.chat(query)
        print("Chatbot:", response)