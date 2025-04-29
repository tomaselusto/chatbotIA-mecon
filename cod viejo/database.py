import sqlite3

def init_db(db_path="chatbot.db"):
    #Crea la base de datos y la tabla si no existen.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preguntas_respuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta TEXT UNIQUE,
            respuesta TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
def add_question_answer(pregunta: str, respuesta: str, db_path="chatbot.db"):
    #Agrega una nueva pregunta y respuesta a la base de datos.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO preguntas_respuestas (pregunta, respuesta) VALUES (?, ?)", (pregunta, respuesta))
        conn.commit()
    except sqlite3.IntegrityError:
        print("La pregunta ya existe en la base de datos.")
    finally:
        conn.close()
    
def get_all_data(db_path="chatbot.db"):
    #Obtiene todas las preguntas y respuestas de la base de datos.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT pregunta, respuesta FROM preguntas_respuestas")
    data = cursor.fetchall()
    conn.close()
    return data