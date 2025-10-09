#!/usr/bin/env python3
"""
Debug específico del mapeo de organización
"""
import sys
import os
sys.path.append('user-service/src')

def debug_organization_mapping():
    print("🔍 DEBUG MAPEO DE ORGANIZACIÓN")
    print("=" * 40)
    
    try:
        from user_repository_mysql import UserRepository
        from user_service import UserService
        
        # 1. Verificar datos en repository
        repo = UserRepository()
        user_data = repo.get_user_by_username_or_email("esperanza_admin")
        
        print("📊 DATOS DEL REPOSITORY:")
        print(f"   organizacion: {user_data.get('organizacion')}")
        print(f"   Todos los campos: {list(user_data.keys())}")
        
        # 2. Verificar mapeo en service
        service = UserService()
        user_data_clean = {k: v for k, v in user_data.items() if k != 'password_hash'}
        
        print("\n📝 DATOS LIMPIOS PARA MAPEO:")
        print(f"   organizacion: {user_data_clean.get('organizacion')}")
        
        # 3. Crear user message
        user_message = service._create_user_message(user_data_clean)
        
        print("\n🎯 USER MESSAGE CREADO:")
        print(f"   organization: {user_message.organization}")
        print(f"   username: {user_message.username}")
        print(f"   first_name: {user_message.first_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_organization_mapping()