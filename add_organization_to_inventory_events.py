#!/usr/bin/env python3
"""
Script para agregar el campo 'organizacion' a las tablas de donaciones y eventos
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            database=os.getenv('DB_NAME', 'ong_management'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def add_organization_fields():
    """Agregar campos de organización a donaciones y eventos"""
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        print("🔄 Agregando campo 'organizacion' a tabla donaciones...")
        
        # Verificar si el campo ya existe en donaciones
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'ong_management' 
            AND TABLE_NAME = 'donaciones' 
            AND COLUMN_NAME = 'organizacion'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Agregar campo organizacion a donaciones
            cursor.execute("""
                ALTER TABLE donaciones 
                ADD COLUMN organizacion VARCHAR(100) DEFAULT 'empuje-comunitario' AFTER cantidad
            """)
            print("✅ Campo 'organizacion' agregado a tabla donaciones")
        else:
            print("ℹ️  Campo 'organizacion' ya existe en tabla donaciones")
        
        print("🔄 Agregando campo 'organizacion' a tabla eventos...")
        
        # Verificar si el campo ya existe en eventos
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'ong_management' 
            AND TABLE_NAME = 'eventos' 
            AND COLUMN_NAME = 'organizacion'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Agregar campo organizacion a eventos
            cursor.execute("""
                ALTER TABLE eventos 
                ADD COLUMN organizacion VARCHAR(100) DEFAULT 'empuje-comunitario' AFTER descripcion
            """)
            print("✅ Campo 'organizacion' agregado a tabla eventos")
        else:
            print("ℹ️  Campo 'organizacion' ya existe en tabla eventos")
        
        # Confirmar cambios
        connection.commit()
        
        print("\n📊 Verificando estructura de tablas...")
        
        # Verificar donaciones
        cursor.execute("DESCRIBE donaciones")
        donaciones_columns = cursor.fetchall()
        print("\n🗃️  Tabla donaciones:")
        for column in donaciones_columns:
            if 'organizacion' in column[0]:
                print(f"   ✅ {column[0]} - {column[1]}")
        
        # Verificar eventos
        cursor.execute("DESCRIBE eventos")
        eventos_columns = cursor.fetchall()
        print("\n🗃️  Tabla eventos:")
        for column in eventos_columns:
            if 'organizacion' in column[0]:
                print(f"   ✅ {column[0]} - {column[1]}")
        
        return True
        
    except Error as e:
        print(f"❌ Error ejecutando migración: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_existing_data():
    """Actualizar datos existentes con organizaciones"""
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        print("\n🔄 Actualizando datos existentes...")
        
        # Actualizar donaciones existentes
        cursor.execute("""
            UPDATE donaciones 
            SET organizacion = 'empuje-comunitario' 
            WHERE organizacion IS NULL OR organizacion = ''
        """)
        donaciones_updated = cursor.rowcount
        print(f"✅ {donaciones_updated} donaciones actualizadas con organización")
        
        # Actualizar eventos existentes
        cursor.execute("""
            UPDATE eventos 
            SET organizacion = 'empuje-comunitario' 
            WHERE organizacion IS NULL OR organizacion = ''
        """)
        eventos_updated = cursor.rowcount
        print(f"✅ {eventos_updated} eventos actualizados con organización")
        
        # Confirmar cambios
        connection.commit()
        
        return True
        
    except Error as e:
        print(f"❌ Error actualizando datos: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_test_data_for_other_orgs():
    """Crear datos de prueba para otras organizaciones"""
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        print("\n🔄 Creando datos de prueba para otras organizaciones...")
        
        # Datos para Fundación Esperanza
        esperanza_donations = [
            ('ALIMENTOS', 'Leche en polvo', 40, 'fundacion-esperanza'),
            ('ROPA', 'Abrigos de invierno', 15, 'fundacion-esperanza'),
            ('JUGUETES', 'Libros infantiles', 25, 'fundacion-esperanza')
        ]
        
        esperanza_events = [
            ('Campaña de Abrigo', 'Distribución de ropa de invierno', 'fundacion-esperanza', '2025-01-25 11:00:00'),
            ('Lectura en el Parque', 'Actividad de lectura para niños', 'fundacion-esperanza', '2025-02-05 16:00:00')
        ]
        
        # Datos para ONG Solidaria
        solidaria_donations = [
            ('UTILES_ESCOLARES', 'Mochilas escolares', 30, 'ong-solidaria'),
            ('JUGUETES', 'Juegos didácticos', 20, 'ong-solidaria'),
            ('ALIMENTOS', 'Cereales variados', 35, 'ong-solidaria')
        ]
        
        solidaria_events = [
            ('Preparación Escolar', 'Entrega de útiles escolares', 'ong-solidaria', '2025-01-30 10:00:00'),
            ('Taller de Juegos', 'Actividades lúdicas educativas', 'ong-solidaria', '2025-02-08 14:00:00')
        ]
        
        # Insertar donaciones
        for desc, cat, qty, org in esperanza_donations + solidaria_donations:
            cursor.execute("""
                INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta)
                VALUES (%s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE cantidad = VALUES(cantidad)
            """, (cat, desc, qty, org))
        
        # Insertar eventos
        for name, desc, org, date in esperanza_events + solidaria_events:
            cursor.execute("""
                INSERT INTO eventos (nombre, descripcion, organizacion, fecha_evento)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion)
            """, (name, desc, org, date))
        
        connection.commit()
        
        print(f"✅ Datos de prueba creados para otras organizaciones")
        
        # Mostrar resumen
        cursor.execute("SELECT organizacion, COUNT(*) FROM donaciones GROUP BY organizacion")
        donations_by_org = cursor.fetchall()
        print("\n📊 Donaciones por organización:")
        for org, count in donations_by_org:
            print(f"   - {org}: {count} donaciones")
        
        cursor.execute("SELECT organizacion, COUNT(*) FROM eventos GROUP BY organizacion")
        events_by_org = cursor.fetchall()
        print("\n📊 Eventos por organización:")
        for org, count in events_by_org:
            print(f"   - {org}: {count} eventos")
        
        return True
        
    except Error as e:
        print(f"❌ Error creando datos de prueba: {e}")
        connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    """Función principal"""
    print("🚀 MIGRACIÓN: Agregando soporte multi-organización a inventario y eventos")
    print("=" * 70)
    
    # Paso 1: Agregar campos de organización
    if not add_organization_fields():
        print("❌ Error agregando campos de organización")
        return
    
    # Paso 2: Actualizar datos existentes
    if not update_existing_data():
        print("❌ Error actualizando datos existentes")
        return
    
    # Paso 3: Crear datos de prueba
    if not create_test_data_for_other_orgs():
        print("❌ Error creando datos de prueba")
        return
    
    print("\n🎉 ¡Migración completada exitosamente!")
    print("✅ Inventario y eventos ahora soportan multi-organización")

if __name__ == "__main__":
    main()