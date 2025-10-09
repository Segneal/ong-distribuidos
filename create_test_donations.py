#!/usr/bin/env python3
"""
Script para crear donaciones de prueba para diferentes organizaciones
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def create_test_donations():
    """Crear donaciones de prueba para diferentes organizaciones"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("📦 CREANDO DONACIONES DE PRUEBA:")
        print("=" * 50)
        
        # Donaciones para fundacion-esperanza
        donations_esperanza = [
            ("ALIMENTOS", "Arroz para familias", 10, 17),  # esperanza_admin
            ("ROPA", "Ropa de invierno", 5, 17),
            ("JUGUETES", "Juguetes navideños", 15, 18),  # esperanza_coord
        ]
        
        for categoria, descripcion, cantidad, usuario_id in donations_esperanza:
            cursor.execute("""
                INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta)
                VALUES (%s, %s, %s, %s, %s)
            """, (categoria, descripcion, cantidad, "fundacion-esperanza", usuario_id))
            
            donation_id = cursor.lastrowid
            print(f"✅ Creada donación ID {donation_id}: {descripcion} (fundacion-esperanza)")
        
        # Donaciones para ong-solidaria
        donations_solidaria = [
            ("ALIMENTOS", "Leche en polvo", 8, 19),  # solidaria_admin
            ("UTILES_ESCOLARES", "Cuadernos y lápices", 20, 20),  # solidaria_vol
        ]
        
        for categoria, descripcion, cantidad, usuario_id in donations_solidaria:
            cursor.execute("""
                INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta)
                VALUES (%s, %s, %s, %s, %s)
            """, (categoria, descripcion, cantidad, "ong-solidaria", usuario_id))
            
            donation_id = cursor.lastrowid
            print(f"✅ Creada donación ID {donation_id}: {descripcion} (ong-solidaria)")
        
        # Donaciones para centro-comunitario
        donations_centro = [
            ("ROPA", "Zapatos usados", 12, 21),  # centro_admin
            ("ALIMENTOS", "Conservas variadas", 6, 22),  # centro_vocal
        ]
        
        for categoria, descripcion, cantidad, usuario_id in donations_centro:
            cursor.execute("""
                INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta)
                VALUES (%s, %s, %s, %s, %s)
            """, (categoria, descripcion, cantidad, "centro-comunitario", usuario_id))
            
            donation_id = cursor.lastrowid
            print(f"✅ Creada donación ID {donation_id}: {descripcion} (centro-comunitario)")
        
        conn.commit()
        
        print(f"\n📊 RESUMEN:")
        print(f"✅ Creadas 3 donaciones para fundacion-esperanza")
        print(f"✅ Creadas 2 donaciones para ong-solidaria") 
        print(f"✅ Creadas 2 donaciones para centro-comunitario")
        
        # Verificar el resultado
        cursor.execute("""
            SELECT organizacion, COUNT(*) as total
            FROM donaciones 
            GROUP BY organizacion
            ORDER BY organizacion
        """)
        
        results = cursor.fetchall()
        print(f"\n📈 DONACIONES POR ORGANIZACIÓN:")
        for result in results:
            print(f"  {result['organizacion']}: {result['total']} donaciones")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_donations()