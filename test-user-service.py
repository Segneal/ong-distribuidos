#!/usr/bin/env python3
import os
import sys

# Configurar variables de entorno
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_NAME'] = 'ong_management'
os.environ['DB_USER'] = 'ong_user'
os.environ['DB_PASSWORD'] = 'ong_pass'
os.environ['DB_PORT'] = '5432'
os.environ['GRPC_PORT'] = '50051'
os.environ['JWT_SECRET'] = 'your-secret-key-change-in-production'
os.environ['ORGANIZATION_ID'] = 'empuje-comunitario'

# Agregar el directorio src al path
sys.path.append('user-service/src')

try:
    print("Iniciando User Service...")
    print(f"DB_HOST: {os.environ.get('DB_HOST')}")
    print(f"GRPC_PORT: {os.environ.get('GRPC_PORT')}")
    
    # Importar y ejecutar el servicio
    from user_service import serve
    serve()
    
except ImportError as e:
    print(f"Error de importación: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error general: {e}")
    sys.exit(1)