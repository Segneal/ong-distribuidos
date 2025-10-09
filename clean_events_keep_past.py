#!/usr/bin/env python3
"""
Script para limpiar eventos manteniendo algunos eventos pasados
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection
from datetime import datetime, timedelta

def clean_events_keep_past():
    """Eliminar eventos futuros y mantener solo algunos eventos pasados recientes"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🧹 LIMPIANDO EVENTOS - MANTENIENDO HISTORIAL RECIENTE...")
        print("=" * 60)
        
        # Definir fecha límite para eventos pasados (últimos 30 días)
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Ver todos los eventos actuales
        cursor.execute("""
            SELECT id, nombre, fecha_evento, organizacion,
                   CASE 
                       WHEN fecha_evento > NOW() THEN 'FUTURO'
                       WHEN fecha_evento > %s THEN 'PASADO_RECIENTE'
                       ELSE 'PASADO_ANTIGUO'
                   END as estado
            FROM eventos 
            ORDER BY fecha_evento DESC
        """, (cutoff_date,))
        
        all_events = cursor.fetchall()
        
        print(f"📊 EVENTOS ACTUALES ({len(all_events)} total):")
        future_events = []
        recent_past_events = []
        old_past_events = []
        
        for event in all_events:
            if event['estado'] == 'FUTURO':
                future_events.append(event)
                print(f"  🔮 FUTURO: ID {event['id']} - {event['nombre']} ({event['fecha_evento']}) - {event['organizacion']}")
            elif event['estado'] == 'PASADO_RECIENTE':
                recent_past_events.append(event)
                print(f"  📅 PASADO RECIENTE: ID {event['id']} - {event['nombre']} ({event['fecha_evento']}) - {event['organizacion']}")
            else:
                old_past_events.append(event)
                print(f"  📜 PASADO ANTIGUO: ID {event['id']} - {event['nombre']} ({event['fecha_evento']}) - {event['organizacion']}")
        
        print(f"\n📈 RESUMEN:")
        print(f"  - Eventos futuros: {len(future_events)} (ELIMINAR)")
        print(f"  - Eventos pasados recientes: {len(recent_past_events)} (MANTENER)")
        print(f"  - Eventos pasados antiguos: {len(old_past_events)} (ELIMINAR)")
        
        # Eventos a eliminar
        events_to_delete = future_events + old_past_events
        
        if len(events_to_delete) == 0:
            print("\n✅ No hay eventos para eliminar")
            cursor.close()
            conn.close()
            return
        
        print(f"\n🗑️  ELIMINANDO {len(events_to_delete)} EVENTOS...")
        
        event_ids_to_delete = [event['id'] for event in events_to_delete]
        
        if event_ids_to_delete:
            placeholders = ','.join(['%s'] * len(event_ids_to_delete))
            
            # Verificar qué tablas existen
            cursor.execute("SHOW TABLES")
            tables_result = cursor.fetchall()
            existing_tables = [list(table.values())[0] for table in tables_result]
            print(f"  📋 Tablas disponibles: {existing_tables}")
            
            # 1. Eliminar participantes (si la tabla existe)
            if 'participantes_eventos' in existing_tables:
                cursor.execute(f"""
                    DELETE FROM participantes_eventos 
                    WHERE evento_id IN ({placeholders})
                """, event_ids_to_delete)
                
                deleted_participants = cursor.rowcount
                print(f"  ✅ Eliminados {deleted_participants} participantes")
            else:
                print(f"  ⚠️  Tabla participantes_eventos no existe")
            
            # 2. Eliminar donaciones distribuidas (si la tabla existe)
            if 'donaciones_distribuidas' in existing_tables:
                cursor.execute(f"""
                    DELETE FROM donaciones_distribuidas 
                    WHERE evento_id IN ({placeholders})
                """, event_ids_to_delete)
                
                deleted_distributions = cursor.rowcount
                print(f"  ✅ Eliminadas {deleted_distributions} distribuciones de donaciones")
            else:
                print(f"  ⚠️  Tabla donaciones_distribuidas no existe")
            
            # 3. Eliminar adhesiones de eventos (si existe)
            if 'adhesiones_eventos' in existing_tables:
                cursor.execute(f"""
                    DELETE FROM adhesiones_eventos 
                    WHERE evento_id IN ({placeholders})
                """, event_ids_to_delete)
                
                deleted_adhesions = cursor.rowcount
                print(f"  ✅ Eliminadas {deleted_adhesions} adhesiones de eventos")
            else:
                print(f"  ⚠️  Tabla adhesiones_eventos no existe")
            
            # 4. Eliminar de eventos_red (si existe)
            if 'eventos_red' in existing_tables:
                cursor.execute(f"""
                    DELETE FROM eventos_red 
                    WHERE evento_id IN ({placeholders})
                """, event_ids_to_delete)
                
                deleted_network = cursor.rowcount
                print(f"  ✅ Eliminados {deleted_network} eventos de la red")
            else:
                print(f"  ⚠️  Tabla eventos_red no existe")
            
            # 5. Eliminar los eventos
            cursor.execute(f"""
                DELETE FROM eventos 
                WHERE id IN ({placeholders})
            """, event_ids_to_delete)
            
            deleted_events = cursor.rowcount
            print(f"  ✅ Eliminados {deleted_events} eventos")
        
        conn.commit()
        
        # Verificar resultado final
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN fecha_evento > NOW() THEN 1 ELSE 0 END) as futuros,
                   SUM(CASE WHEN fecha_evento <= NOW() AND fecha_evento > %s THEN 1 ELSE 0 END) as pasados_recientes,
                   SUM(CASE WHEN fecha_evento <= %s THEN 1 ELSE 0 END) as pasados_antiguos
            FROM eventos
        """, (cutoff_date, cutoff_date))
        
        final_count = cursor.fetchone()
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"  - Total eventos: {final_count['total']}")
        print(f"  - Eventos futuros: {final_count['futuros']}")
        print(f"  - Eventos pasados recientes: {final_count['pasados_recientes']}")
        print(f"  - Eventos pasados antiguos: {final_count['pasados_antiguos']}")
        
        # Mostrar eventos que quedaron
        if final_count['total'] > 0:
            print(f"\n📋 EVENTOS RESTANTES:")
            cursor.execute("""
                SELECT id, nombre, fecha_evento, organizacion
                FROM eventos 
                ORDER BY fecha_evento DESC
            """)
            
            remaining_events = cursor.fetchall()
            for event in remaining_events:
                print(f"  📅 ID {event['id']}: {event['nombre']} ({event['fecha_evento']}) - {event['organizacion']}")
        
        print(f"\n🎉 LIMPIEZA COMPLETADA!")
        print(f"✅ Base limpia con {final_count['pasados_recientes']} eventos pasados recientes como historial")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_events_keep_past()