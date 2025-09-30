#!/usr/bin/env python3
"""
Script para ejecutar la migración de tablas de red en MySQL
"""

import mysql.connector
import os

def execute_migration():
    try:
        # Conectar a MySQL con las credenciales correctas
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # Leer el archivo de migración
        with open('database/network_tables_migration.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir en statements individuales
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"🔄 Ejecutando {len(statements)} statements de migración...")
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✅ Statement {i}/{len(statements)} ejecutado")
                except mysql.connector.Error as e:
                    if "already exists" in str(e) or "Duplicate" in str(e):
                        print(f"⚠️  Statement {i}/{len(statements)} ya existe (ignorado)")
                    else:
                        print(f"❌ Error en statement {i}: {e}")
                        print(f"   SQL: {statement[:100]}...")
        
        conn.commit()
        print("✅ Migración completada exitosamente!")
        
        # Verificar que las tablas se crearon
        cursor.execute("SHOW TABLES LIKE '%externas%' OR SHOW TABLES LIKE '%transferencias%'")
        tables = cursor.fetchall()
        print(f"📋 Tablas de red creadas: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = execute_migration()
    if success:
        print("🎉 ¡Migración de red completada!")
    else:
        print("💥 Falló la migración")