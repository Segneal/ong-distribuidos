#!/usr/bin/env python3
"""
Script para aplicar migración de base de datos directamente
"""

import mysql.connector
from mysql.connector import Error

def apply_migration():
    """Aplicar migración de base de datos"""
    
    try:
        # Conectar usando las mismas credenciales que los servicios
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='ong_management',
            user='root',
            password='admin123',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔄 Aplicando migración de base de datos...")
            
            # 1. Agregar campo organizacion a donaciones
            print("1️⃣ Agregando campo 'organizacion' a tabla donaciones...")
            try:
                cursor.execute("""
                    ALTER TABLE donaciones 
                    ADD COLUMN organizacion VARCHAR(100) DEFAULT 'empuje-comunitario' AFTER cantidad
                """)
                print("✅ Campo agregado a donaciones")
            except Error as e:
                if "Duplicate column name" in str(e):
                    print("ℹ️  Campo 'organizacion' ya existe en donaciones")
                else:
                    print(f"❌ Error agregando campo a donaciones: {e}")
            
            # 2. Agregar campo organizacion a eventos
            print("2️⃣ Agregando campo 'organizacion' a tabla eventos...")
            try:
                cursor.execute("""
                    ALTER TABLE eventos 
                    ADD COLUMN organizacion VARCHAR(100) DEFAULT 'empuje-comunitario' AFTER descripcion
                """)
                print("✅ Campo agregado a eventos")
            except Error as e:
                if "Duplicate column name" in str(e):
                    print("ℹ️  Campo 'organizacion' ya existe en eventos")
                else:
                    print(f"❌ Error agregando campo a eventos: {e}")
            
            # 3. Actualizar datos existentes
            print("3️⃣ Actualizando datos existentes...")
            cursor.execute("""
                UPDATE donaciones 
                SET organizacion = 'empuje-comunitario' 
                WHERE organizacion IS NULL OR organizacion = ''
            """)
            donaciones_updated = cursor.rowcount
            
            cursor.execute("""
                UPDATE eventos 
                SET organizacion = 'empuje-comunitario' 
                WHERE organizacion IS NULL OR organizacion = ''
            """)
            eventos_updated = cursor.rowcount
            
            print(f"✅ {donaciones_updated} donaciones actualizadas")
            print(f"✅ {eventos_updated} eventos actualizados")
            
            # 4. Crear datos de prueba para otras organizaciones
            print("4️⃣ Creando datos de prueba...")
            
            # Donaciones para Fundación Esperanza
            test_donations = [
                ('ALIMENTOS', 'Leche en polvo', 40, 'fundacion-esperanza'),
                ('ROPA', 'Abrigos de invierno', 15, 'fundacion-esperanza'),
                ('JUGUETES', 'Libros infantiles', 25, 'fundacion-esperanza'),
                ('UTILES_ESCOLARES', 'Mochilas escolares', 30, 'ong-solidaria'),
                ('JUGUETES', 'Juegos didácticos', 20, 'ong-solidaria'),
                ('ALIMENTOS', 'Cereales variados', 35, 'ong-solidaria'),
                ('ALIMENTOS', 'Conservas variadas', 50, 'centro-comunitario'),
                ('ROPA', 'Ropa deportiva', 25, 'centro-comunitario')
            ]
            
            for categoria, descripcion, cantidad, organizacion in test_donations:
                try:
                    cursor.execute("""
                        INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta)
                        VALUES (%s, %s, %s, %s, 1)
                    """, (categoria, descripcion, cantidad, organizacion))
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        print(f"Error insertando donación: {e}")
            
            # Eventos para otras organizaciones
            test_events = [
                ('Campaña de Abrigo', 'Distribución de ropa de invierno', 'fundacion-esperanza', '2025-01-25 11:00:00'),
                ('Lectura en el Parque', 'Actividad de lectura para niños', 'fundacion-esperanza', '2025-02-05 16:00:00'),
                ('Preparación Escolar', 'Entrega de útiles escolares', 'ong-solidaria', '2025-01-30 10:00:00'),
                ('Taller de Juegos', 'Actividades lúdicas educativas', 'ong-solidaria', '2025-02-08 14:00:00'),
                ('Jornada Deportiva', 'Actividades deportivas comunitarias', 'centro-comunitario', '2025-02-12 09:00:00')
            ]
            
            for nombre, descripcion, organizacion, fecha in test_events:
                try:
                    cursor.execute("""
                        INSERT INTO eventos (nombre, descripcion, organizacion, fecha_evento)
                        VALUES (%s, %s, %s, %s)
                    """, (nombre, descripcion, organizacion, fecha))
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        print(f"Error insertando evento: {e}")
            
            # Confirmar cambios
            connection.commit()
            
            # 5. Verificar resultados
            print("5️⃣ Verificando resultados...")
            
            cursor.execute("SELECT organizacion, COUNT(*) FROM donaciones GROUP BY organizacion")
            donations_by_org = cursor.fetchall()
            print("\n📦 Donaciones por organización:")
            for org, count in donations_by_org:
                print(f"   - {org}: {count} donaciones")
            
            cursor.execute("SELECT organizacion, COUNT(*) FROM eventos GROUP BY organizacion")
            events_by_org = cursor.fetchall()
            print("\n📅 Eventos por organización:")
            for org, count in events_by_org:
                print(f"   - {org}: {count} eventos")
            
            print("\n🎉 ¡Migración completada exitosamente!")
            
    except Error as e:
        print(f"❌ Error de conexión MySQL: {e}")
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

if __name__ == "__main__":
    print("🚀 APLICANDO MIGRACIÓN DE BASE DE DATOS")
    print("=" * 50)
    apply_migration()