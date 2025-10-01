#!/usr/bin/env python3
"""
Test de ListUsers
"""
import sys
import os
sys.path.append('user-service/src')

def test_list_users():
    print("🧪 TEST LIST USERS")
    print("=" * 25)
    
    try:
        from user_service import UserService
        import users_pb2
        
        service = UserService()
        
        # Crear request
        request = users_pb2.ListUsersRequest(
            include_inactive=False
        )
        
        # Llamar al método
        response = service.ListUsers(request, None)
        
        print(f"Success: {response.success}")
        print(f"Message: {response.message}")
        print(f"Users count: {len(response.users)}")
        
        for user in response.users:
            print(f"  - {user.username} | {user.organization} | {user.first_name} {user.last_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_list_users()