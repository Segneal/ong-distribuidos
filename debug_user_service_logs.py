#!/usr/bin/env python3
"""
Debug con logs detallados del user-service
"""
import sys
import os
sys.path.append('user-service/src')

def debug_with_logs():
    print("🔍 DEBUG CON LOGS DETALLADOS")
    print("=" * 40)
    
    try:
        from user_service import UserService
        import users_pb2
        
        service = UserService()
        
        # Crear request como lo haría gRPC
        request = users_pb2.AuthRequest(
            username_or_email="esperanza_admin",
            password="password123"
        )
        
        print(f"Request: {request.username_or_email} / {request.password}")
        
        # Llamar al método directamente
        response = service.AuthenticateUser(request, None)
        
        print(f"Response success: {response.success}")
        print(f"Response message: {response.message}")
        
        if response.user:
            print(f"User ID: {response.user.id}")
            print(f"User organization: {response.user.organization}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_with_logs()