#!/usr/bin/env python3
"""
Test directo al servidor gRPC
"""
import grpc
import sys
import os
sys.path.append('user-service/src')

def test_grpc_server():
    print("🧪 TEST DIRECTO AL SERVIDOR GRPC")
    print("=" * 40)
    
    try:
        import users_pb2
        import users_pb2_grpc
        
        # Conectar al servidor gRPC
        channel = grpc.insecure_channel('localhost:50051')
        stub = users_pb2_grpc.UserServiceStub(channel)
        
        # Test con esperanza_admin
        print("🔐 Probando esperanza_admin con password123")
        
        request = users_pb2.AuthRequest(
            username_or_email="esperanza_admin",
            password="password123"
        )
        
        try:
            response = stub.AuthenticateUser(request)
            
            print(f"Success: {response.success}")
            print(f"Message: {response.message}")
            
            if response.success and response.user:
                print(f"User ID: {response.user.id}")
                print(f"Username: {response.user.username}")
                print(f"Organization: {response.user.organization}")
                print(f"Token length: {len(response.token)}")
            
        except grpc.RpcError as e:
            print(f"gRPC Error: {e.code()} - {e.details()}")
        
        # Test con admin (usuario original)
        print("\n🔐 Probando admin con admin123")
        
        request2 = users_pb2.AuthRequest(
            username_or_email="admin",
            password="admin123"
        )
        
        try:
            response2 = stub.AuthenticateUser(request2)
            
            print(f"Success: {response2.success}")
            print(f"Message: {response2.message}")
            
            if response2.success and response2.user:
                print(f"User ID: {response2.user.id}")
                print(f"Username: {response2.user.username}")
                print(f"Organization: {response2.user.organization}")
            
        except grpc.RpcError as e:
            print(f"gRPC Error: {e.code()} - {e.details()}")
        
        channel.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grpc_server()