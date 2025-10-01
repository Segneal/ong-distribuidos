#!/usr/bin/env python3
"""
Debug completo del flujo de autenticación
"""
import mysql.connector
import hashlib
import sys
import os
sys.path.append('user-service/src')

def debug_complete_flow():
    print("🔍 DEBUG COMPLETO DEL FLUJO DE AUTENTICACIÓN")
    print("=" * 60)
    
    # PASO 1: Verificar datos en BD
    print("\n📊 PASO 1: VERIFICAR DATOS EN BASE DE DATOS")
    print("-" * 40)
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        cursor = connection.cursor()
        
        # Buscar usuario esperanza_admin
        cursor.execute("""
            SELECT id, nombre_usuario, nombre, apellido, email, rol, organizacion, activo, password_hash
            FROM usuarios 
            WHERE nombre_usuario = %s
        """, ("esperanza_admin",))
        
        user = cursor.fetchone()
        if user:
            print("✅ Usuario encontrado en BD:")
            print(f"   ID: {user[0]}")
            print(f"   Username: {user[1]}")
            print(f"   Nombre: {user[2]} {user[3]}")
            print(f"   Email: {user[4]}")
            print(f"   Rol: {user[5]}")
            print(f"   Organización: {user[6]}")
            print(f"   Activo: {user[7]}")
            print(f"   Password hash: {user[8][:20]}...")
        else:
            print("❌ Usuario NO encontrado en BD")
            return
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return
    
    # PASO 2: Verificar UserRepository
    print("\n🔧 PASO 2: VERIFICAR USER REPOSITORY")
    print("-" * 40)
    
    try:
        from user_repository_mysql import UserRepository
        repo = UserRepository()
        
        user_data = repo.get_user_by_username_or_email("esperanza_admin")
        if user_data:
            print("✅ UserRepository.get_user_by_username_or_email funciona:")
            print(f"   Campos devueltos: {list(user_data.keys())}")
            print(f"   Organización: {user_data.get('organizacion')}")
            print(f"   Password hash: {user_data.get('password_hash', '')[:20]}...")
        else:
            print("❌ UserRepository NO devuelve usuario")
            return
            
    except Exception as e:
        print(f"❌ Error en UserRepository: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # PASO 3: Verificar verify_password
    print("\n🔐 PASO 3: VERIFICAR VERIFY_PASSWORD")
    print("-" * 40)
    
    try:
        from crypto import verify_password
        
        password = "password123"
        stored_hash = user_data.get('password_hash')
        
        print(f"   Password input: {password}")
        print(f"   Stored hash: {stored_hash[:20]}...")
        print(f"   Hash type: {'bcrypt' if stored_hash.startswith('$2b$') else 'SHA256'}")
        
        # Verificar manualmente
        if stored_hash.startswith('$2b$'):
            print("   Usando verificación bcrypt")
        else:
            print("   Usando verificación SHA256")
            manual_hash = hashlib.sha256(password.encode()).hexdigest()
            print(f"   Manual SHA256: {manual_hash[:20]}...")
            print(f"   Match manual: {manual_hash == stored_hash}")
        
        # Usar función verify_password
        result = verify_password(password, stored_hash)
        print(f"   verify_password result: {result}")
        
    except Exception as e:
        print(f"❌ Error en verify_password: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # PASO 4: Verificar _create_user_message
    print("\n📝 PASO 4: VERIFICAR _CREATE_USER_MESSAGE")
    print("-" * 40)
    
    try:
        from user_service import UserService
        service = UserService()
        
        # Limpiar password_hash para el mensaje
        user_data_clean = {k: v for k, v in user_data.items() if k != 'password_hash'}
        
        user_message = service._create_user_message(user_data_clean)
        print("✅ _create_user_message funciona:")
        print(f"   ID: {user_message.id}")
        print(f"   Username: {user_message.username}")
        print(f"   First name: {user_message.first_name}")
        print(f"   Organization: {user_message.organization}")
        
    except Exception as e:
        print(f"❌ Error en _create_user_message: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # PASO 5: Simular AuthenticateUser completo
    print("\n🎯 PASO 5: SIMULAR AUTHENTICATE_USER COMPLETO")
    print("-" * 40)
    
    try:
        # Simular el flujo completo
        print("   1. Buscar usuario... ✅")
        print("   2. Verificar activo... ✅" if user_data['activo'] else "   2. Verificar activo... ❌")
        print("   3. Verificar password... ✅" if result else "   3. Verificar password... ❌")
        
        if user_data['activo'] and result:
            print("   4. Generar token... ✅")
            print("   5. Crear user message... ✅")
            print("   ✅ AuthenticateUser debería funcionar")
        else:
            print("   ❌ AuthenticateUser fallaría")
            
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
    
    print(f"\n🎯 CONCLUSIÓN:")
    if user_data['activo'] and result:
        print("   ✅ Todos los pasos funcionan - el problema puede estar en otro lado")
        print("   🔍 Revisar logs del user-service para más detalles")
    else:
        print("   ❌ Problema identificado en los pasos anteriores")

if __name__ == "__main__":
    debug_complete_flow()