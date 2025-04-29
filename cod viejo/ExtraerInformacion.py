from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from iniciar_sesion import iniciar_sesion
from verificador_links import URL_BASE,UBICACION_DRIVER_CHROME
import json
import time
import random
    
def extraer_info(driver,url, archivo_salida="contexto.json"):                
    try:        
        driver.get(url)
        print("📌 La nueva URL es:", driver.current_url)


        #esperamos a que cargue la página
        wait= WebDriverWait(driver, 10)
        h1_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        content = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "entry-content")))

        # Obtener HTML de la página
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        #extraer datos
        h1_text = h1_element.text.strip()
        content_text = content.text.strip()
        content_div = soup.find("div", class_="entry-content")
        if content_div:
            links=content_div.find_all("a") #solo los links dentro del contenido
            if links:
                links_list = [{"texto": link.text.strip(), "url": link.get("href")} for link in links if link.get("href")]
            else:
                links_list = []
                print("No se encontraron links dentro del contenido")
        else:
            print("No se encontró el contenedor")

        # Crear estructura de datos
        datos= {
            "url": url,
            "titulo": h1_text,
            "contenido": content_text,
            "links": links_list
        }

        #guardamos en archivos JSON
    
        try:
            with open(archivo_salida, "r", encoding="utf-8") as file:
                data=json.loads(file.read()) #cargamos los datos existentes
        except(FileNotFoundError, json.JSONDecodeError):
            data=[] #sino existe iniciamos una lista vacia

        data.append(datos) #agregamos los datos extraidos
        with open(archivo_salida, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)# Guardar en formato JSON legible

        print(f"Datos extraídos y guardados en {archivo_salida}")
    except TimeoutException:
        print(f"❌ Tiempo de espera agotado al cargar la página: {url}")
    except WebDriverException as e:
        print(f"❌ Error en WebDriver al procesar {url}: {e}")
    except Exception as e:
        print(f"❌ Error inesperado al procesar {url}: {e}")
    if datos is None:
        print(f"❌ No se pudo extraer información de {url}.")
        return False
    else:
        return True


def extraer_toda_info(archivo_links="links_procesados.json", archivo_salida="contexto.json"):
    # Iniciamos sesión y obtenemos el driver
    driver = iniciar_sesion(URL_BASE, UBICACION_DRIVER_CHROME)
        
    # Tratamos de leer los links procesados
    try:
        with open(archivo_links, "r", encoding="utf-8") as file:
            links_data = json.loads(file.read())
            print("📜 Links a procesar:", links_data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error al cargar el archivo de links: {e}")
        driver.quit()
        return
    
    # Ahora extraemos la info de cada link
    for url in links_data.keys():
        if isinstance(url, str) and isinstance(links_data[url], bool):  # Validamos formato
            print(f"🔍 Extrayendo información de: {url}")
            try:
                if not verificar_driver(driver):
                    print("❌ El driver no está conectado. Reiniciando...")
                    driver.quit()
                    driver = iniciar_sesion(URL_BASE, UBICACION_DRIVER_CHROME)
                
                if not links_data[url]:  # Solo procesamos si está en True
                    print(f"🔸 {url} ya fue procesado.")
                else:
                    if extraer_info(driver, url, archivo_salida):
                        links_data[url] = False  # Marcamos false para indicar que está procesado
                    time.sleep(random.uniform(1, 3))  # Espera aleatoria para evitar bloqueos
            except Exception as e:
                print(f"❌ Error al extraer información de {url}: {e}")
        else:
            print(f"❌ Formato incorrecto en el JSON: {url}")
            continue
    
    # Guardar el diccionario actualizado en el archivo JSON (una sola vez al final)
    try:
        with open(archivo_links, 'w', encoding="utf-8") as file:
            json.dump(links_data, file, indent=4)
            print(links_data)
    except Exception as e:
        print(f"❌ Error al guardar el archivo de links: {e}")
    
    driver.quit()
    print("✅ Proceso completado.")
   
def verificar_driver(driver):
    """verificar si el driver está activo"""
    try:
        driver.current_url
        return True
    except WebDriverException:
        return False    



extraer_toda_info()