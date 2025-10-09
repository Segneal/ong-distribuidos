#!/usr/bin/env python3
"""
Script simple para limpiar eventos futuros
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def clean_future_events_simple():
    """Eliminar solo eventos futuros de forma simple"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🧹 LIMPIANDO EVENTOS FUTUROS (SIMPLE)...")
        print("=" * 50)
        
        # Ver eventos futuros
        cursor.execute("""
            SELECT id, nombre, fecha_evento, organizacion
            FROM eventos 
            WHERE fecha_evento > NOW()
            ORDER BY fecha_evento
        """)
        
        future_events = cursor.fetchall()
        
        print(f"📊 EVENTOS FUTUROS A ELIMINAR ({len(future_events)}):")
        for event in future_events:
            print(f"  🔮 ID {event['id']}: {event['nombre']} ({event['fecha_evento']}) - {event['organizacion']}")
        
        if len(future_events) == 0:
            print("\n✅ No hay eventos futuros para eliminar")
            cursor.close()
            conn.close()
            return
        
        # Eliminar de eventos_red primero (si existe)
        try:
            future_event_ids = [event['id'] for event in future_events]
            placeholders = ','.join(['%s'] * len(future_event_ids))
            
            cursor.execute(f"""
                DELETE FROM eventos_red 
                WHERE evento_id IN ({placeholders})
            """, future_event_ids)
            
            deleted_network = cursor.rowcount
            print(f"\n🗑️  Eliminados {deleted_network} eventos de la red")
            
        except Exception as e:
            print(f"⚠️  Error eliminando de eventos_red (puede no existir): {e}")
        
        # Eliminar eventos futuros
        cursor.execute("""
            DELETE FROM eventos 
            WHERE fecha_evento > NOW()
        """)
        
        deleted_events = cursor.rowcount
        print(f"🗑️  Eliminados {deleted_events} eventos futuros")
        
        conn.commit()
        
        # Verificar resultado
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
        
        print(f"\n🎉 LIMPIEZA COMPLETADA!")
        print(f"✅ Base limpia para probar sistema multi-organización")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_future_events_simple()