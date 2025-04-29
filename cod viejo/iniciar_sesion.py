from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import getpass


def iniciar_sesion(url,ubicacion_driver):
    #usuario= input("usuario: ")
    usuario= "telusto_mecon"
    contrasena="Amigus67!!"# Esto oculta la contraseña al escribirla
    #contrasena=getpass.getpass("contraseña: ")# Esto oculta la contraseña al escribirla
    driver= webdriver.Chrome()
    servicio = Service(ubicacion_driver)
    opciones = Options()
    opciones.add_argument("--headless")  # Para ejecutar en segundo plano
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=servicio, options=opciones)
    driver.get(url)
    campo_usuario = driver.find_element(By.NAME, "userName")  # Reemplaza con el atributo real
    campo_contrasena = driver.find_element(By.NAME, "loginInput")  # Reemplaza con el atributo real
    # Ingresar los datos
    campo_usuario.send_keys(usuario)
    campo_contrasena.send_keys(contrasena)
    campo_contrasena.send_keys(Keys.RETURN)
    
    return  driver # Devolver el driver para usarlo en otras funciones


def verificar_sesion(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product_name")))
        print("Sesión iniciada correctamente")
        return True
    except:
        print("Error al iniciar sesión")
        return False
    
