#!/usr/bin/env python3
"""
Script para verificar la estructura de la base de datos
"""

import mysql.connector
from mysql.connector import Error

def check_db_structure():
    """Verificar estructura de tablas"""
    
    try:
        # Probar diferentes combinaciones de credenciales
        credentials_to_try = [
            {'user': 'root', 'password': ''},
            {'user': 'root', 'password': 'admin123'},
            {'user': 'root', 'password': 'root'},
            {'user': 'ong_user', 'password': 'ong_password'}
        ]
        
        connection = None
        
        for creds in credentials_to_try:
            try:
                print(f"🔄 Probando credenciales: {creds['user']} / {'*' * len(creds['password'])}")
                connection = mysql.connector.connect(
                    host='localhost',
                    port=3306,
                    database='ong_management',
                    user=creds['user'],
                    password=creds['password'],
                    charset='utf8mb4'
                )
                print(f"✅ Conexión exitosa con {creds['user']}")
                break
            except Error as e:
                print(f"❌ Falló con {creds['user']}: {e}")
                continue
        
        if not connection or not connection.is_connected():
            print("❌ No se pudo conectar con ninguna credencial")
            return False
        
        cursor = connection.cursor()
        
        # Verificar estructura de tabla donaciones
        print("\n📦 TABLA DONACIONES:")
        cursor.execute("DESCRIBE donaciones")
        donaciones_columns = cursor.fetchall()
        
        has_org_donations = False
        for column in donaciones_columns:
            print(f"   - {column[0]} ({column[1]})")
            if column[0] == 'organizacion':
                has_org_donations = True
        
        print(f"   ✅ Campo 'organizacion': {'SÍ' if has_org_donations else 'NO'}")
        
        # Verificar estructura de tabla eventos
        print("\n📅 TABLA EVENTOS:")
        cursor.execute("DESCRIBE eventos")
        eventos_columns = cursor.fetchall()
        
        has_org_events = False
        for column in eventos_columns:
            print(f"   - {column[0]} ({column[1]})")
            if column[0] == 'organizacion':
                has_org_events = True
        
        print(f"   ✅ Campo 'organizacion': {'SÍ' if has_org_events else 'NO'}")
        
        # Mostrar datos actuales
        if has_org_donations:
            print("\n📊 DONACIONES POR ORGANIZACIÓN:")
            cursor.execute("SELECT organizacion, COUNT(*) FROM donaciones GROUP BY organizacion")
            for org, count in cursor.fetchall():
                print(f"   - {org}: {count} donaciones")
        
        if has_org_events:
            print("\n📊 EVENTOS POR ORGANIZACIÓN:")
            cursor.execute("SELECT organizacion, COUNT(*) FROM eventos GROUP BY organizacion")
            for org, count in cursor.fetchall():
                print(f"   - {org}: {count} eventos")
        
        return True
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🔍 VERIFICANDO ESTRUCTURA DE BASE DE DATOS")
    print("=" * 50)
    check_db_structure()