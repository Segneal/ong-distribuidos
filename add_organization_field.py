#!/usr/bin/env python3
import mysql.connector

def add_organization_field():
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
        
        # Verificar estructura actual de usuarios
        print("Estructura actual de usuarios:")
        cursor.execute("DESCRIBE usuarios")
        columns = [row[0] for row in cursor.fetchall()]
        for col in columns:
            print(f"  - {col}")
        
        # Agregar campo organización si no existe
        if 'organizacion' not in columns:
            print("\nAgregando campo 'organizacion' a tabla usuarios...")
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN organizacion VARCHAR(100) DEFAULT 'empuje-comunitario' NOT NULL
            """)
            connection.commit()
            print("✓ Campo 'organizacion' agregado exitosamente")
        else:
            print("✓ Campo 'organizacion' ya existe")
        
        # Crear tabla de organizaciones
        print("\nCreando tabla de organizaciones...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizaciones (
                id VARCHAR(100) PRIMARY KEY,
                nombre_completo VARCHAR(255) NOT NULL,
                descripcion TEXT,
                contacto_email VARCHAR(255),
                contacto_telefono VARCHAR(50),
                direccion TEXT,
                activa BOOLEAN DEFAULT true,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar organizaciones de prueba
        organizaciones = [
            ('empuje-comunitario', 'ONG Empuje Comunitario', 'Organización principal del sistema', 'admin@empuje.org', '+54-11-1234-5678', 'Buenos Aires, Argentina'),
            ('fundacion-esperanza', 'Fundación Esperanza', 'Fundación dedicada a la ayuda social', 'contacto@esperanza.org', '+54-11-2345-6789', 'Córdoba, Argentina'),
            ('ong-solidaria', 'ONG Solidaria', 'Organización de ayuda comunitaria', 'info@solidaria.org', '+54-11-3456-7890', 'Rosario, Argentina'),
            ('centro-comunitario', 'Centro Comunitario Unidos', 'Centro de desarrollo comunitario', 'unidos@centro.org', '+54-11-4567-8901', 'Mendoza, Argentina')
        ]
        
        for org_data in organizaciones:
            try:
                cursor.execute("""
                    INSERT INTO organizaciones 
                    (id, nombre_completo, descripcion, contacto_email, contacto_telefono, direccion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, org_data)
                print(f"✓ Organización {org_data[0]} agregada")
            except mysql.connector.IntegrityError:
                print(f"⚠ Organización {org_data[0]} ya existe")
        
        connection.commit()
        
        # Crear usuarios de prueba para diferentes organizaciones
        print("\nCreando usuarios de prueba para diferentes organizaciones...")
        
        # Usuarios para fundacion-esperanza
        test_users = [
            ('esperanza_admin', 'María', 'González', 'maria@esperanza.org', '+54-11-1111-1111', 'PRESIDENTE', 'fundacion-esperanza'),
            ('esperanza_coord', 'Carlos', 'Ruiz', 'carlos@esperanza.org', '+54-11-2222-2222', 'COORDINADOR', 'fundacion-esperanza'),
            
            # Usuarios para ong-solidaria
            ('solidaria_admin', 'Ana', 'López', 'ana@solidaria.org', '+54-11-3333-3333', 'PRESIDENTE', 'ong-solidaria'),
            ('solidaria_vol', 'Pedro', 'Martín', 'pedro@solidaria.org', '+54-11-4444-4444', 'VOLUNTARIO', 'ong-solidaria'),
            
            # Usuarios para centro-comunitario
            ('centro_admin', 'Laura', 'Fernández', 'laura@centro.org', '+54-11-5555-5555', 'PRESIDENTE', 'centro-comunitario'),
            ('centro_vocal', 'Diego', 'Silva', 'diego@centro.org', '+54-11-6666-6666', 'VOCAL', 'centro-comunitario')
        ]
        
        for user_data in test_users:
            try:
                # Verificar si el usuario ya existe
                cursor.execute("SELECT id FROM usuarios WHERE username = %s", (user_data[0],))
                if cursor.fetchone():
                    print(f"⚠ Usuario {user_data[0]} ya existe")
                    continue
                
                cursor.execute("""
                    INSERT INTO usuarios 
                    (username, name, lastName, email, phone, role, organizacion, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'password123')
                """, user_data)
                print(f"✓ Usuario {user_data[0]} ({user_data[6]}) creado")
            except mysql.connector.Error as err:
                print(f"❌ Error creando usuario {user_data[0]}: {err}")
        
        connection.commit()
        
        # Mostrar resumen
        cursor.execute("SELECT COUNT(*) FROM organizaciones")
        org_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT organizacion, COUNT(*) FROM usuarios GROUP BY organizacion")
        user_counts = cursor.fetchall()
        
        print(f"\n✅ Sistema multi-organización configurado:")
        print(f"   - Organizaciones: {org_count}")
        print("   - Usuarios por organización:")
        for org, count in user_counts:
            print(f"     * {org}: {count} usuarios")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    add_organization_field()