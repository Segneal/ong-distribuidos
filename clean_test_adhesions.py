#!/usr/bin/env python3
"""
Limpiar adhesiones de test para poder probar notificaciones
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def clean_test_adhesions():
    """Limpiar adhesiones de test"""
    print("🧹 LIMPIANDO ADHESIONES DE TEST")
    print("=" * 40)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Mostrar adhesiones actuales
        cursor.execute("""
            SELECT aee.id, aee.evento_externo_id, aee.voluntario_id, aee.estado,
                   u.nombre, u.apellido, u.organizacion,
                   er.nombre as evento_nombre
            FROM adhesiones_eventos_externos aee
            LEFT JOIN usuarios u ON aee.voluntario_id = u.id
            LEFT JOIN eventos_red er ON aee.evento_externo_id = er.evento_id
            WHERE aee.estado = 'PENDIENTE'
            ORDER BY aee.fecha_adhesion DESC
        """)
        
        adhesions = cursor.fetchall()
        print(f"Adhesiones pendientes: {len(adhesions)}")
        
        for adhesion in adhesions:
            print(f"  - ID: {adhesion['id']}")
            print(f"    Evento: {adhesion['evento_nombre']} (ID: {adhesion['evento_externo_id']})")
            print(f"    Voluntario: {adhesion['nombre']} {adhesion['apellido']} ({adhesion['organizacion']})")
            print()
        
        # Eliminar adhesiones de test (las que tienen datos de test)
        cursor.execute("""
            DELETE FROM adhesiones_eventos_externos 
            WHERE datos_voluntario LIKE '%test%' 
            OR datos_voluntario LIKE '%Test%'
            OR datos_voluntario LIKE '%notification%'
        """)
        
        deleted = cursor.rowcount
        print(f"Adhesiones de test eliminadas: {deleted}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Limpieza completada")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_test_adhesions()