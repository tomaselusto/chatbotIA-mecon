from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time
import random


URL_BASE="https://intranet.mecon.gob.ar/tramites/rrhh/"
UBICACION_DRIVER_CHROME="C:/Users/telusto_mecon/Desktop/contexto/chromedriver-win64/chromedriver.exe"

def verificar_driver(driver):
    #verificar si el driver está activo
    try:
        driver.current_tul
        return True
    except WebDriverException:
        return False

def extraer_info(driver, url, archivo_salida="contexto.json"):
    datos = None  
    try:
        driver.get(url)
        print("📌 La nueva URL es:", driver.current_url)

        #esperamos a que cargue la página
        wait=WebDriverWait(driver, 10)
        h1_element=  wait.until(EC.presence_of_element_located((By.TAG_NAME,"h1")))
        content= wait.until(EC.presence_of_element_located((By.CLASS_NAME, "entry-content")))
        
        # Esperás los elementos <li> que pueden contener los íconos
        ul_items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li")))

        telefono = None
        email = None
        
        for li in ul_items:
            try:
                icon = li.find_element(By.TAG_NAME, "i")
                if "fa-phone" in icon.get_attribute("class"):
                    telefono = li.text.strip()
                elif "fa-envelope" in icon.get_attribute("class"):
                    email_elem = li.find_element(By.TAG_NAME, "a")
                    email = email_elem.get_attribute("href").replace("mailto:", "").strip()
            except:
                continue
        
        #obtener HTML    
        page_source= driver.page_source
        soup=BeautifulSoup(page_source,"html.parser")
        
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

        #creamos la estructura de datos:
        datos={
            "url":url,
            "titulo": h1_text,
            "contenido":content_text,
            "telefóno": telefono,
            "email":email,
            "links": links_list
        }


        #guardamos en archivo JSON
        try:
            with open(archivo_salida, "r", encoding="utf-8") as file:
                data=json.loads(file.read()) #cargamos data existende
        except(FileNotFoundError, json.JSONDecodeError):
            data=[] #sino existe lo creamos

        data.append(datos) #agregamos datos extraidos
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



def recopilar_informacion(archivo_links="links_procesados.json",archivo_salida="contexto.json"):
    #inicializamos el driver
    
    servicio = Service(UBICACION_DRIVER_CHROME)
    opciones = Options()
    opciones.add_argument("--headless")  # Para ejecutar en segundo plano
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=servicio, options=opciones)
    driver.get(URL_BASE)

    #tratamos de procesar el arhivo de links
    try:
        with open(archivo_links, "r", encoding="utf-8") as file:
            links_data=json.loads(file.read())
            print("📜 Links a procesar:", links_data)

    except(FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error al cargar el archivo de links: {e}")
        driver.quit()
        return
    
    #extraemos la info de cada link
    for url in links_data.keys():
        if isinstance(url, str) and isinstance(links_data[url], bool):  # Validamos formato
            print(f"🔍 Extrayendo información de: {url}")
            try: 
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

                            
recopilar_informacion()