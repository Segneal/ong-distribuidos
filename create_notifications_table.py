#!/usr/bin/env python3
import mysql.connector

def create_notifications_table():
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
        
        # Crear tabla de notificaciones
        create_table_query = """
        CREATE TABLE IF NOT EXISTS notificaciones_usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            mensaje TEXT NOT NULL,
            tipo ENUM('EVENT_CANCELLED', 'EVENT_UPDATED', 'DONATION_RECEIVED', 'GENERAL') DEFAULT 'GENERAL',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_leida TIMESTAMP NULL,
            leida BOOLEAN DEFAULT false,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
        """
        
        cursor.execute(create_table_query)
        print("✓ Tabla notificaciones_usuarios creada")
        
        # Crear índices
        indices = [
            "CREATE INDEX idx_notificaciones_usuario ON notificaciones_usuarios(usuario_id)",
            "CREATE INDEX idx_notificaciones_leida ON notificaciones_usuarios(leida)",
            "CREATE INDEX idx_notificaciones_fecha ON notificaciones_usuarios(fecha_creacion)",
            "CREATE INDEX idx_notificaciones_tipo ON notificaciones_usuarios(tipo)"
        ]
        
        for index_query in indices:
            try:
                cursor.execute(index_query)
                print(f"✓ Índice creado")
            except mysql.connector.Error as err:
                if "Duplicate key name" in str(err):
                    print(f"⚠ Índice ya existe")
                else:
                    print(f"❌ Error creando índice: {err}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✅ Tabla de notificaciones configurada exitosamente")
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    create_notifications_table()