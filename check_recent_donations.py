#!/usr/bin/env python3
"""
Script para verificar las donaciones más recientes
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def check_recent_donations():
    """Verificar las donaciones más recientes"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("📦 DONACIONES MÁS RECIENTES:")
        print("=" * 80)
        
        cursor.execute("""
            SELECT d.id, d.categoria, d.descripcion, d.cantidad, d.organizacion, 
                   d.usuario_alta, d.fecha_alta,
                   u.nombre_usuario, u.organizacion as user_org
            FROM donaciones d
            LEFT JOIN usuarios u ON d.usuario_alta = u.id
            ORDER BY d.fecha_alta DESC
            LIMIT 10
        """)
        
        donations = cursor.fetchall()
        
        for donation in donations:
            print(f"ID: {donation['id']} | {donation['categoria']} | {donation['descripcion']}")
            print(f"  📦 Donación Org: {donation['organizacion']}")
            print(f"  👤 Usuario: {donation['nombre_usuario']} (ID: {donation['usuario_alta']})")
            print(f"  🏢 Usuario Org: {donation['user_org']}")
            
            if donation['organizacion'] != donation['user_org']:
                print(f"  ❌ PROBLEMA: Org de donación != Org de usuario")
            else:
                print(f"  ✅ OK: Organizaciones coinciden")
            
            print(f"  📅 Fecha: {donation['fecha_alta']}")
            print("-" * 60)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_recent_donations()