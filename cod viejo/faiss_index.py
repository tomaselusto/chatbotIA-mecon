import faiss
import numpy as np
import os

class FaissIndex:
    def __init__(self, index_path="faiss_index.bin", dimension=384):
        self.index_path=index_path
        self.dimension=dimension
        self.index=faiss.IndexFlatL2(dimension)
        
    def build_index(self, vectors, metadata):
        #construimos el índice FAISS con lso vectores y almacenamos la metadata(URLs, títulos).
        vectors=np.array(vectors, dtype=np.float32)
        self.index.add(vectors)
        self.metadata=metadata
        self.save_index()
    
    def save_index(self):
        #guardamos el archivo faiss en un archivo
        faiss.write_index(self.index, self.index_path)
        np.save(self.index_path + "_metadata.npy", allow_pickle=True)
    
    def load_index(self):
        #carga el indice faiss desde un archivo
        if os.path.exists(self.index_path):
            self.index=faiss.read_index(self.index_path)
            self.metadata=np.load(self.index_path +"_metadata.npy", allow_pickle=True).tolist()
        else:
            print("no se encontró un índiuce FAISS para guardado")
            
    def search(self, query_vector, k=5):
        #realiza una busqueda en el índice y devuelve los resultados
        query_vector=np.array(query_vector, dtype=np.float32).reshape(1,-1)
        distance, indices= self.index.search(query_vector, k)
        result= [(self.metadata[i], distance[0][j]) for j,i in enumerate(indices[0]) if i!= -1]
        return result
        