import json
import time
from verificador_links import hay_nueva_informacion
from ExtraerInformacion import extraer_toda_info
from chatBot import preguntar

def main():
    print("🔹 Verificando nuevos links...")
    hay_nueva_informacion()  # Actualiza 'links_prdoocesados.json'
    
    print("🔹 Extrayendo información de los nuevos links...")
    extraer_toda_info()  # Extrae info y la guarda en 'contexto.json'

    print("🔹 Cargando información en el chatbot...")
    with open("archivos/contexto.json", "r", encoding="utf-8") as file:
        contexto = json.load(file)

    print("✅ Todo listo. Iniciando el chatbot con la nueva información.")
    preguntar(contexto)  # Pasamos la info extraída al chatbot
    




if __name__=="__main__":
    main()