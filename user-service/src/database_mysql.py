import mysql.connector
import os
import sys
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        try:
            # Configuración de conexión MySQL
            connection_params = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'database': os.getenv('DB_NAME', 'ong_management'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'port': int(os.getenv('DB_PORT', '3306')),
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': False
            }
            
            print(f"🔄 Conectando a MySQL...")
            print(f"📡 Host: {connection_params['host']}:{connection_params['port']}")
            print(f"🗄️  Base de datos: {connection_params['database']}")
            
            # Crear conexión
            self.connection = mysql.connector.connect(**connection_params)
            
            # Probar la conexión
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            print(f"✅ Conexión exitosa a MySQL: {os.getenv('DB_NAME', 'ong_management')}")
            return self.connection
            
        except mysql.connector.Error as e:
            print(f"❌ Error de conexión a MySQL: {e}")
            print("💡 Verifica que MySQL esté ejecutándose y las credenciales sean correctas")
            return None
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            return None
    
    def get_cursor(self):
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        try:
            return self.connection.cursor(dictionary=True)
        except Exception as e:
            print(f"❌ Error obteniendo cursor: {e}")
            return None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Conexión a MySQL cerrada")

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
                cursor.execute("SELECT VERSION() as version")
                version = cursor.fetchone()
                print(f"✅ MySQL version: {version['version']}")
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