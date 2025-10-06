#!/usr/bin/env python3
"""
Script para debuggear por qué no se ven los eventos de Fundación Esperanza
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def debug_esperanza_events():
    """Debuggear eventos de Fundación Esperanza"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 DEBUGGING EVENTOS DE FUNDACIÓN ESPERANZA")
        print("=" * 50)
        
        # 1. Verificar usuarios de Fundación Esperanza
        print("👥 USUARIOS DE FUNDACIÓN ESPERANZA:")
        cursor.execute("""
            SELECT id, nombre, email, organizacion, rol
            FROM usuarios 
            WHERE organizacion = 'fundacion-esperanza'
        """)
        
        esperanza_users = cursor.fetchall()
        print(f"📊 Total usuarios: {len(esperanza_users)}")
        
        for user in esperanza_users:
            print(f"  👤 ID {user['id']}: {user['nombre']} ({user['email']}) - {user['rol']}")
        
        # 2. Verificar TODOS los eventos en la base de datos
        print(f"\n📅 TODOS LOS EVENTOS EN LA BASE DE DATOS:")
        cursor.execute("""
            SELECT id, nombre, fecha_evento, organizacion, descripcion
            FROM eventos 
            ORDER BY organizacion, fecha_evento DESC
        """)
        
        all_events = cursor.fetchall()
        print(f"📊 Total eventos: {len(all_events)}")
        
        esperanza_events = []
        other_events = []
        
        for event in all_events:
            if event['organizacion'] == 'fundacion-esperanza':
                esperanza_events.append(event)
                print(f"  🏥 ESPERANZA: ID {event['id']} - {event['nombre']} ({event['fecha_evento']})")
            else:
                other_events.append(event)
                print(f"  🏢 {event['organizacion'].upper()}: ID {event['id']} - {event['nombre']} ({event['fecha_evento']})")
        
        print(f"\n📈 RESUMEN POR ORGANIZACIÓN:")
        print(f"  - Fundación Esperanza: {len(esperanza_events)} eventos")
        print(f"  - Otras organizaciones: {len(other_events)} eventos")
        
        # 3. Verificar eventos en la red
        print(f"\n🌐 EVENTOS EN LA RED:")
        cursor.execute("""
            SELECT er.evento_id, e.nombre, e.organizacion, e.fecha_evento
            FROM eventos_red er
            JOIN eventos e ON er.evento_id = e.id
            ORDER BY e.organizacion, e.fecha_evento DESC
        """)
        
        network_events = cursor.fetchall()
        print(f"📊 Total eventos en red: {len(network_events)}")
        
        esperanza_network = []
        other_network = []
        
        for event in network_events:
            if event['organizacion'] == 'fundacion-esperanza':
                esperanza_network.append(event)
                print(f"  🏥 ESPERANZA EN RED: ID {event['evento_id']} - {event['nombre']}")
            else:
                other_network.append(event)
                print(f"  🏢 {event['organizacion'].upper()} EN RED: ID {event['evento_id']} - {event['nombre']}")
        
        print(f"\n📈 RESUMEN RED POR ORGANIZACIÓN:")
        print(f"  - Fundación Esperanza en red: {len(esperanza_network)} eventos")
        print(f"  - Otras organizaciones en red: {len(other_network)} eventos")
        
        # 4. Verificar si hay eventos huérfanos en eventos_red
        print(f"\n🔍 VERIFICANDO EVENTOS HUÉRFANOS EN LA RED:")
        cursor.execute("""
            SELECT er.evento_id
            FROM eventos_red er
            LEFT JOIN eventos e ON er.evento_id = e.id
            WHERE e.id IS NULL
        """)
        
        orphan_events = cursor.fetchall()
        if orphan_events:
            print(f"⚠️  EVENTOS HUÉRFANOS ENCONTRADOS: {len(orphan_events)}")
            for orphan in orphan_events:
                print(f"  🚫 Evento ID {orphan['evento_id']} en eventos_red pero no existe en eventos")
        else:
            print(f"✅ No hay eventos huérfanos en la red")
        
        # 5. Crear un evento de prueba para Fundación Esperanza si no existe
        if len(esperanza_events) == 0:
            print(f"\n🆕 CREANDO EVENTO DE PRUEBA PARA FUNDACIÓN ESPERANZA...")
            
            cursor.execute("""
                INSERT INTO eventos (nombre, descripcion, fecha_evento, ubicacion, organizacion, creado_por)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                "Evento de Prueba - Esperanza",
                "Evento creado para testing del sistema multi-organización",
                "2025-10-06 10:00:00",  # Evento pasado reciente
                "Centro Comunitario Esperanza",
                "fundacion-esperanza",
                esperanza_users[0]['id'] if esperanza_users else 1
            ))
            
            new_event_id = cursor.lastrowid
            print(f"✅ Evento creado con ID: {new_event_id}")
            
            # Exponer en la red
            cursor.execute("""
                INSERT INTO eventos_red (evento_id, organizacion_origen)
                VALUES (%s, %s)
            """, (new_event_id, "fundacion-esperanza"))
            
            print(f"✅ Evento expuesto en la red")
            
            conn.commit()
        
        print(f"\n🎉 DEBUGGING COMPLETADO")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_esperanza_events()