#!/usr/bin/env python3
import mysql.connector

def check_users_table():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        # Verificar estructura de usuarios
        print("Estructura de tabla usuarios:")
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} - {col[1]} - {col[2]} - {col[3]}")
        
        # Mostrar algunos usuarios existentes
        print("\nUsuarios existentes:")
        cursor.execute("SELECT id, name, lastName, email, role, organizacion FROM usuarios LIMIT 5")
        users = cursor.fetchall()
        for user in users:
            print(f"  ID: {user[0]}, Nombre: {user[1]} {user[2]}, Email: {user[3]}, Rol: {user[4]}, Org: {user[5]}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    check_users_table()