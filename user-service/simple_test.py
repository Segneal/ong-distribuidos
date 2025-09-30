import psycopg2
import os

# Configurar variables de entorno para forzar inglés
os.environ['LC_ALL'] = 'C'
os.environ['LANG'] = 'C'

try:
    # Conexión simple
    conn = psycopg2.connect(
        host='localhost',
        database='ong_management', 
        user='ong_user',
        password='ong_pass',
        port=5432
    )
    print("Conexion exitosa!")
    conn.close()
except Exception as e:
    print(f"Error: {repr(e)}")