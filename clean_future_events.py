#!/usr/bin/env python3
"""
Script para limpiar eventos futuros y dejar solo los eventos pasados
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection
from datetime import datetime

def clean_future_events():
    """Eliminar eventos futuros y dejar solo los pasados"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🧹 LIMPIANDO EVENTOS FUTUROS...")
        print("=" * 50)
        
        # Primero, ver qué eventos tenemos
        cursor.execute("""
            SELECT id, nombre, fecha_evento, organizacion,
                   CASE 
                       WHEN fecha_evento > NOW() THEN 'FUTURO'
                       ELSE 'PASADO'
                   END as estado
            FROM eventos 
            ORDER BY fecha_evento DESC
        """)
        
        all_events = cursor.fetchall()
        
        print(f"📊 EVENTOS ACTUALES ({len(all_events)} total):")
        future_events = []
        past_events = []
        
        for event in all_events:
            if event['estado'] == 'FUTURO':
                future_events.append(event)
                print(f"  🔮 FUTURO: ID {event['id']} - {event['nombre']} ({event['fecha_evento']}) - {event['organizacion']}")
            else:
                past_events.append(event)
                print(f"  📅 PASADO: ID {event['id']} - {event['nombre']} ({event['fecha_evento']}) - {event['organizacion']}")
        
        print(f"\n📈 RESUMEN:")
        print(f"  - Eventos futuros: {len(future_events)}")
        print(f"  - Eventos pasados: {len(past_events)}")
        
        if len(future_events) == 0:
            print("\n✅ No hay eventos futuros para eliminar")
            cursor.close()
            conn.close()
            return
        
        # Eliminar eventos futuros
        print(f"\n🗑️  ELIMINANDO {len(future_events)} EVENTOS FUTUROS...")
        
        future_event_ids = [event['id'] for event in future_events]
        
        # 1. Eliminar participantes de eventos futuros
        if future_event_ids:
            placeholders = ','.join(['%s'] * len(future_event_ids))
            
            cursor.execute(f"""
                DELETE FROM participantes_eventos 
                WHERE evento_id IN ({placeholders})
            """, future_event_ids)
            
            deleted_participants = cursor.rowcount
            print(f"  ✅ Eliminados {deleted_participants} participantes")
            
            # 2. Eliminar donaciones distribuidas de eventos futuros
            cursor.execute(f"""
                DELETE FROM donaciones_distribuidas 
                WHERE evento_id IN ({placeholders})
            """, future_event_ids)
            
            deleted_distributions = cursor.rowcount
            print(f"  ✅ Eliminadas {deleted_distributions} distribuciones de donaciones")
            
            # 3. Eliminar de eventos_red (si están expuestos)
            cursor.execute(f"""
                DELETE FROM eventos_red 
                WHERE evento_id IN ({placeholders})
            """, future_event_ids)
            
            deleted_network = cursor.rowcount
            print(f"  ✅ Eliminados {deleted_network} eventos de la red")
            
            # 4. Eliminar los eventos futuros
            cursor.execute(f"""
                DELETE FROM eventos 
                WHERE id IN ({placeholders})
            """, future_event_ids)
            
            deleted_events = cursor.rowcount
            print(f"  ✅ Eliminados {deleted_events} eventos futuros")
        
        conn.commit()
        
        # Verificar resultado final
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN fecha_evento > NOW() THEN 1 ELSE 0 END) as futuros,
                   SUM(CASE WHEN fecha_evento <= NOW() THEN 1 ELSE 0 END) as pasados
            FROM eventos
        """)
        
        final_count = cursor.fetchone()
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"  - Total eventos: {final_count['total']}")
        print(f"  - Eventos futuros: {final_count['futuros']}")
        print(f"  - Eventos pasados: {final_count['pasados']}")
        
        if final_count['futuros'] == 0:
            print(f"\n🎉 LIMPIEZA COMPLETADA!")
            print(f"✅ Solo quedan {final_count['pasados']} eventos pasados")
        else:
            print(f"\n⚠️  Aún quedan {final_count['futuros']} eventos futuros")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_future_events()