#!/usr/bin/env python3
"""
Ejecutar messaging service localmente para debug
"""
import os
import sys

# Configurar variables de entorno
os.environ['KAFKA_BROKERS'] = 'localhost:9092'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = 'root'
os.environ['DB_NAME'] = 'ong_management'
os.environ['ORGANIZATION_ID'] = 'empuje-comunitario'
os.environ['SERVICE_PORT'] = '50055'  # Puerto diferente para no conflicto

# Agregar path
sys.path.append('messaging-service/src')

# Importar y ejecutar
if __name__ == "__main__":
    from server import app
    import uvicorn
    
    print("🚀 STARTING LOCAL MESSAGING SERVICE ON PORT 50055")
    uvicorn.run(app, host="0.0.0.0", port=50055)