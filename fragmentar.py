import json

# Cargar el archivo JSON
file_path = "contexto.json"
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Función para dividir contenido en fragmentos manejables
#def dividir_texto(texto, max_length=512):
#    fragmentos = []
#    palabras = texto.split()
#    temp = []
#    
#    for palabra in palabras:
#        temp.append(palabra)
#        if len(" ".join(temp)) > max_length:
#            fragmentos.append(" ".join(temp))
#            temp = []
#    
#    if temp:
#        fragmentos.append(" ".join(temp))
#    
#    return fragmentos
def dividir_texto_overlap(texto, max_length=512, overlap=100):  #este genera fragmentos pisados unos con otros lo cual mejora las respuestas cuando la INFORMACIÓN está entre 2 partes
    palabras = texto.split()
    fragmentos = []
    i=0
    while i < len(palabras):
        chunk=palabras[i:i+max_length]
        fragmento=" ".join(chunk)
        fragmentos.append(fragmento)
        i+=max_length-overlap #avanzamos con solapamiento
    return fragmentos

# Procesar el JSON en fragmentos más pequeños
fragmentos_procesados = []
for item in data:
    titulo = item.get("titulo", "Sin título")
    url = item.get("url", "")
    contenido = item.get("contenido", "")
    
    # Dividir el contenido en fragmentos
    fragmentos = dividir_texto_overlap(contenido)
    
    for i, fragmento in enumerate(fragmentos):
        fragmentos_procesados.append({
            "titulo": titulo,
            "url": url,
            "fragmento": fragmento,
            "id_fragmento": f"{titulo}_{i}"
        })
        



# Mostrar algunos fragmentos de ejemplo
fragmentos_procesados[:5]
