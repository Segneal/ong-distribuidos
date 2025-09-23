import psycopg2
import os
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        try:
            # Usar variables de entorno directamente sin dotenv
            connection_string = (
                f"host=localhost "
                f"dbname=ong_management "
                f"user=ong_user "
                f"password=ong_pass "
                f"port=5432"
            )
            
            self.connection = psycopg2.connect(connection_string)
            self.connection.autocommit = False
            print(f"✅ Conexión exitosa a la base de datos")
            return self.connection
        except psycopg2.OperationalError as e:
            print(f"❌ Error de conexión a PostgreSQL: {e}")
            return None
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
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

def get_db_connection():
    return DatabaseConnection()

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