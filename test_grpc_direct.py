#!/usr/bin/env python3
"""
Script para probar gRPC directamente
"""
import grpc
import sys
import os

# Agregar el path del proto
sys.path.append('user-service')

try:
    import user_service.proto.users_pb2 as users_pb2
    import user_service.proto.users_pb2_grpc as users_pb2_grpc
except ImportError:
    print("❌ No se pueden importar los proto files")
    print("Asegúrate de que el user-service esté configurado correctamente")
    sys.exit(1)

def test_grpc_auth():
    try:
        print("🧪 PROBANDO GRPC DIRECTAMENTE")
        print("=" * 40)
        
        # Conectar al servicio gRPC
        channel = grpc.insecure_channel('localhost:50051')
        stub = users_pb2_grpc.UserServiceStub(channel)
        
        # Probar autenticación
        test_users = [
            ("esperanza_admin", "password123"),
            ("admin", "admin123")
        ]
        
        for username, password in test_users:
            print(f"\n🔐 Probando: {username}")
            
            request = users_pb2.AuthRequest(
                username_or_email=username,
                password=password
            )
            
            try:
                response = stub.AuthenticateUser(request)
                
                print(f"   Success: {response.success}")
                print(f"   Message: {response.message}")
                
                if response.success and response.user:
                    user = response.user
                    print(f"   Usuario: {user.first_name} {user.last_name}")
                    print(f"   Email: {user.email}")
                    print(f"   Rol: {user.role}")
                    print(f"   Organización: {user.organization}")
                else:
                    print(f"   ❌ Login fallido")
                    
            except grpc.RpcError as e:
                print(f"   ❌ Error gRPC: {e.code()} - {e.details()}")
        
        channel.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_grpc_auth()