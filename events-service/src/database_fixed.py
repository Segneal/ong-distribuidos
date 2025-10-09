import mysql.connector
import os

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'ong_management')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'root')
        self.port = int(os.getenv('DB_PORT', '3306'))
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            print(f"✅ Events Service conectado a {self.database}")
            return self.connection
        except Exception as e:
            print(f"❌ Error de conexión en Events Service: {str(e)}")
            return None
    
    def get_cursor(self):
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        try:
            return self.connection.cursor(dictionary=True)
        except Exception as e:
            print(f"❌ Error obteniendo cursor: {str(e)}")
            return None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

def get_db_connection():
    return DatabaseConnection()