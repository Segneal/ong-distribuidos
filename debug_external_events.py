#!/usr/bin/env python3
"""
Script para debuggear eventos externos
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def debug_external_events():
    """Debuggear eventos externos"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 DEBUGGING EVENTOS EXTERNOS")
        print("=" * 50)
        
        # 1. Ver todos los eventos en la tabla eventos
        print("📅 EVENTOS EN TABLA 'eventos':")
        cursor.execute("""
            SELECT id, nombre, organizacion, fecha_evento
            FROM eventos 
            ORDER BY organizacion, fecha_evento DESC
        """)
        
        eventos = cursor.fetchall()
        for evento in eventos:
            print(f"  📝 ID {evento['id']}: {evento['nombre']}")
            print(f"      🏢 Organización: {evento['organizacion']}")
            print(f"      📅 Fecha: {evento['fecha_evento']}")
            print()
        
        # 2. Ver eventos en la tabla eventos_externos
        print("🌐 EVENTOS EN TABLA 'eventos_externos':")
        cursor.execute("""
            SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo, fecha_creacion
            FROM eventos_externos 
            ORDER BY organizacion_id, fecha_evento DESC
        """)
        
        eventos_externos = cursor.fetchall()
        if len(eventos_externos) == 0:
            print("  ⚠️  No hay eventos en la tabla eventos_externos")
        else:
            for evento in eventos_externos:
                print(f"  🌐 ID {evento['id']}: {evento['nombre']}")
                print(f"      🏢 Organización: {evento['organizacion_id']}")
                print(f"      🔢 Evento ID: {evento['evento_id']}")
                print(f"      📅 Fecha: {evento['fecha_evento']}")
                print(f"      ✅ Activo: {evento['activo']}")
                print(f"      📅 Creado: {evento['fecha_creacion']}")
                print()
        
        # 3. Ver eventos en la tabla eventos_red
        print("🔗 EVENTOS EN TABLA 'eventos_red':")
        cursor.execute("""
            SELECT er.evento_id, er.organizacion_origen, e.nombre, e.organizacion, e.fecha_evento
            FROM eventos_red er
            LEFT JOIN eventos e ON er.evento_id = e.id
            ORDER BY er.organizacion_origen, e.fecha_evento DESC
        """)
        
        eventos_red = cursor.fetchall()
        if len(eventos_red) == 0:
            print("  ⚠️  No hay eventos en la tabla eventos_red")
        else:
            for evento in eventos_red:
                print(f"  🔗 Evento ID {evento['evento_id']}: {evento['nombre'] or 'EVENTO ELIMINADO'}")
                print(f"      🏢 Org Origen: {evento['organizacion_origen']}")
                print(f"      🏢 Org Real: {evento['organizacion'] or 'N/A'}")
                print(f"      📅 Fecha: {evento['fecha_evento'] or 'N/A'}")
                print()
        
        # 4. Verificar qué devuelve la consulta de eventos externos activos
        print("🔍 CONSULTA DE EVENTOS EXTERNOS ACTIVOS:")
        cursor.execute("""
            SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, fecha_creacion
            FROM eventos_externos 
            WHERE activo = true AND fecha_evento > CURRENT_TIMESTAMP
            ORDER BY fecha_evento ASC
        """)
        
        eventos_activos = cursor.fetchall()
        print(f"📊 Total eventos externos activos: {len(eventos_activos)}")
        
        for evento in eventos_activos:
            print(f"  ✅ ID {evento['id']}: {evento['nombre']}")
            print(f"      🏢 Organización: {evento['organizacion_id']}")
            print(f"      🔢 Evento ID: {evento['evento_id']}")
            print(f"      📅 Fecha: {evento['fecha_evento']}")
            print()
        
        # 5. Verificar si hay inconsistencias entre tablas
        print("⚠️  VERIFICANDO INCONSISTENCIAS:")
        
        # Eventos en eventos_red que no existen en eventos
        cursor.execute("""
            SELECT er.evento_id, er.organizacion_origen
            FROM eventos_red er
            LEFT JOIN eventos e ON er.evento_id = e.id
            WHERE e.id IS NULL
        """)
        
        huerfanos = cursor.fetchall()
        if len(huerfanos) > 0:
            print(f"  🚫 Eventos huérfanos en eventos_red: {len(huerfanos)}")
            for huerfano in huerfanos:
                print(f"    - Evento ID {huerfano['evento_id']} de {huerfano['organizacion_origen']}")
        else:
            print(f"  ✅ No hay eventos huérfanos en eventos_red")
        
        # Eventos que deberían estar en eventos_externos pero no están
        cursor.execute("""
            SELECT e.id, e.nombre, e.organizacion, e.fecha_evento
            FROM eventos e
            JOIN eventos_red er ON e.id = er.evento_id
            LEFT JOIN eventos_externos ee ON (ee.organizacion_id = e.organizacion AND ee.evento_id = e.id)
            WHERE ee.id IS NULL
        """)
        
        faltantes = cursor.fetchall()
        if len(faltantes) > 0:
            print(f"  ⚠️  Eventos que deberían estar en eventos_externos: {len(faltantes)}")
            for faltante in faltantes:
                print(f"    - ID {faltante['id']}: {faltante['nombre']} ({faltante['organizacion']})")
        else:
            print(f"  ✅ Todos los eventos de la red están en eventos_externos")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 DEBUGGING COMPLETADO")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_external_events()