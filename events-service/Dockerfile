FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY ./events-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY ./events-service/src/ ./src/
COPY ./events-service/proto/ ./proto/
COPY ./shared/ ./shared/

# Compilar archivos protobuf
RUN python -m grpc_tools.protoc \
    --proto_path=./proto \
    --python_out=./src \
    --grpc_python_out=./src \
    ./proto/events.proto

# Configurar PYTHONPATH para encontrar los modelos compartidos
ENV PYTHONPATH=/app:/app/shared
ENV PYTHONUNBUFFERED=1

# Exponer puerto gRPC
EXPOSE 50053

# Script de inicio con verificación de base de datos
COPY ./events-service/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Comando para ejecutar el servicio
CMD ["/docker-entrypoint.sh"]