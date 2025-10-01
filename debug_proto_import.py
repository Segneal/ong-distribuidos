#!/usr/bin/env python3
"""
Debug para verificar qué proto files está usando el user-service
"""
import sys
import os
sys.path.append('user-service/src')

def debug_proto_import():
    print("🔍 DEBUG PROTO IMPORT")
    print("=" * 30)
    
    try:
        import users_pb2
        
        # Verificar si User tiene campo organization
        user_fields = users_pb2.User.DESCRIPTOR.fields_by_name
        print(f"Campos en User message:")
        for field_name in user_fields:
            print(f"   - {field_name}")
        
        if 'organization' in user_fields:
            print("✅ Campo 'organization' existe en proto")
        else:
            print("❌ Campo 'organization' NO existe en proto")
        
        # Crear un User message de prueba
        user = users_pb2.User(
            id=1,
            username="test",
            first_name="Test",
            last_name="User",
            email="test@test.com",
            organization="test-org"
        )
        
        print(f"✅ User message creado con organization: {user.organization}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_proto_import()