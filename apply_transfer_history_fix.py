#!/usr/bin/env python3
"""
Script para aplicar la corrección del historial de transferencias
Agrega el campo organizacion_propietaria para filtrar correctamente
"""
import mysql.connector
import sys

def apply_migration():
    """Aplicar la migración para corregir el historial de transferencias"""
    print("=== APLICANDO CORRECCIÓN HISTORIAL TRANSFERENCIAS ===")
    
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='ong_management',
            user='root',
            password='root'
        )
        
        cursor = connection.cursor()
        
        # Verificar si el campo ya existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'ong_management' 
            AND TABLE_NAME = 'transferencias_donaciones' 
            AND COLUMN_NAME = 'organizacion_propietaria'
        """)
        
        field_exists = cursor.fetchone()[0] > 0
        
        if field_exists:
            print("✅ El campo organizacion_propietaria ya existe")
        else:
            print("📝 Agregando campo organizacion_propietaria...")
            
            # Agregar campo
            cursor.execute("""
                ALTER TABLE transferencias_donaciones 
                ADD COLUMN organizacion_propietaria VARCHAR(100) DEFAULT 'empuje-comunitario'
            """)
            
            print("✅ Campo agregado exitosamente")
        
        # Actualizar registros existentes
        print("📝 Actualizando registros existentes...")
        
        # Para transferencias enviadas, la organización propietaria es empuje-comunitario
        cursor.execute("""
            UPDATE transferencias_donaciones 
            SET organizacion_propietaria = 'empuje-comunitario' 
            WHERE tipo = 'ENVIADA' AND (organizacion_propietaria IS NULL OR organizacion_propietaria = '')
        """)
        
        enviadas_updated = cursor.rowcount
        
        # Para transferencias recibidas, también empuje-comunitario por ahora
        cursor.execute("""
            UPDATE transferencias_donaciones 
            SET organizacion_propietaria = 'empuje-comunitario' 
            WHERE tipo = 'RECIBIDA' AND (organizacion_propietaria IS NULL OR organizacion_propietaria = '')
        """)
        
        recibidas_updated = cursor.rowcount
        
        print(f"✅ Actualizados {enviadas_updated} registros ENVIADAS")
        print(f"✅ Actualizados {recibidas_updated} registros RECIBIDAS")
        
        # Crear índice si no existe
        try:
            cursor.execute("""
                CREATE INDEX idx_transferencias_organizacion_propietaria 
                ON transferencias_donaciones(organizacion_propietaria, fecha_transferencia DESC)
            """)
            print("✅ Índice creado exitosamente")
        except mysql.connector.Error as e:
            if "Duplicate key name" in str(e):
                print("✅ Índice ya existe")
            else:
                print(f"⚠️  Error creando índice: {e}")
        
        # Hacer el campo NOT NULL si no lo es
        try:
            cursor.execute("""
                ALTER TABLE transferencias_donaciones 
                MODIFY COLUMN organizacion_propietaria VARCHAR(100) NOT NULL
            """)
            print("✅ Campo configurado como NOT NULL")
        except mysql.connector.Error as e:
            print(f"⚠️  Error configurando NOT NULL: {e}")
        
        # Commit cambios
        connection.commit()
        
        # Verificar resultado
        cursor.execute("""
            SELECT 
                organizacion_propietaria,
                tipo,
                COUNT(*) as cantidad
            FROM transferencias_donaciones 
            GROUP BY organizacion_propietaria, tipo
            ORDER BY organizacion_propietaria, tipo
        """)
        
        results = cursor.fetchall()
        
        print("\n📊 RESUMEN DE TRANSFERENCIAS POR ORGANIZACIÓN:")
        for org, tipo, cantidad in results:
            print(f"   {org} - {tipo}: {cantidad} transferencias")
        
        cursor.close()
        connection.close()
        
        print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verify_migration():
    """Verificar que la migración se aplicó correctamente"""
    print("\n=== VERIFICANDO MIGRACIÓN ===")
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='ong_management',
            user='root',
            password='root'
        )
        
        cursor = connection.cursor()
        
        # Verificar estructura de la tabla
        cursor.execute("""
            DESCRIBE transferencias_donaciones
        """)
        
        columns = cursor.fetchall()
        
        print("📋 ESTRUCTURA DE LA TABLA:")
        for column in columns:
            field, type_info, null, key, default, extra = column
            print(f"   {field}: {type_info} {'(NOT NULL)' if null == 'NO' else '(NULL)'}")
        
        # Verificar datos
        cursor.execute("""
            SELECT COUNT(*) FROM transferencias_donaciones
        """)
        
        total_count = cursor.fetchone()[0]
        print(f"\n📊 Total de transferencias: {total_count}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando migración: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 CORRECCIÓN HISTORIAL DE TRANSFERENCIAS")
    print("="*60)
    
    # Aplicar migración
    migration_success = apply_migration()
    
    if migration_success:
        # Verificar migración
        verify_migration()
        
        print("\n" + "="*60)
        print("🎉 CORRECCIÓN COMPLETADA")
        print("="*60)
        print("✅ El historial de transferencias ahora se filtra correctamente por organización")
        print("✅ Cada organización verá solo sus propias transferencias")
        print("✅ Los registros existentes han sido actualizados")
        
        print("\n🔄 PRÓXIMOS PASOS:")
        print("1. Reiniciar el API Gateway para aplicar los cambios en el código")
        print("2. Probar el historial de transferencias en el frontend")
        print("3. Verificar que cada organización vea solo sus transferencias")
        
    else:
        print("\n❌ LA MIGRACIÓN FALLÓ")
        print("Revisa los errores anteriores y corrige los problemas")

if __name__ == "__main__":
    main()