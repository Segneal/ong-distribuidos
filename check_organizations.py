#!/usr/bin/env python3
"""
Script para verificar las organizaciones en usuarios y donaciones
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def check_organizations():
    """Verificar organizaciones en usuarios y donaciones"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🏢 ORGANIZACIONES EN USUARIOS:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT DISTINCT organizacion, COUNT(*) as usuarios
            FROM usuarios 
            GROUP BY organizacion
            ORDER BY organizacion
        """)
        
        user_orgs = cursor.fetchall()
        for org in user_orgs:
            print(f"  📋 {org['organizacion']} - {org['usuarios']} usuarios")
        
        print("\n🏢 ORGANIZACIONES EN DONACIONES:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT DISTINCT organizacion, COUNT(*) as donaciones
            FROM donaciones 
            GROUP BY organizacion
            ORDER BY organizacion
        """)
        
        donation_orgs = cursor.fetchall()
        for org in donation_orgs:
            print(f"  📦 {org['organizacion']} - {org['donaciones']} donaciones")
        
        print("\n🔍 COMPARACIÓN:")
        print("=" * 50)
        
        user_org_names = {org['organizacion'] for org in user_orgs}
        donation_org_names = {org['organizacion'] for org in donation_orgs}
        
        print(f"Organizaciones en usuarios: {user_org_names}")
        print(f"Organizaciones en donaciones: {donation_org_names}")
        
        if user_org_names == donation_org_names:
            print("✅ Las organizaciones coinciden")
        else:
            print("❌ Las organizaciones NO coinciden")
            print(f"Solo en usuarios: {user_org_names - donation_org_names}")
            print(f"Solo en donaciones: {donation_org_names - user_org_names}")
        
        # Verificar usuarios específicos
        print("\n👤 USUARIOS ESPECÍFICOS:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT nombre_usuario, organizacion
            FROM usuarios 
            WHERE nombre_usuario IN ('admin', 'esperanza_admin')
        """)
        
        specific_users = cursor.fetchall()
        for user in specific_users:
            print(f"  {user['nombre_usuario']}: {user['organizacion']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_organizations()