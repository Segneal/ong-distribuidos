import mysql.connector
import os

def setup_database():
    try:
        print("🔄 Configurando base de datos MySQL...")
        
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        # Leer el archivo SQL
        with open('database/mysql_schema.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Dividir en comandos individuales
        commands = sql_script.split(';')
        
        print("📊 Ejecutando comandos SQL...")
        
        for i, command in enumerate(commands):
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    if i % 10 == 0:  # Mostrar progreso cada 10 comandos
                        print(f"✅ Ejecutados {i+1}/{len(commands)} comandos")
                except mysql.connector.Error as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Error en comando {i+1}: {e}")
        
        connection.commit()
        print("✅ Base de datos configurada exitosamente!")
        
        # Verificar que los datos se insertaron
        cursor.execute("USE ong_management")
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        user_count = cursor.fetchone()[0]
        print(f"👥 Usuarios creados: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM donaciones")
        donation_count = cursor.fetchone()[0]
        print(f"📦 Donaciones creadas: {donation_count}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        return False

if __name__ == "__main__":
    setup_database()