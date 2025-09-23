import grpc
from concurrent import futures
import users_pb2_grpc
from user_service import UserService
import os
import sys
import signal
from dotenv import load_dotenv

load_dotenv()

def signal_handler(signum, frame):
    print("🛑 Señal de terminación recibida, cerrando servidor...")
    sys.exit(0)

def serve():
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Crear servidor gRPC
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # Agregar el servicio de usuarios
        users_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
        
        # Configurar puerto - escuchar en todas las interfaces
        port = os.getenv('GRPC_PORT', '50051')
        server.add_insecure_port(f'0.0.0.0:{port}')
        
        # Iniciar servidor
        server.start()
        print(f"✅ Servidor gRPC de usuarios iniciado en puerto {port}")
        print(f"🌐 Escuchando en 0.0.0.0:{port}")
        
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            print("🛑 Deteniendo servidor...")
            server.stop(0)
            
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    serve()