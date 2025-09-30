FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY messaging-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY messaging-service/src/ ./src/

# Copy shared directory
COPY shared/ ./shared/

# Copy wait script
COPY messaging-service/wait-for-services.sh ./
RUN chmod +x wait-for-services.sh

EXPOSE 50054 8000

CMD ["./wait-for-services.sh", "mysql:3306", "kafka:9092", "--", "python", "src/main.py"]