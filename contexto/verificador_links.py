import json
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

#archivo que guardará los links procesados
ARCHIVO_LINKS= "links_procesados.json"
URL_BASE="https://intranet.mecon.gob.ar/tramites/rrhh/"
UBICACION_DRIVER_CHROME="C:/Users/telusto_mecon/Desktop/contexto/chromedriver-win64/chromedriver.exe"


def es_url_valida(url):
    """Verifica si una URL es válida."""
    regex = re.compile(
    r'^(?:http|ftp)s?://'                             # http:// o https:// o ftp://
    r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'     # subdominio(s)
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)'              # dominio
    r'(?:/?|[/?]\S+)$',                               # ruta
    re.IGNORECASE)
    return re.match(regex, url) is not None

def filtrar_urls_validas(links):
    """Filtra URLs válidas y elimina duplicados."""
    return {url: True for url in links if es_url_valida(url)} #

def obtener_links(driver):  
    try:       
        driver.get("https://intranet.mecon.gob.ar/tramites/rrhh/")
        wait=WebDriverWait(driver, 10)
        print("📌 La nueva URL es:", driver.current_url)
        xpath_div = "//main//div//div//div//article//div[contains(@class, 'entry-content')]"
        div_contenedor = esperar_por_elemento(driver, xpath_div)
        if div_contenedor:
            print("✅ Elemento encontrado!")
        else:
            print("❌ No se encontró el elemento después de 10 segundos.")

        # Extraemos todos los links dentro de ese div
        links =filtrar_urls_validas({a.get_attribute("href"): True for a in div_contenedor.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")})
        return links
    #links = [a.get_attribute("href") for a in div_contenedor.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]
    except TimeoutException:
        print("❌ Tiempo de espera agotado al cargar la página.")
        return {}
    except WebDriverException as e:
        print(f"❌ Error en WebDriver: {e}")
        return {}
    finally:
        driver.quit()
    


def esperar_por_elemento(driver, xpath, tiempo_max=10):
    """Espera a que el elemento aparezca en el DOM antes de interactuar con él."""
    tiempo_inicial = time.time()
    while time.time() - tiempo_inicial < tiempo_max:
        if len(driver.find_elements(By.XPATH, xpath)) > 0:
            return driver.find_element(By.XPATH, xpath)
        time.sleep(1)  # Espera 1 segundo antes de reintentar
    return None


    
def cargar_links_guardados():
    """cargar los links guardados en el archivo"""
    if not os.path.exists(ARCHIVO_LINKS):
        return {}  # De no existir el archivo devolvemos un conjunto vacío
    try:
        with open(ARCHIVO_LINKS, "r", encoding="utf-8") as f:
            return json.load(f)  # Convertimos a set al cargar los datos
    except json.JSONDecodeError:
        print("❌ Error al decodificar el archivo JSON. Se devolverá un diccionario vacío.")
        return {}
    except Exception as e:
        print(f"❌ Error inesperado al cargar el archivo: {e}")
        return {}

    
    
def guardar_links_nuevos(nuevos_links):
    """guardar los links nuevos en el archivo"""
    try:
        with open(ARCHIVO_LINKS, "w", encoding="utf-8") as f:
            json.dump(nuevos_links, f, indent=4)  # Convertimos el set en lista para guardarlo
    except Exception as e:
        print(f"❌ Error al guardar los links: {e}")

def hay_nueva_informacion():
    """verificar si hay nueva información"""
    service= Service(UBICACION_DRIVER_CHROME)
    opciones = Options()
    options= webdriver.ChromeOptions()
    options.add_argument("--Headless") #ejecuta sin abrir la ventana
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    driver= webdriver.Chrome(service=service, options=options)
    driver.get(URL_BASE)
    
    links_guardados = cargar_links_guardados()
    links_actuales = obtener_links(driver)
    nuevos_links = set(links_actuales.keys()) - set(links_guardados.keys())
    #nuevos_links = {link: True for link in links_actuales.keys() if link not in links_guardados}
    if nuevos_links:
        print(f"🔔 ¡Hay{len(nuevos_links)} links nuevos!")
        for link in nuevos_links:
            print(f" ➜ {link}")
        guardar_links_nuevos({**links_guardados, **links_actuales})  # Fusionamos los diccionarios
        #guardar_links_nuevos(links_actuales) #Actualiza el archivo con todos los links
        return True
 
    else:
        print("🔕 No hay información nueva.")
        return False
        
   
    

if __name__ == "__main__":
    hay_nueva_informacion()