import sqlite3

# Conectar a la base de datos (se crea si no existe)
conn = sqlite3.connect('chatbot.db')
cursor = conn.cursor()

# Crear la tabla 'contexto'
cursor.execute('''
CREATE TABLE IF NOT EXISTS contexto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL
);
''')

# Crear la tabla 'links'
cursor.execute('''
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contexto_id INTEGER,
    texto TEXT NOT NULL,
    url TEXT NOT NULL,
    FOREIGN KEY (contexto_id) REFERENCES contexto(id)
);
''')

# Crear la tabla 'interacciones'
cursor.execute('''
CREATE TABLE IF NOT EXISTS interacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Base de datos y tablas creadas correctamente.")