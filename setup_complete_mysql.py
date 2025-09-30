import mysql.connector

def setup_complete_database():
    try:
        print("🔄 Configurando base de datos MySQL completa...")
        
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
        cursor.execute("USE ong_management")
        
        # Crear todas las tablas
        print("🔄 Creando tablas...")
        
        # Tabla usuarios
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
        print("✅ Tabla usuarios creada")
        
        # Tabla donaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                categoria ENUM('ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES') NOT NULL,
                descripcion TEXT,
                cantidad INT NOT NULL CHECK (cantidad >= 0),
                eliminado BOOLEAN DEFAULT false,
                fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_alta INT,
                fecha_modificacion TIMESTAMP NULL,
                usuario_modificacion INT,
                FOREIGN KEY (usuario_alta) REFERENCES usuarios(id),
                FOREIGN KEY (usuario_modificacion) REFERENCES usuarios(id)
            )
        """)
        print("✅ Tabla donaciones creada")
        
        # Tabla eventos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                descripcion TEXT,
                fecha_evento TIMESTAMP NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabla eventos creada")
        
        # Tabla participantes_evento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participantes_evento (
                evento_id INT,
                usuario_id INT,
                fecha_adhesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (evento_id, usuario_id),
                FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        print("✅ Tabla participantes_evento creada")
        
        # Tabla donaciones_repartidas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donaciones_repartidas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                evento_id INT,
                donacion_id INT,
                cantidad_repartida INT NOT NULL CHECK (cantidad_repartida > 0),
                usuario_registro INT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
                FOREIGN KEY (donacion_id) REFERENCES donaciones(id),
                FOREIGN KEY (usuario_registro) REFERENCES usuarios(id)
            )
        """)
        print("✅ Tabla donaciones_repartidas creada")
        
        # Tabla solicitudes_externas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitudes_externas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                organizacion_solicitante VARCHAR(100) NOT NULL,
                solicitud_id VARCHAR(100) NOT NULL,
                donaciones JSON NOT NULL,
                activa BOOLEAN DEFAULT true,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_solicitud (organizacion_solicitante, solicitud_id)
            )
        """)
        print("✅ Tabla solicitudes_externas creada")
        
        # Tabla eventos_externos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventos_externos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                organizacion_id VARCHAR(100) NOT NULL,
                evento_id VARCHAR(100) NOT NULL,
                nombre VARCHAR(255) NOT NULL,
                descripcion TEXT,
                fecha_evento TIMESTAMP NOT NULL,
                activo BOOLEAN DEFAULT true,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_evento (organizacion_id, evento_id)
            )
        """)
        print("✅ Tabla eventos_externos creada")
        
        # Tabla solicitudes_donaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitudes_donaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                solicitud_id VARCHAR(100) UNIQUE NOT NULL,
                donaciones JSON NOT NULL,
                estado ENUM('ACTIVA', 'DADA_DE_BAJA', 'COMPLETADA') DEFAULT 'ACTIVA',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                usuario_creacion INT,
                usuario_actualizacion INT,
                notas TEXT,
                FOREIGN KEY (usuario_creacion) REFERENCES usuarios(id),
                FOREIGN KEY (usuario_actualizacion) REFERENCES usuarios(id)
            )
        """)
        print("✅ Tabla solicitudes_donaciones creada")
        
        # Insertar datos de prueba
        print("🔄 Insertando datos de prueba...")
        
        # Deshabilitar verificaciones de foreign key temporalmente
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Usuarios
        users = [
            ('admin', 'Juan', 'Pérez', '+54911234567', 'admin@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'PRESIDENTE'),
            ('vocal1', 'María', 'González', '+54911234568', 'maria@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOCAL'),
            ('coord1', 'Carlos', 'López', '+54911234569', 'carlos@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'COORDINADOR'),
            ('vol1', 'Ana', 'Martínez', '+54911234570', 'ana@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOLUNTARIO'),
            ('vol2', 'Pedro', 'Rodríguez', '+54911234571', 'pedro@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOLUNTARIO')
        ]
        
        cursor.execute("DELETE FROM usuarios")  # Limpiar usuarios existentes
        for user in users:
            cursor.execute("""
                INSERT INTO usuarios (nombre_usuario, nombre, apellido, telefono, email, password_hash, rol) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, user)
        print("✅ Usuarios insertados")
        
        # Donaciones
        donations = [
            ('ALIMENTOS', 'Puré de tomates en lata', 50, 1),
            ('ALIMENTOS', 'Arroz blanco 1kg', 25, 1),
            ('ROPA', 'Camisetas talle M', 30, 2),
            ('ROPA', 'Pantalones infantiles', 20, 2),
            ('JUGUETES', 'Pelotas de fútbol', 15, 1),
            ('JUGUETES', 'Muñecas de trapo', 10, 2),
            ('UTILES_ESCOLARES', 'Cuadernos rayados', 100, 1),
            ('UTILES_ESCOLARES', 'Lápices de colores', 50, 2)
        ]
        
        for donation in donations:
            cursor.execute("""
                INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta) 
                VALUES (%s, %s, %s, %s)
            """, donation)
        print("✅ Donaciones insertadas")
        
        # Eventos
        events = [
            ('Entrega de Alimentos - Barrio Norte', 'Distribución de alimentos no perecederos', '2025-01-15 10:00:00'),
            ('Jornada de Juegos - Plaza Central', 'Actividades recreativas para niños', '2025-01-20 14:00:00'),
            ('Entrega de Útiles Escolares', 'Preparación para inicio de clases', '2025-02-01 09:00:00'),
            ('Evento Pasado - Navidad 2024', 'Celebración navideña comunitaria', '2024-12-24 18:00:00')
        ]
        
        for event in events:
            cursor.execute("""
                INSERT INTO eventos (nombre, descripcion, fecha_evento) 
                VALUES (%s, %s, %s)
            """, event)
        print("✅ Eventos insertados")
        
        # Participantes en eventos
        participants = [
            (1, 3), (1, 4), (1, 5),  # Evento 1
            (2, 3), (2, 4),          # Evento 2
            (3, 4), (3, 5),          # Evento 3
            (4, 3), (4, 4), (4, 5)   # Evento 4
        ]
        
        for participant in participants:
            cursor.execute("""
                INSERT INTO participantes_evento (evento_id, usuario_id) 
                VALUES (%s, %s)
            """, participant)
        print("✅ Participantes insertados")
        
        # Donaciones repartidas
        distributed = [
            (4, 1, 10, 3),  # 10 latas de puré en Navidad
            (4, 5, 5, 3),   # 5 pelotas en Navidad
            (4, 6, 3, 4)    # 3 muñecas en Navidad
        ]
        
        for dist in distributed:
            cursor.execute("""
                INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro) 
                VALUES (%s, %s, %s, %s)
            """, dist)
        print("✅ Donaciones repartidas insertadas")
        
        # Rehabilitar verificaciones de foreign key
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        connection.commit()
        
        # Verificar datos
        print("\n📊 Verificando datos insertados:")
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        print(f"👥 Usuarios: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM donaciones")
        print(f"📦 Donaciones: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM eventos")
        print(f"📅 Eventos: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM participantes_evento")
        print(f"👥 Participaciones: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM donaciones_repartidas")
        print(f"📤 Donaciones repartidas: {cursor.fetchone()[0]}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Base de datos MySQL configurada completamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        return False

if __name__ == "__main__":
    setup_complete_database()