FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY ./inventory-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY ./inventory-service/src/ ./src/
COPY ./inventory-service/proto/ ./proto/
COPY ./shared/ ./shared/

# Configurar PYTHONPATH para encontrar los modelos compartidos
ENV PYTHONPATH=/app:/app/shared

# Exponer puerto gRPC
EXPOSE 50052

# Comando para ejecutar el servicio
CMD ["python", "src/server.py"]