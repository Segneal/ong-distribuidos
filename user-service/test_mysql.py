import mysql.connector
import os

def test_mysql_connection():
    try:
        print("🔍 Probando conexión a MySQL...")
        
        # Intentar diferentes configuraciones
        configs = [
            {'host': 'localhost', 'user': 'root', 'password': '', 'port': 3306},
            {'host': 'localhost', 'user': 'root', 'password': 'root', 'port': 3306},
            {'host': 'localhost', 'user': 'root', 'password': 'admin', 'port': 3306},
            {'host': 'localhost', 'user': 'root', 'password': '123456', 'port': 3306},
        ]
        
        connection = None
        for i, config in enumerate(configs):
            try:
                print(f"🔄 Probando configuración {i+1}: user={config['user']}, password={'***' if config['password'] else '(vacío)'}")
                connection = mysql.connector.connect(**config)
                print(f"✅ Conexión exitosa con configuración {i+1}!")
                break
            except mysql.connector.Error as e:
                print(f"❌ Configuración {i+1} falló: {e}")
                continue
        
        if not connection:
            print("❌ No se pudo conectar con ninguna configuración")
            return False
        
        print("✅ Conexión exitosa a MySQL!")
        
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()
        
        print("📊 Bases de datos disponibles:")
        for db in databases:
            print(f"  - {db[0]}")
        
        # Verificar si existe la base de datos ong_management
        cursor.execute("SHOW DATABASES LIKE 'ong_management';")
        result = cursor.fetchone()
        
        if result:
            print("✅ Base de datos 'ong_management' encontrada")
        else:
            print("⚠️  Base de datos 'ong_management' no encontrada")
            print("💡 Necesitas ejecutar el script mysql_schema.sql")
        
        cursor.close()
        connection.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_mysql_connection()