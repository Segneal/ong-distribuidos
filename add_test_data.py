#!/usr/bin/env python3
"""
Script para agregar datos de prueba para vol1 y otros usuarios
"""
import pymysql
from datetime import datetime, timedelta

def add_test_data():
    try:
        # Conectar a la base de datos
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        print("=== AGREGANDO EVENTOS DE PRUEBA ===")
        
        # Crear eventos de prueba en diferentes meses
        eventos_prueba = [
            # Eventos de septiembre 2024 (pasados)
            ("Entrega de Alimentos - Septiembre", "Distribución mensual de alimentos", "2024-09-15 10:00:00"),
            ("Jornada de Juegos - Septiembre", "Actividades recreativas para niños", "2024-09-22 14:00:00"),
            
            # Eventos de octubre 2024 (pasados)
            ("Entrega de Ropa - Octubre", "Distribución de ropa de invierno", "2024-10-10 09:00:00"),
            ("Taller de Manualidades - Octubre", "Taller creativo para la comunidad", "2024-10-25 16:00:00"),
            
            # Eventos de noviembre 2024 (pasados)
            ("Celebración Día del Niño", "Evento especial con juegos y regalos", "2024-11-20 15:00:00"),
            ("Entrega de Útiles - Noviembre", "Preparación para fin de año escolar", "2024-11-30 08:00:00"),
            
            # Eventos de enero 2025 (futuros)
            ("Inicio de Clases 2025", "Entrega de útiles escolares", "2025-01-15 09:00:00"),
            ("Jornada de Salud Comunitaria", "Controles médicos gratuitos", "2025-01-28 10:00:00"),
        ]
        
        evento_ids = []
        for nombre, descripcion, fecha in eventos_prueba:
            cursor.execute("""
                INSERT INTO eventos (nombre, descripcion, fecha_evento, fecha_creacion, fecha_actualizacion)
                VALUES (%s, %s, %s, NOW(), NOW())
            """, (nombre, descripcion, fecha))
            evento_ids.append(cursor.lastrowid)
            print(f"  ✓ Evento creado: {nombre} (ID: {cursor.lastrowid})")
        
        print(f"\n=== AGREGANDO PARTICIPACIONES PARA vol1 (ID: 14) ===")
        
        # vol1 participa en varios eventos
        participaciones_vol1 = [
            evento_ids[0],  # Entrega de Alimentos - Septiembre
            evento_ids[1],  # Jornada de Juegos - Septiembre  
            evento_ids[2],  # Entrega de Ropa - Octubre
            evento_ids[4],  # Celebración Día del Niño
            evento_ids[6],  # Inicio de Clases 2025
        ]
        
        for evento_id in participaciones_vol1:
            cursor.execute("""
                INSERT INTO participantes_evento (evento_id, usuario_id, fecha_adhesion)
                VALUES (%s, %s, NOW())
            """, (evento_id, 14))
            print(f"  ✓ vol1 agregado al evento {evento_id}")
        
        print(f"\n=== AGREGANDO PARTICIPACIONES PARA OTROS USUARIOS ===")
        
        # coord1 (ID: 13) participa en algunos eventos
        participaciones_coord1 = [
            evento_ids[0],  # Entrega de Alimentos - Septiembre
            evento_ids[3],  # Taller de Manualidades - Octubre
            evento_ids[5],  # Entrega de Útiles - Noviembre
            evento_ids[7],  # Jornada de Salud Comunitaria
        ]
        
        for evento_id in participaciones_coord1:
            cursor.execute("""
                INSERT INTO participantes_evento (evento_id, usuario_id, fecha_adhesion)
                VALUES (%s, %s, NOW())
            """, (evento_id, 13))
            print(f"  ✓ coord1 agregado al evento {evento_id}")
        
        # vol2 (ID: 15) participa en algunos eventos
        participaciones_vol2 = [
            evento_ids[1],  # Jornada de Juegos - Septiembre
            evento_ids[2],  # Entrega de Ropa - Octubre
            evento_ids[4],  # Celebración Día del Niño
        ]
        
        for evento_id in participaciones_vol2:
            cursor.execute("""
                INSERT INTO participantes_evento (evento_id, usuario_id, fecha_adhesion)
                VALUES (%s, %s, NOW())
            """, (evento_id, 15))
            print(f"  ✓ vol2 agregado al evento {evento_id}")
        
        print(f"\n=== AGREGANDO DONACIONES REPARTIDAS ===")
        
        # Agregar donaciones repartidas a algunos eventos
        # Evento de Entrega de Alimentos (evento_ids[0]) - con donaciones
        cursor.execute("""
            INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro, fecha_registro)
            VALUES (%s, 2, 10, 14, NOW())
        """, (evento_ids[0],))  # vol1 registra reparto de alimentos
        print(f"  ✓ Donación repartida en evento {evento_ids[0]} (Entrega de Alimentos)")
        
        cursor.execute("""
            INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro, fecha_registro)
            VALUES (%s, 3, 5, 14, NOW())
        """, (evento_ids[0],))  # vol1 registra más reparto
        print(f"  ✓ Otra donación repartida en evento {evento_ids[0]}")
        
        # Evento de Entrega de Ropa (evento_ids[2]) - con donaciones
        cursor.execute("""
            INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro, fecha_registro)
            VALUES (%s, 4, 8, 13, NOW())
        """, (evento_ids[2],))  # coord1 registra reparto de ropa
        print(f"  ✓ Donación repartida en evento {evento_ids[2]} (Entrega de Ropa)")
        
        # Evento Día del Niño (evento_ids[4]) - con donaciones
        cursor.execute("""
            INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro, fecha_registro)
            VALUES (%s, 6, 3, 14, NOW())
        """, (evento_ids[4],))  # vol1 registra reparto de juguetes
        print(f"  ✓ Donación repartida en evento {evento_ids[4]} (Día del Niño)")
        
        # Los otros eventos NO tienen donaciones repartidas (para probar el filtro)
        
        connection.commit()
        print(f"\n✅ DATOS DE PRUEBA AGREGADOS EXITOSAMENTE")
        print(f"📊 Resumen:")
        print(f"  - {len(eventos_prueba)} eventos creados")
        print(f"  - {len(participaciones_vol1)} participaciones para vol1")
        print(f"  - {len(participaciones_coord1)} participaciones para coord1") 
        print(f"  - {len(participaciones_vol2)} participaciones para vol2")
        print(f"  - 4 donaciones repartidas en 3 eventos")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_test_data()