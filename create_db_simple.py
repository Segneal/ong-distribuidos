import mysql.connector

def create_database():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        # Crear base de datos
        print("🔄 Creando base de datos...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS ong_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Base de datos 'ong_management' creada")
        
        # Usar la base de datos
        cursor.execute("USE ong_management")
        
        # Crear tabla de usuarios
        print("🔄 Creando tabla usuarios...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                telefono VARCHAR(20),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol ENUM('PRESIDENTE', 'VOCAL', 'COORDINADOR', 'VOLUNTARIO') NOT NULL,
                activo BOOLEAN DEFAULT true,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar usuarios de prueba
        print("🔄 Insertando usuarios de prueba...")
        users = [
            ('admin', 'Juan', 'Pérez', '+54911234567', 'admin@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'PRESIDENTE'),
            ('vocal1', 'María', 'González', '+54911234568', 'maria@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOCAL'),
            ('coord1', 'Carlos', 'López', '+54911234569', 'carlos@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'COORDINADOR'),
            ('vol1', 'Ana', 'Martínez', '+54911234570', 'ana@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOLUNTARIO'),
            ('vol2', 'Pedro', 'Rodríguez', '+54911234571', 'pedro@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOLUNTARIO')
        ]
        
        for user in users:
            try:
                cursor.execute("""
                    INSERT INTO usuarios (nombre_usuario, nombre, apellido, telefono, email, password_hash, rol) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, user)
            except mysql.connector.IntegrityError:
                print(f"⚠️  Usuario {user[0]} ya existe, saltando...")
        
        connection.commit()
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f"✅ {count} usuarios en la base de datos")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_database()