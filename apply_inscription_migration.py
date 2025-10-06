#!/usr/bin/env python3
"""
Script para aplicar la migración de solicitudes de inscripción
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def apply_inscription_migration():
    """Aplicar migración para solicitudes de inscripción"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor()
        
        print("🔧 APLICANDO MIGRACIÓN DE SOLICITUDES DE INSCRIPCIÓN")
        print("=" * 55)
        
        # Leer el archivo de migración
        with open('database/inscription_requests_migration.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Ejecutar el SQL completo usando multi=True
        print(f"📝 Ejecutando migración completa...")
        try:
            results = cursor.execute(migration_sql, multi=True)
            for result in results:
                if result.with_rows:
                    result.fetchall()
            print(f"✅ Migración ejecutada exitosamente")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"⚠️  Algunas tablas ya existen, continuando...")
            else:
                print(f"❌ Error en migración: {e}")
                # Intentar crear las tablas individualmente
                print("🔄 Intentando crear tablas individualmente...")
                
                # Crear tabla solicitudes_inscripcion
                try:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS solicitudes_inscripcion (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            solicitud_id VARCHAR(100) UNIQUE NOT NULL,
                            nombre VARCHAR(100) NOT NULL,
                            apellido VARCHAR(100) NOT NULL,
                            email VARCHAR(255) NOT NULL,
                            telefono VARCHAR(20),
                            organizacion_destino VARCHAR(100) NOT NULL,
                            rol_solicitado ENUM('COORDINADOR', 'VOLUNTARIO') NOT NULL,
                            mensaje TEXT,
                            estado ENUM('PENDIENTE', 'APROBADA', 'DENEGADA') DEFAULT 'PENDIENTE',
                            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            fecha_respuesta TIMESTAMP NULL,
                            usuario_revisor INT NULL,
                            comentarios_revisor TEXT,
                            datos_adicionales JSON,
                            FOREIGN KEY (usuario_revisor) REFERENCES usuarios(id),
                            INDEX idx_organizacion_estado (organizacion_destino, estado),
                            INDEX idx_fecha_solicitud (fecha_solicitud),
                            INDEX idx_estado (estado)
                        )
                    """)
                    print("✅ Tabla solicitudes_inscripcion creada")
                except Exception as e2:
                    print(f"⚠️  Error creando solicitudes_inscripcion: {e2}")
                
                # Crear tabla notificaciones_solicitudes
                try:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS notificaciones_solicitudes (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            solicitud_id VARCHAR(100) NOT NULL,
                            usuario_destinatario INT NOT NULL,
                            tipo_notificacion ENUM('NUEVA_SOLICITUD', 'SOLICITUD_APROBADA', 'SOLICITUD_DENEGADA') NOT NULL,
                            leida BOOLEAN DEFAULT FALSE,
                            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (usuario_destinatario) REFERENCES usuarios(id),
                            INDEX idx_usuario_leida (usuario_destinatario, leida),
                            INDEX idx_fecha_creacion (fecha_creacion)
                        )
                    """)
                    print("✅ Tabla notificaciones_solicitudes creada")
                except Exception as e3:
                    print(f"⚠️  Error creando notificaciones_solicitudes: {e3}")
                
                # Insertar datos de prueba
                try:
                    cursor.execute("""
                        INSERT IGNORE INTO solicitudes_inscripcion (
                            solicitud_id, nombre, apellido, email, telefono, 
                            organizacion_destino, rol_solicitado, mensaje
                        ) VALUES 
                        ('INS-2025-001', 'Roberto', 'García', 'roberto.garcia@email.com', '+54911111111',
                         'empuje-comunitario', 'VOLUNTARIO', 'Me gustaría colaborar con la organización en actividades comunitarias'),
                        ('INS-2025-002', 'Laura', 'Fernández', 'laura.fernandez@email.com', '+54922222222',
                         'fundacion-esperanza', 'COORDINADOR', 'Tengo experiencia en gestión de proyectos sociales y me interesa coordinar actividades'),
                        ('INS-2025-003', 'Miguel', 'Torres', 'miguel.torres@email.com', '+54933333333',
                         'empuje-comunitario', 'VOLUNTARIO', 'Quiero ayudar en eventos y distribución de donaciones')
                    """)
                    print("✅ Datos de prueba insertados")
                except Exception as e4:
                    print(f"⚠️  Error insertando datos de prueba: {e4}")
        
        conn.commit()
        
        # Verificar que las tablas se crearon
        cursor.execute("SHOW TABLES LIKE 'solicitudes_inscripcion'")
        if cursor.fetchone():
            print("✅ Tabla solicitudes_inscripcion creada")
        
        cursor.execute("SHOW TABLES LIKE 'notificaciones_solicitudes'")
        if cursor.fetchone():
            print("✅ Tabla notificaciones_solicitudes creada")
        
        # Verificar datos de prueba
        cursor.execute("SELECT COUNT(*) as total FROM solicitudes_inscripcion")
        result = cursor.fetchone()
        print(f"📊 Solicitudes de prueba insertadas: {result[0]}")
        
        print(f"\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error aplicando migración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    apply_inscription_migration()