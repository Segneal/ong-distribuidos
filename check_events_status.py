#!/usr/bin/env python3
"""
Script para verificar el estado actual de los eventos
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection
from datetime import datetime

def check_events_status():
    """Verificar el estado actual de los eventos"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("📊 ESTADO ACTUAL DE EVENTOS")
        print("=" * 40)
        
        # Contar eventos por estado
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN fecha_evento > NOW() THEN 1 ELSE 0 END) as futuros,
                SUM(CASE WHEN fecha_evento <= NOW() THEN 1 ELSE 0 END) as pasados
            FROM eventos
        """)
        
        counts = cursor.fetchone()
        
        print(f"📈 RESUMEN:")
        print(f"  - Total eventos: {counts['total']}")
        print(f"  - Eventos futuros: {counts['futuros']}")
        print(f"  - Eventos pasados: {counts['pasados']}")
        
        # Mostrar todos los eventos
        if counts['total'] > 0:
            cursor.execute("""
                SELECT id, nombre, fecha_evento, organizacion,
                       CASE 
                           WHEN fecha_evento > NOW() THEN 'FUTURO'
                           ELSE 'PASADO'
                       END as estado
                FROM eventos 
                ORDER BY fecha_evento DESC
            """)
            
            events = cursor.fetchall()
            
            print(f"\n📋 EVENTOS ACTUALES:")
            for event in events:
                status_icon = "🔮" if event['estado'] == 'FUTURO' else "📅"
                print(f"  {status_icon} ID {event['id']}: {event['nombre']}")
                print(f"      📅 Fecha: {event['fecha_evento']}")
                print(f"      🏢 Organización: {event['organizacion']}")
                print(f"      📊 Estado: {event['estado']}")
                print()
        
        # Verificar eventos en la red
        cursor.execute("""
            SELECT COUNT(*) as total_red
            FROM eventos_red
        """)
        
        red_count = cursor.fetchone()
        print(f"🌐 EVENTOS EN LA RED: {red_count['total_red']}")
        
        if red_count['total_red'] > 0:
            cursor.execute("""
                SELECT er.evento_id, e.nombre, e.fecha_evento, e.organizacion
                FROM eventos_red er
                JOIN eventos e ON er.evento_id = e.id
                ORDER BY e.fecha_evento DESC
            """)
            
            red_events = cursor.fetchall()
            print(f"📋 EVENTOS EXPUESTOS EN LA RED:")
            for event in red_events:
                print(f"  🌐 ID {event['evento_id']}: {event['nombre']} - {event['organizacion']}")
        
        print(f"\n✅ VERIFICACIÓN COMPLETADA")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_events_status()