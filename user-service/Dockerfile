FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY proto/ ./proto/

# Compilar archivos protobuf
RUN python -m grpc_tools.protoc \
    --proto_path=./proto \
    --python_out=./src \
    --grpc_python_out=./src \
    ./proto/users.proto

# Crear directorio para testing
RUN mkdir -p testing/usuarios

# Configurar variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exponer puerto gRPC
EXPOSE 50051

# Script de inicio con verificación de base de datos
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Comando para iniciar el servidor
CMD ["/docker-entrypoint.sh"]