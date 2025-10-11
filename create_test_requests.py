#!/usr/bin/env python3
"""
Script para crear solicitudes de prueba
"""
import mysql.connector
import json
from datetime import datetime

def create_test_requests():
    """Crea solicitudes de prueba"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== CREANDO SOLICITUDES DE PRUEBA ===\n")
        
        # Crear solicitud activa para empuje-comunitario
        solicitud_id_1 = f"req-empuje-comunitario-test-{int(datetime.now().timestamp())}"
        donaciones_1 = [
            {"category": "ROPA", "description": "Ropa de invierno para niños"},
            {"category": "ALIMENTOS", "description": "Alimentos no perecederos"}
        ]
        
        cursor.execute("""
            INSERT INTO solicitudes_donaciones 
            (solicitud_id, donaciones, estado, organization_id, notas, usuario_creacion)
            VALUES (%s, %s, 'ACTIVA', 'empuje-comunitario', 'Solicitud de prueba', 11)
        """, (solicitud_id_1, json.dumps(donaciones_1)))
        
        print(f"✓ Solicitud activa creada: {solicitud_id_1}")
        
        # Crear otra solicitud activa
        solicitud_id_2 = f"req-empuje-comunitario-test2-{int(datetime.now().timestamp())}"
        donaciones_2 = [
            {"category": "UTILES_ESCOLARES", "description": "Útiles escolares para primaria"},
            {"category": "JUGUETES", "description": "Juguetes educativos"}
        ]
        
        cursor.execute("""
            INSERT INTO solicitudes_donaciones 
            (solicitud_id, donaciones, estado, organization_id, notas, usuario_creacion)
            VALUES (%s, %s, 'ACTIVA', 'empuje-comunitario', 'Segunda solicitud de prueba', 11)
        """, (solicitud_id_2, json.dumps(donaciones_2)))
        
        print(f"✓ Segunda solicitud activa creada: {solicitud_id_2}")
        
        # Crear solicitudes externas (de otras organizaciones)
        solicitudes_externas = [
            {
                'org': 'fundacion-esperanza',
                'solicitud_id': f"req-esperanza-{int(datetime.now().timestamp())}",
                'donaciones': [
                    {"category": "ALIMENTOS", "description": "Comida para comedores comunitarios"},
                    {"category": "ROPA", "description": "Ropa para adultos mayores"}
                ]
            },
            {
                'org': 'ong-solidaria',
                'solicitud_id': f"req-solidaria-{int(datetime.now().timestamp())}",
                'donaciones': [
                    {"category": "JUGUETES", "description": "Juguetes para navidad"},
                    {"category": "UTILES_ESCOLARES", "description": "Mochilas y cuadernos"}
                ]
            }
        ]
        
        for solicitud in solicitudes_externas:
            # Verificar si la tabla solicitudes_externas tiene la columna 'estado'
            cursor.execute("SHOW COLUMNS FROM solicitudes_externas LIKE 'estado'")
            has_estado = cursor.fetchone() is not None
            
            if has_estado:
                cursor.execute("""
                    INSERT INTO solicitudes_externas 
                    (organizacion_solicitante, solicitud_id, donaciones, estado)
                    VALUES (%s, %s, %s, 'ACTIVA')
                """, (solicitud['org'], solicitud['solicitud_id'], json.dumps(solicitud['donaciones'])))
            else:
                cursor.execute("""
                    INSERT INTO solicitudes_externas 
                    (organizacion_solicitante, solicitud_id, donaciones, activa)
                    VALUES (%s, %s, %s, 1)
                """, (solicitud['org'], solicitud['solicitud_id'], json.dumps(solicitud['donaciones'])))
            
            print(f"✓ Solicitud externa creada: {solicitud['solicitud_id']} de {solicitud['org']}")
        
        # Verificar el resultado
        print("\n=== VERIFICANDO SOLICITUDES CREADAS ===")
        
        # Solicitudes propias activas
        cursor.execute("""
            SELECT COUNT(*) FROM solicitudes_donaciones 
            WHERE estado = 'ACTIVA' AND organization_id = 'empuje-comunitario'
        """)
        count_own = cursor.fetchone()[0]
        print(f"✓ Solicitudes propias activas: {count_own}")
        
        # Solicitudes externas
        cursor.execute("SELECT COUNT(*) FROM solicitudes_externas WHERE activa = 1")
        count_external = cursor.fetchone()[0]
        print(f"✓ Solicitudes externas activas: {count_external}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    create_test_requests()