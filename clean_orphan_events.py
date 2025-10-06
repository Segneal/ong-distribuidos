#!/usr/bin/env python3
"""
Script para limpiar eventos huérfanos en eventos_red
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def clean_orphan_events():
    """Limpiar eventos huérfanos en eventos_red"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🧹 LIMPIANDO EVENTOS HUÉRFANOS EN LA RED")
        print("=" * 45)
        
        # Encontrar eventos huérfanos
        cursor.execute("""
            SELECT er.evento_id
            FROM eventos_red er
            LEFT JOIN eventos e ON er.evento_id = e.id
            WHERE e.id IS NULL
        """)
        
        orphan_events = cursor.fetchall()
        
        if len(orphan_events) == 0:
            print("✅ No hay eventos huérfanos para limpiar")
            cursor.close()
            conn.close()
            return
        
        print(f"🚫 EVENTOS HUÉRFANOS ENCONTRADOS: {len(orphan_events)}")
        for orphan in orphan_events:
            print(f"  🗑️  Evento ID {orphan['evento_id']} (no existe en tabla eventos)")
        
        # Eliminar eventos huérfanos
        orphan_ids = [orphan['evento_id'] for orphan in orphan_events]
        placeholders = ','.join(['%s'] * len(orphan_ids))
        
        cursor.execute(f"""
            DELETE FROM eventos_red 
            WHERE evento_id IN ({placeholders})
        """, orphan_ids)
        
        deleted_count = cursor.rowcount
        print(f"\n🗑️  ELIMINADOS: {deleted_count} eventos huérfanos de eventos_red")
        
        conn.commit()
        
        # Verificar resultado
        cursor.execute("""
            SELECT COUNT(*) as total_red
            FROM eventos_red
        """)
        
        final_count = cursor.fetchone()
        
        cursor.execute("""
            SELECT er.evento_id, e.nombre, e.organizacion
            FROM eventos_red er
            JOIN eventos e ON er.evento_id = e.id
            ORDER BY e.organizacion, e.nombre
        """)
        
        remaining_events = cursor.fetchall()
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"  - Total eventos en red: {final_count['total_red']}")
        
        if remaining_events:
            print(f"\n📋 EVENTOS VÁLIDOS EN LA RED:")
            for event in remaining_events:
                print(f"  ✅ ID {event['evento_id']}: {event['nombre']} - {event['organizacion']}")
        
        print(f"\n🎉 LIMPIEZA DE HUÉRFANOS COMPLETADA")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_orphan_events()