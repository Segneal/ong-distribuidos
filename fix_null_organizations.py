#!/usr/bin/env python3
"""
Script para arreglar usuarios con organización NULL
"""
import mysql.connector

def fix_null_organizations():
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
        
        print("🔧 ARREGLANDO USUARIOS CON ORGANIZACIÓN NULL")
        print("=" * 50)
        
        # Verificar usuarios con organización NULL
        cursor.execute("SELECT id, nombre_usuario, organizacion FROM usuarios WHERE organizacion IS NULL")
        null_org_users = cursor.fetchall()
        
        if null_org_users:
            print(f"Encontrados {len(null_org_users)} usuarios sin organización:")
            for user in null_org_users:
                print(f"   - {user[1]} (ID: {user[0]})")
            
            # Actualizar usuarios sin organización a empuje-comunitario
            cursor.execute("UPDATE usuarios SET organizacion = 'empuje-comunitario' WHERE organizacion IS NULL")
            connection.commit()
            
            print(f"✅ {cursor.rowcount} usuarios actualizados a 'empuje-comunitario'")
        else:
            print("✅ Todos los usuarios ya tienen organización asignada")
        
        # Verificar estado final
        print("\n📊 ESTADO FINAL:")
        cursor.execute("SELECT organizacion, COUNT(*) FROM usuarios GROUP BY organizacion")
        org_counts = cursor.fetchall()
        
        for org, count in org_counts:
            print(f"   • {org}: {count} usuarios")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ Arreglo completado exitosamente")
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    fix_null_organizations()