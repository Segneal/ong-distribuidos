#!/usr/bin/env python3
"""
Verificar estructura de tabla notificaciones
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_notifications_structure():
    """Verificar estructura de notificaciones"""
    print("🔍 VERIFICANDO ESTRUCTURA DE NOTIFICACIONES")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Estructura detallada de notificaciones
        cursor.execute("SHOW CREATE TABLE notificaciones")
        create_table = cursor.fetchone()[1]
        
        print("Estructura de tabla notificaciones:")
        print(create_table)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_notifications_structure()