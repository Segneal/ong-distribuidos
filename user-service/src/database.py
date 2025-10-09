import psycopg2
import os
import locale
import sys
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Configurar codificación para Windows
if sys.platform == "win32":
    try:
        # Forzar locale en inglés para evitar problemas con mensajes de error en español
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['LC_ALL'] = 'C'
        os.environ['LANG'] = 'C'
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        try:
            # Configuración de conexión con encoding UTF-8 explícito
            connection_params = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'database': os.getenv('DB_NAME', 'ong_management'),
                'user': os.getenv('DB_USER', 'ong_user'),
                'password': os.getenv('DB_PASSWORD', 'ong_pass'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'connect_timeout': 10,
                'client_encoding': 'UTF8'
            }
            
            # Crear conexión con encoding UTF-8
            self.connection = psycopg2.connect(**connection_params)
            
            # Configurar encoding y opciones adicionales
            self.connection.set_client_encoding('UTF8')
            self.connection.autocommit = False
            
            # Ejecutar comando para asegurar UTF-8
            with self.connection.cursor() as cursor:
                cursor.execute("SET client_encoding TO 'UTF8';")
                cursor.execute("SET standard_conforming_strings = on;")
            
            print(f"✅ Conexión exitosa a la base de datos: {os.getenv('DB_NAME', 'ong_management')}")
            return self.connection
        except psycopg2.OperationalError as e:
            try:
                error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            except:
                error_msg = repr(e)
            print(f"❌ Error de conexión a PostgreSQL: {error_msg}")
            print("💡 Verifica que PostgreSQL esté ejecutándose y las credenciales sean correctas")
            return None
        except UnicodeDecodeError as e:
            print(f"❌ Error de codificación UTF-8: {repr(e)}")
            print("💡 Problema con caracteres especiales en mensajes de PostgreSQL")
            return None
        except Exception as e:
            try:
                error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            except:
                error_msg = repr(e)
            print(f"❌ Error conectando a la base de datos: {error_msg}")
            return None
    
    def get_cursor(self):
        if not self.connection or self.connection.closed:
            if not self.connect():
                return None
        try:
            return self.connection.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"❌ Error obteniendo cursor: {e}")
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
                print(f"✅ PostgreSQL version: {version['version']}")
                cursor.close()
                db.close()
                return True
            except Exception as e:
                print(f"❌ Error ejecutando query de prueba: {e}")
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