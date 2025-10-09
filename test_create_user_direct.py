#!/usr/bin/env python3
"""
Test directo de CreateUser con logs
"""
import sys
import os
sys.path.append('user-service/src')

def test_create_user_direct():
    print("🧪 TEST DIRECTO CREATE USER")
    print("=" * 35)
    
    try:
        from user_service import UserService
        import users_pb2
        
        service = UserService()
        
        # Crear request igual al que llega por gRPC
        request = users_pb2.CreateUserRequest(
            username="test_user_debug",
            first_name="Test",
            last_name="User",
            email="test@debug.com",
            phone="123456789",
            role=users_pb2.VOLUNTARIO,
            organization="fundacion-esperanza"
        )
        
        print(f"Request creado:")
        print(f"  username: {request.username}")
        print(f"  organization: {request.organization}")
        
        # Llamar al método directamente
        response = service.CreateUser(request, None)
        
        print(f"\nResponse:")
        print(f"  success: {response.success}")
        print(f"  message: {response.message}")
        
        if response.user:
            print(f"  user.id: {response.user.id}")
            print(f"  user.organization: {response.user.organization}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_user_direct()