import psycopg2
import os
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'ong_management')
        self.user = os.getenv('DB_USER', 'ong_user')
        self.password = os.getenv('DB_PASSWORD', 'ong_pass')
        self.port = os.getenv('DB_PORT', '5432')
        
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                options='-c client_encoding=UTF8'
            )
            self.connection.autocommit = False
            print(f"✅ Events Service conectado a {self.database}")
            return self.connection
        except Exception as e:
            print(f"❌ Error de conexión en Events Service: {str(e)}")
            return None
    
    def get_cursor(self):
        if not self.connection or self.connection.closed:
            if not self.connect():
                return None
        try:
            return self.connection.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"❌ Error obteniendo cursor: {str(e)}")
            return None
    
    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()

def get_db_connection():
    return DatabaseConnection()