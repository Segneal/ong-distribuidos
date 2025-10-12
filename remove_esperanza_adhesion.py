#!/usr/bin/env python3
"""
Eliminar adhesión específica de esperanza-social
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def remove_esperanza_adhesion():
    """Eliminar adhesión de esperanza-social al evento 27"""
    print("🗑️ ELIMINANDO ADHESIÓN DE ESPERANZA-SOCIAL")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Buscar usuario de esperanza-social
        cursor.execute("""
            SELECT id, nombre, apellido FROM usuarios 
            WHERE organizacion = 'esperanza-social' 
            AND rol IN ('PRESIDENTE', 'COORDINADOR')
            LIMIT 1
        """)
        
        user = cursor.fetchone()
        if not user:
            print("❌ No se encontró usuario de esperanza-social")
            return
        
        user_id = user['id']
        print(f"Usuario encontrado: {user['nombre']} {user['apellido']} (ID: {user_id})")
        
        # Buscar adhesión al evento 27
        cursor.execute("""
            SELECT id FROM adhesiones_eventos_externos 
            WHERE evento_externo_id = 27 AND voluntario_id = %s
        """, (user_id,))
        
        adhesion = cursor.fetchone()
        if adhesion:
            # Eliminar adhesión
            cursor.execute("""
                DELETE FROM adhesiones_eventos_externos 
                WHERE id = %s
            """, (adhesion['id'],))
            
            conn.commit()
            print(f"✅ Adhesión eliminada: ID {adhesion['id']}")
        else:
            print("⚠️  No se encontró adhesión al evento 27")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    remove_esperanza_adhesion()