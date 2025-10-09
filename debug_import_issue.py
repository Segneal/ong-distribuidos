#!/usr/bin/env python3
"""
Debug de problema de import
"""
import sys
import os
sys.path.append('user-service/src')

def debug_import_issue():
    print("🔍 DEBUG IMPORT ISSUE")
    print("=" * 30)
    
    try:
        # Limpiar caché de imports
        if 'user_repository_mysql' in sys.modules:
            print("Removiendo user_repository_mysql del caché")
            del sys.modules['user_repository_mysql']
        
        if 'user_service' in sys.modules:
            print("Removiendo user_service del caché")
            del sys.modules['user_service']
        
        # Importar de nuevo
        from user_repository_mysql import UserRepository
        from user_service import UserService
        import users_pb2
        import inspect
        
        # Verificar signatura después de limpiar caché
        repo = UserRepository()
        sig = inspect.signature(repo.create_user)
        print(f"\nSignatura después de limpiar caché:")
        print(f"  Parámetros: {list(sig.parameters.keys())}")
        print(f"  Total: {len(sig.parameters)}")
        
        # Probar crear usuario
        service = UserService()
        request = users_pb2.CreateUserRequest(
            username="test_cache_debug",
            first_name="Test",
            last_name="Cache",
            email="test@cache.com",
            phone="123456789",
            role=users_pb2.VOLUNTARIO,
            organization="fundacion-esperanza"
        )
        
        print(f"\nProbando CreateUser después de limpiar caché...")
        response = service.CreateUser(request, None)
        
        print(f"Success: {response.success}")
        print(f"Message: {response.message}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_import_issue()