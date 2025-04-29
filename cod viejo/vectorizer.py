import json
import faiss
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class Database:
    def __init__(self, db_path: str = "chatbot.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS qa (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT UNIQUE,
                            answer TEXT)''')
        self.conn.commit()

    def insert_qa(self, question: str, answer: str):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO qa (question, answer) VALUES (?, ?)", (question, answer))
        self.conn.commit()

    def fetch_all_qa(self) -> List[Tuple[str, str]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT question, answer FROM qa")
        return cursor.fetchall()
    
    def fetch_answer(self, question: str) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT answer FROM qa WHERE question = ?", (question,))
        result = cursor.fetchone()
        return result[0] if result else None

class ChatbotFAISS:
    def __init__(self, db_path: str = "chatbot.db", index_path: str = "faiss_index.idx"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.db = Database(db_path)
        self.index_path = index_path
        self.index = None
        self.init_faiss()
    
    def init_faiss(self):
        try:
            self.index = faiss.read_index(self.index_path)
        except:
            self.create_faiss_index()
    
    def create_faiss_index(self):
        qa_pairs = self.db.fetch_all_qa()
        if not qa_pairs:
            self.index = faiss.IndexFlatL2(384)
            return
        
        questions = [q for q, _ in qa_pairs]
        embeddings = np.array(self.model.encode(questions), dtype=np.float32)
        
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        faiss.write_index(self.index, self.index_path)
    
    def search(self, query: str, top_k: int = 3) -> List[str]:
        query_embedding = np.array(self.model.encode([query]), dtype=np.float32)
        distances, indices = self.index.search(query_embedding, top_k)
        qa_pairs = self.db.fetch_all_qa()
        return [qa_pairs[i][1] for i in indices[0] if i < len(qa_pairs)]
    
    def chat(self, query: str) -> str:
        db_answer = self.db.fetch_answer(query)
        if db_answer:
            return db_answer
        
        results = self.search(query)
        if results:
            return "\n\n".join(results)
        
        new_answer = input("No tengo respuesta, ¿cómo debería responder? ")
        self.db.insert_qa(query, new_answer)
        self.create_faiss_index()  # Reindexamos FAISS con la nueva pregunta
        return "¡Gracias! Aprendí una nueva respuesta."

if __name__ == "__main__":
    chatbot = ChatbotFAISS()
    while True:
        query = input("Usuario: ")
        if query.lower() in ["salir", "exit"]:
            break
        response = chatbot.chat(query)
        print("Chatbot:", response)
