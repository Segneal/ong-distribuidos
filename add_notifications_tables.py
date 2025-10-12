#!/usr/bin/env python3
"""
Script para agregar las tablas de notificaciones faltantes
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def create_notifications_tables():
    """Crear las tablas de notificaciones"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=== CREANDO TABLAS DE NOTIFICACIONES ===")
        
        # Tabla principal de notificaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notificaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                tipo ENUM('transferencia_recibida', 'transferencia_enviada', 'adhesion_evento', 'solicitud_donacion', 'evento_cancelado', 'inscripcion_procesada') NOT NULL,
                titulo VARCHAR(255) NOT NULL,
                mensaje TEXT NOT NULL,
                datos_adicionales JSON,
                leida BOOLEAN DEFAULT FALSE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_lectura TIMESTAMP NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        print("✅ Tabla 'notificaciones' creada")
        
        # Agregar campo organizacion a usuarios si no existe
        try:
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN organizacion VARCHAR(100) DEFAULT 'empuje-comunitario'
            """)
            print("✅ Campo 'organizacion' agregado a tabla usuarios")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("ℹ️  Campo 'organizacion' ya existe en tabla usuarios")
            else:
                print(f"⚠️  Error agregando campo organizacion: {e}")
        
        # Agregar campo organizacion_propietaria a transferencias_donaciones si no existe
        try:
            cursor.execute("""
                ALTER TABLE transferencias_donaciones 
                ADD COLUMN organizacion_propietaria VARCHAR(100) NOT NULL DEFAULT 'empuje-comunitario'
            """)
            print("✅ Campo 'organizacion_propietaria' agregado a tabla transferencias_donaciones")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("ℹ️  Campo 'organizacion_propietaria' ya existe en tabla transferencias_donaciones")
            else:
                print(f"⚠️  Error agregando campo organizacion_propietaria: {e}")
        
        # Crear índices para notificaciones
        try:
            cursor.execute("CREATE INDEX idx_notificaciones_usuario ON notificaciones(usuario_id)")
        except mysql.connector.Error:
            pass  # Índice ya existe
        
        try:
            cursor.execute("CREATE INDEX idx_notificaciones_tipo ON notificaciones(tipo)")
        except mysql.connector.Error:
            pass  # Índice ya existe
        
        try:
            cursor.execute("CREATE INDEX idx_notificaciones_leida ON notificaciones(leida)")
        except mysql.connector.Error:
            pass  # Índice ya existe
        
        try:
            cursor.execute("CREATE INDEX idx_notificaciones_fecha ON notificaciones(fecha_creacion)")
        except mysql.connector.Error:
            pass  # Índice ya existe
        
        try:
            cursor.execute("CREATE INDEX idx_transferencias_propietaria ON transferencias_donaciones(organizacion_propietaria)")
        except mysql.connector.Error:
            pass  # Índice ya existe
        
        print("✅ Índices creados")
        
        # Actualizar usuarios existentes con organizaciones
        cursor.execute("""
            UPDATE usuarios SET organizacion = 'empuje-comunitario' WHERE organizacion IS NULL OR organizacion = ''
        """)
        
        # Crear usuarios de prueba para otras organizaciones
        cursor.execute("""
            INSERT IGNORE INTO usuarios (nombre_usuario, nombre, apellido, telefono, email, password_hash, rol, organizacion) VALUES
            ('admin_esperanza', 'Laura', 'Fernández', '+54911234572', 'admin@esperanza-social.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'PRESIDENTE', 'esperanza-social'),
            ('coord_esperanza', 'Miguel', 'Torres', '+54911234573', 'coord@esperanza-social.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'COORDINADOR', 'esperanza-social')
        """)
        
        print("✅ Usuarios de prueba para otras organizaciones creados")
        
        # Actualizar transferencias existentes con organizacion_propietaria
        cursor.execute("""
            UPDATE transferencias_donaciones 
            SET organizacion_propietaria = CASE 
                WHEN tipo = 'ENVIADA' THEN 'empuje-comunitario'
                WHEN tipo = 'RECIBIDA' THEN organizacion_contraparte
                ELSE 'empuje-comunitario'
            END
            WHERE organizacion_propietaria = 'empuje-comunitario'
        """)
        
        print("✅ Transferencias actualizadas con organizacion_propietaria")
        
        # Crear algunas notificaciones de prueba
        cursor.execute("""
            INSERT IGNORE INTO notificaciones (usuario_id, tipo, titulo, mensaje, datos_adicionales) VALUES
            (3, 'transferencia_recibida', 'Donación Recibida', 'Has recibido una transferencia de donaciones de Fundación Esperanza', '{"organizacion_origen": "fundacion-esperanza", "cantidad_items": 3}'),
            (1, 'transferencia_enviada', 'Donación Enviada', 'Has enviado donaciones a Centro Comunitario', '{"organizacion_destino": "centro-comunitario", "cantidad_items": 2}')
        """)
        
        print("✅ Notificaciones de prueba creadas")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 TABLAS DE NOTIFICACIONES CREADAS EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_notifications_tables()