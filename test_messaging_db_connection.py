#!/usr/bin/env python3
"""
Test de conexión a la base de datos del messaging service
"""
import mysql.connector

# Credenciales que usa el messaging service
MESSAGING_DB_CONFIG = {
    'host': 'localhost',  # Desde fuera de Docker
    'port': 3306,         # Puerto estándar
    'user': 'root',       # Usuario root
    'password': 'root',   # Contraseña root
    'database': 'ong_management'
}

# Credenciales que usamos en los tests
TEST_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def test_messaging_db():
    """Test de la base de datos del messaging service"""
    print("=== TESTING MESSAGING SERVICE DATABASE ===")
    
    try:
        conn = mysql.connector.connect(**MESSAGING_DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("✅ Conexión exitosa con credenciales del messaging service")
        
        # Verificar transferencias
        cursor.execute("""
            SELECT COUNT(*) as total FROM transferencias_donaciones 
            WHERE organizacion_propietaria = 'esperanza-social'
        """)
        
        result = cursor.fetchone()
        print(f"Transferencias para esperanza-social: {result['total']}")
        
        # Verificar la transferencia específica
        cursor.execute("""
            SELECT * FROM transferencias_donaciones 
            WHERE organizacion_propietaria = 'esperanza-social'
            ORDER BY id DESC LIMIT 1
        """)
        
        transfer = cursor.fetchone()
        if transfer:
            print(f"Última transferencia: ID {transfer['id']}, Tipo: {transfer['tipo']}")
        else:
            print("No se encontraron transferencias")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error con credenciales del messaging service: {e}")
    
    print("\n=== TESTING TEST DATABASE ===")
    
    try:
        conn = mysql.connector.connect(**TEST_DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("✅ Conexión exitosa con credenciales de test")
        
        # Verificar transferencias
        cursor.execute("""
            SELECT COUNT(*) as total FROM transferencias_donaciones 
            WHERE organizacion_propietaria = 'esperanza-social'
        """)
        
        result = cursor.fetchone()
        print(f"Transferencias para esperanza-social: {result['total']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error con credenciales de test: {e}")

if __name__ == "__main__":
    test_messaging_db()