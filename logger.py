import json,datetime

def guardar_interaccion(pregunta, respuesta, resultado="sin feedback"):
    log ={
        "pregunta": pregunta,
        "respuesta": respuesta,
        "resultado": resultado,
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open("logs_chat.jsonl", "a", encoding="utf-8") as file:
        file.write(json.dumps(log, ensure_ascii=False) + "\n")