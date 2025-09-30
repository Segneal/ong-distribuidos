import psycopg2
import os
import sys
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Configurar encoding para evitar problemas con mensajes de error en español
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['LC_ALL'] = 'C'
    os.environ['LANG'] = 'C'

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Configuración de conexión
                connection_params = {
                    'host': os.getenv('DB_HOST', 'localhost'),
                    'database': os.getenv('DB_NAME', 'ong_management'),
                    'user': os.getenv('DB_USER', 'ong_user'),
                    'password': os.getenv('DB_PASSWORD', 'ong_pass'),
                    'port': int(os.getenv('DB_PORT', '5432')),
                    'connect_timeout': 10
                }
                
                print(f"🔄 Intento {retry_count + 1}/{max_retries} - Conectando a PostgreSQL...")
                
                # Crear conexión
                self.connection = psycopg2.connect(**connection_params)
                self.connection.autocommit = False
                
                # Probar la conexión con una query simple
                with self.connection.cursor() as test_cursor:
                    test_cursor.execute("SELECT 1;")
                    test_cursor.fetchone()
                
                print(f"✅ Conexión exitosa a la base de datos: {os.getenv('DB_NAME', 'ong_management')}")
                return self.connection
                
            except UnicodeDecodeError as e:
                print(f"❌ Error de codificación UTF-8 (intento {retry_count + 1}): {repr(e)}")
                print("💡 Problema con caracteres especiales en mensajes de PostgreSQL")
                retry_count += 1
                if retry_count >= max_retries:
                    print("❌ Máximo número de reintentos alcanzado")
                    return None
                    
            except psycopg2.OperationalError as e:
                error_str = repr(e)  # Usar repr para evitar problemas de encoding
                print(f"❌ Error de conexión a PostgreSQL (intento {retry_count + 1}): {error_str}")
                retry_count += 1
                if retry_count >= max_retries:
                    print("❌ Máximo número de reintentos alcanzado")
                    print("💡 Verifica que PostgreSQL esté ejecutándose y las credenciales sean correctas")
                    return None
                    
            except Exception as e:
                error_str = repr(e)
                print(f"❌ Error conectando a la base de datos (intento {retry_count + 1}): {error_str}")
                retry_count += 1
                if retry_count >= max_retries:
                    print("❌ Máximo número de reintentos alcanzado")
                    return None
        
        return None
    
    def get_cursor(self):
        if not self.connection or self.connection.closed:
            if not self.connect():
                return None
        try:
            return self.connection.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"❌ Error obteniendo cursor: {repr(e)}")
            return None
    
    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("🔒 Conexión a la base de datos cerrada")

def get_db_connection():
    return DatabaseConnection()

# Función para probar la conexión
def test_connection():
    """Prueba la conexión a la base de datos"""
    db = get_db_connection()
    conn = db.connect()
    if conn:
        cursor = db.get_cursor()
        if cursor:
            try:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✅ PostgreSQL version: {version['version'][:50]}...")
                cursor.close()
                db.close()
                return True
            except Exception as e:
                print(f"❌ Error ejecutando query de prueba: {repr(e)}")
                cursor.close()
                db.close()
                return False
        else:
            print("❌ No se pudo obtener cursor")
            db.close()
            return False
    else:
        print("❌ No se pudo conectar a la base de datos")
        return False