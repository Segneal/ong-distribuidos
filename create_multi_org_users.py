#!/usr/bin/env python3
import mysql.connector
import hashlib

def create_multi_org_users():
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
        
        # Función para hashear password
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()
        
        # Usuarios de prueba para diferentes organizaciones
        test_users = [
            # Usuarios para fundacion-esperanza
            ('esperanza_admin', 'María', 'González', 'maria@esperanza.org', '+54-11-1111-1111', 'PRESIDENTE', 'fundacion-esperanza'),
            ('esperanza_coord', 'Carlos', 'Ruiz', 'carlos@esperanza.org', '+54-11-2222-2222', 'COORDINADOR', 'fundacion-esperanza'),
            
            # Usuarios para ong-solidaria
            ('solidaria_admin', 'Ana', 'López', 'ana@solidaria.org', '+54-11-3333-3333', 'PRESIDENTE', 'ong-solidaria'),
            ('solidaria_vol', 'Pedro', 'Martín', 'pedro@solidaria.org', '+54-11-4444-4444', 'VOLUNTARIO', 'ong-solidaria'),
            
            # Usuarios para centro-comunitario
            ('centro_admin', 'Laura', 'Fernández', 'laura@centro.org', '+54-11-5555-5555', 'PRESIDENTE', 'centro-comunitario'),
            ('centro_vocal', 'Diego', 'Silva', 'diego@centro.org', '+54-11-6666-6666', 'VOCAL', 'centro-comunitario')
        ]
        
        print("Creando usuarios para diferentes organizaciones...")
        
        for user_data in test_users:
            try:
                # Verificar si el usuario ya existe
                cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (user_data[0],))
                if cursor.fetchone():
                    print(f"⚠ Usuario {user_data[0]} ya existe")
                    continue
                
                # Verificar si el email ya existe
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (user_data[3],))
                if cursor.fetchone():
                    print(f"⚠ Email {user_data[3]} ya existe")
                    continue
                
                cursor.execute("""
                    INSERT INTO usuarios 
                    (nombre_usuario, nombre, apellido, email, telefono, rol, organizacion, password_hash, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true)
                """, (
                    user_data[0],  # nombre_usuario
                    user_data[1],  # nombre
                    user_data[2],  # apellido
                    user_data[3],  # email
                    user_data[4],  # telefono
                    user_data[5],  # rol
                    user_data[6],  # organizacion
                    hash_password('password123')  # password_hash
                ))
                print(f"✓ Usuario {user_data[0]} ({user_data[6]}) creado")
                
            except mysql.connector.Error as err:
                print(f"❌ Error creando usuario {user_data[0]}: {err}")
        
        connection.commit()
        
        # Mostrar resumen final
        print("\n=== RESUMEN DEL SISTEMA MULTI-ORGANIZACIÓN ===")
        
        cursor.execute("SELECT COUNT(*) FROM organizaciones")
        org_count = cursor.fetchone()[0]
        print(f"Organizaciones registradas: {org_count}")
        
        cursor.execute("SELECT organizacion, COUNT(*) FROM usuarios GROUP BY organizacion")
        user_counts = cursor.fetchall()
        print("\nUsuarios por organización:")
        for org, count in user_counts:
            print(f"  • {org}: {count} usuarios")
        
        # Mostrar credenciales de acceso
        print("\n=== CREDENCIALES DE ACCESO ===")
        print("Password para todos los usuarios de prueba: password123")
        print("\nUsuarios de prueba creados:")
        
        cursor.execute("""
            SELECT nombre_usuario, nombre, apellido, organizacion, rol 
            FROM usuarios 
            WHERE organizacion != 'empuje-comunitario'
            ORDER BY organizacion, rol
        """)
        
        test_users_created = cursor.fetchall()
        current_org = None
        
        for user in test_users_created:
            if user[3] != current_org:
                current_org = user[3]
                print(f"\n  📋 {current_org.upper()}:")
            print(f"    - {user[0]} | {user[1]} {user[2]} | {user[4]}")
        
        print("\n✅ Sistema multi-organización configurado exitosamente!")
        print("\n🔧 Próximos pasos:")
        print("   1. Modificar sistema de autenticación para mostrar organización")
        print("   2. Adaptar Kafka producers/consumers para usar organización del usuario")
        print("   3. Probar flujos de mensajería entre organizaciones")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    create_multi_org_users()