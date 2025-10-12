#!/usr/bin/env python3
"""
Script para probar el sistema de aprobación de adhesiones
"""

import mysql.connector
import json
from datetime import datetime

def test_adhesion_system():
    """Probar el sistema de aprobación de adhesiones"""
    
    # Configuración de la base de datos
    config = {
        'host': 'localhost',
        'database': 'ong_management',
        'user': 'root',
        'password': 'root',
        'port': 3306,
        'charset': 'utf8mb4'
    }
    
    try:
        print("=== Prueba del Sistema de Aprobación de Adhesiones ===")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar estructura de la tabla
        print("\n1. Verificando estructura de la tabla...")
        cursor.execute("DESCRIBE adhesiones_eventos_externos")
        columns = cursor.fetchall()
        
        print("Columnas de la tabla adhesiones_eventos_externos:")
        for col in columns:
            print(f"  - {col['Field']}: {col['Type']} ({col['Null']}, {col['Default']})")
        
        # 2. Crear una adhesión de prueba en estado PENDIENTE
        print("\n2. Creando adhesión de prueba...")
        
        volunteer_data = {
            "name": "Juan",
            "surname": "Pérez",
            "email": "juan.perez@test.com",
            "phone": "123456789"
        }
        
        cursor.execute("""
            INSERT INTO adhesiones_eventos_externos 
            (evento_externo_id, voluntario_id, estado, datos_voluntario)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            estado = 'PENDIENTE', fecha_adhesion = NOW()
        """, (1, 1, 'PENDIENTE', json.dumps(volunteer_data)))
        
        adhesion_id = cursor.lastrowid or 1
        connection.commit()
        print(f"✓ Adhesión creada con ID: {adhesion_id}")
        
        # 3. Verificar que la adhesión está en estado PENDIENTE
        print("\n3. Verificando estado inicial...")
        cursor.execute("""
            SELECT id, estado, fecha_adhesion, fecha_aprobacion, motivo_rechazo
            FROM adhesiones_eventos_externos 
            WHERE id = %s
        """, (adhesion_id,))
        
        adhesion = cursor.fetchone()
        if adhesion:
            print(f"✓ Adhesión {adhesion['id']}: Estado = {adhesion['estado']}")
            print(f"  Fecha adhesión: {adhesion['fecha_adhesion']}")
            print(f"  Fecha aprobación: {adhesion['fecha_aprobacion']}")
        
        # 4. Aprobar la adhesión
        print("\n4. Aprobando adhesión...")
        cursor.execute("""
            UPDATE adhesiones_eventos_externos 
            SET estado = 'CONFIRMADA', fecha_aprobacion = NOW()
            WHERE id = %s
        """, (adhesion_id,))
        connection.commit()
        
        # Verificar aprobación
        cursor.execute("""
            SELECT id, estado, fecha_adhesion, fecha_aprobacion
            FROM adhesiones_eventos_externos 
            WHERE id = %s
        """, (adhesion_id,))
        
        adhesion = cursor.fetchone()
        if adhesion:
            print(f"✓ Adhesión aprobada: Estado = {adhesion['estado']}")
            print(f"  Fecha aprobación: {adhesion['fecha_aprobacion']}")
        
        # 5. Crear otra adhesión para probar rechazo
        print("\n5. Creando segunda adhesión para probar rechazo...")
        cursor.execute("""
            INSERT INTO adhesiones_eventos_externos 
            (evento_externo_id, voluntario_id, estado, datos_voluntario)
            VALUES (%s, %s, %s, %s)
        """, (2, 2, 'PENDIENTE', json.dumps(volunteer_data)))
        
        adhesion_id_2 = cursor.lastrowid
        connection.commit()
        print(f"✓ Segunda adhesión creada con ID: {adhesion_id_2}")
        
        # 6. Rechazar la segunda adhesión
        print("\n6. Rechazando segunda adhesión...")
        cursor.execute("""
            UPDATE adhesiones_eventos_externos 
            SET estado = 'RECHAZADA', fecha_aprobacion = NOW(), motivo_rechazo = %s
            WHERE id = %s
        """, ("Evento completo", adhesion_id_2))
        connection.commit()
        
        # Verificar rechazo
        cursor.execute("""
            SELECT id, estado, fecha_aprobacion, motivo_rechazo
            FROM adhesiones_eventos_externos 
            WHERE id = %s
        """, (adhesion_id_2,))
        
        adhesion = cursor.fetchone()
        if adhesion:
            print(f"✓ Adhesión rechazada: Estado = {adhesion['estado']}")
            print(f"  Motivo: {adhesion['motivo_rechazo']}")
            print(f"  Fecha procesamiento: {adhesion['fecha_aprobacion']}")
        
        # 7. Mostrar resumen de todas las adhesiones
        print("\n7. Resumen de todas las adhesiones:")
        cursor.execute("""
            SELECT id, evento_externo_id, voluntario_id, estado, 
                   fecha_adhesion, fecha_aprobacion, motivo_rechazo
            FROM adhesiones_eventos_externos 
            ORDER BY fecha_adhesion DESC
            LIMIT 10
        """)
        
        adhesions = cursor.fetchall()
        for adh in adhesions:
            print(f"  ID {adh['id']}: Evento {adh['evento_externo_id']}, "
                  f"Voluntario {adh['voluntario_id']}, Estado: {adh['estado']}")
            if adh['motivo_rechazo']:
                print(f"    Motivo rechazo: {adh['motivo_rechazo']}")
        
        print("\n✅ Prueba del sistema de aprobación completada exitosamente!")
        return True
        
    except mysql.connector.Error as e:
        print(f"Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_adhesion_system()