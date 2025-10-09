#!/usr/bin/env python3
"""
Verificar si el user-service necesita reiniciarse
"""
import sys
import os
sys.path.append('user-service/src')

def check_user_service_version():
    print("🔍 VERIFICANDO VERSIÓN DEL USER-SERVICE")
    print("=" * 45)
    
    try:
        from user_repository_mysql import UserRepository
        import inspect
        
        # Verificar la signatura del método create_user
        repo = UserRepository()
        sig = inspect.signature(repo.create_user)
        params = list(sig.parameters.keys())
        
        print(f"Parámetros en create_user: {len(params)}")
        for i, param in enumerate(params):
            print(f"   {i+1}. {param}")
        
        if 'organization' in params:
            print("✅ Método create_user tiene parámetro 'organization'")
        else:
            print("❌ Método create_user NO tiene parámetro 'organization'")
        
        # Verificar proto files
        import users_pb2
        user_fields = users_pb2.User.DESCRIPTOR.fields_by_name
        
        if 'organization' in user_fields:
            print("✅ Proto User tiene campo 'organization'")
        else:
            print("❌ Proto User NO tiene campo 'organization'")
        
        print(f"\n🎯 CONCLUSIÓN:")
        if 'organization' in params and 'organization' in user_fields:
            print("   ✅ Código actualizado correctamente")
            print("   🔄 El user-service corriendo necesita reiniciarse")
        else:
            print("   ❌ Hay problemas en el código")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user_service_version()