#!/usr/bin/env python3
"""
Debug específico del error de CreateUser
"""
import sys
import os
sys.path.append('user-service/src')

def debug_create_user_error():
    print("🔍 DEBUG ERROR CREATE USER")
    print("=" * 35)
    
    try:
        # 1. Verificar signatura del método create_user
        from user_repository_mysql import UserRepository
        import inspect
        
        repo = UserRepository()
        sig = inspect.signature(repo.create_user)
        
        print("📋 SIGNATURA create_user:")
        print(f"   Parámetros: {list(sig.parameters.keys())}")
        print(f"   Total parámetros: {len(sig.parameters)}")
        
        # 2. Verificar proto CreateUserRequest
        import users_pb2
        
        # Crear un request de prueba
        request = users_pb2.CreateUserRequest(
            username="test",
            first_name="Test",
            last_name="User",
            email="test@test.com",
            phone="123456789",
            role=users_pb2.VOLUNTARIO
        )
        
        print("\n📝 CAMPOS EN CreateUserRequest:")
        fields = request.DESCRIPTOR.fields_by_name
        for field_name in fields:
            print(f"   - {field_name}")
        
        # 3. Verificar si organization existe en request
        has_org = hasattr(request, 'organization')
        print(f"\n🔍 Request tiene 'organization': {has_org}")
        
        if has_org:
            print(f"   organization value: '{request.organization}'")
        
        # 4. Simular la llamada problemática
        print("\n🧪 SIMULANDO LLAMADA:")
        
        # Simular getattr
        org_value = getattr(request, 'organization', 'empuje-comunitario')
        print(f"   getattr result: '{org_value}'")
        
        # Contar argumentos que se pasarían
        args = [
            request.username,
            request.first_name,
            request.last_name,
            request.email,
            request.phone,
            'VOLUNTARIO',  # role_string
            'hash123',     # password_hash
            org_value      # organization
        ]
        
        print(f"   Argumentos a pasar: {len(args)}")
        for i, arg in enumerate(args):
            print(f"     {i+1}. {arg}")
        
        print(f"\n🎯 ANÁLISIS:")
        print(f"   Método espera: {len(sig.parameters)} parámetros")
        print(f"   Se pasan: {len(args)} argumentos")
        
        if len(args) == len(sig.parameters):
            print("   ✅ Número de argumentos correcto")
        else:
            print("   ❌ Número de argumentos incorrecto")
            print(f"   Diferencia: {len(args) - len(sig.parameters)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_create_user_error()