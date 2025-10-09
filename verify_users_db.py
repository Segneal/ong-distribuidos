#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
"""
import mysql.connector

def verify_users():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        print("🔍 VERIFICANDO USUARIOS EN LA BASE DE DATOS")
        print("=" * 60)
        
        # Verificar estructura de la tabla
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        print("📋 Estructura de la tabla usuarios:")
        for col in columns:
            print(f"   - {col[0]} ({col[1]})")
        
        print("\n👥 USUARIOS POR ORGANIZACIÓN:")
        print("-" * 40)
        
        # Obtener usuarios por organización
        cursor.execute("""
            SELECT organizacion, COUNT(*) as total
            FROM usuarios 
            GROUP BY organizacion
            ORDER BY organizacion
        """)
        
        org_counts = cursor.fetchall()
        for org, count in org_counts:
            print(f"\n🏢 {org.upper()}: {count} usuarios")
            
            # Obtener detalles de usuarios de esta organización
            cursor.execute("""
                SELECT nombre_usuario, nombre, apellido, rol, email, activo
                FROM usuarios 
                WHERE organizacion = %s
                ORDER BY rol, nombre_usuario
            """, (org,))
            
            users = cursor.fetchall()
            for user in users:
                status = "✅" if user[5] else "❌"
                print(f"   {status} {user[0]} | {user[1]} {user[2]} | {user[3]} | {user[4]}")
        
        print(f"\n📊 RESUMEN TOTAL:")
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_users = cursor.fetchone()[0]
        print(f"   Total de usuarios: {total_users}")
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = true")
        active_users = cursor.fetchone()[0]
        print(f"   Usuarios activos: {active_users}")
        
        # Verificar organizaciones
        print(f"\n🏢 ORGANIZACIONES REGISTRADAS:")
        cursor.execute("SELECT * FROM organizaciones")
        orgs = cursor.fetchall()
        for org in orgs:
            print(f"   • {org[0]} - {org[1]} (Activa: {org[2]})")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ Verificación completada exitosamente!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    verify_users()