#!/usr/bin/env python3
"""
Script para configurar MySQL para el messaging-service
"""
import mysql.connector
import sys

def setup_mysql():
    """Configura MySQL para el messaging-service"""
    try:
        # Conectar como root
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            port=3306
        )
        cursor = conn.cursor()
        
        print("✓ Conectado a MySQL como root")
        
        # Crear base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS ong_management")
        print("✓ Base de datos 'ong_management' verificada")
        
        # Crear usuario ong_user si no existe
        try:
            cursor.execute("CREATE USER 'ong_user'@'localhost' IDENTIFIED BY 'ong_pass'")
            print("✓ Usuario 'ong_user' creado")
        except mysql.connector.Error as e:
            if e.errno == 1396:  # User already exists
                print("✓ Usuario 'ong_user' ya existe")
            else:
                raise
        
        # Otorgar permisos
        cursor.execute("GRANT ALL PRIVILEGES ON ong_management.* TO 'ong_user'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        print("✓ Permisos otorgados a 'ong_user'")
        
        # Usar la base de datos
        cursor.execute("USE ong_management")
        
        # Crear tabla de solicitudes de donaciones si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitudes_donaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                solicitud_id VARCHAR(100) UNIQUE NOT NULL,
                donaciones JSON NOT NULL,
                estado ENUM('ACTIVA', 'DADA_DE_BAJA', 'COMPLETADA') DEFAULT 'ACTIVA',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                usuario_creacion INTEGER,
                usuario_actualizacion INTEGER,
                notas TEXT,
                organization_id INTEGER NOT NULL DEFAULT 1
            )
        """)
        print("✓ Tabla 'solicitudes_donaciones' verificada")
        
        # Crear índices
        try:
            cursor.execute("CREATE INDEX idx_solicitudes_donaciones_estado ON solicitudes_donaciones(estado)")
        except mysql.connector.Error:
            pass  # Index might already exist
            
        try:
            cursor.execute("CREATE INDEX idx_solicitudes_donaciones_fecha ON solicitudes_donaciones(fecha_creacion)")
        except mysql.connector.Error:
            pass  # Index might already exist
            
        try:
            cursor.execute("CREATE INDEX idx_solicitudes_donaciones_org ON solicitudes_donaciones(organization_id)")
        except mysql.connector.Error:
            pass  # Index might already exist
        
        print("✓ Índices verificados")
        
        # Verificar que podemos conectar como ong_user
        conn.close()
        
        test_conn = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='ong_user',
            password='ong_pass',
            port=3306
        )
        test_cursor = test_conn.cursor()
        test_cursor.execute("SELECT 1")
        result = test_cursor.fetchone()
        test_conn.close()
        
        if result:
            print("✓ Conexión como 'ong_user' verificada exitosamente")
            return True
        else:
            print("✗ Error al verificar conexión como 'ong_user'")
            return False
            
    except mysql.connector.Error as e:
        print(f"✗ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("Configurando MySQL para messaging-service...")
    if setup_mysql():
        print("\n🎉 Configuración completada exitosamente!")
        print("El messaging-service ahora debería poder conectarse a MySQL.")
    else:
        print("\n❌ Error en la configuración")
        sys.exit(1)