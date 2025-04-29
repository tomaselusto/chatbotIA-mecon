import logging

logging.basicConfig(filename="chatbot_interaction.log", level=logging.INFO,
                    format='%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

def log_interaction(pregunta, respuesta):
    logging.info(f"Pregunta: {pregunta}")
    logging.info(f"Respuesta: {respuesta}")
    logging.info("----")
    #registramos la interacción del usuario
