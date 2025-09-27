#!/bin/bash

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "Waiting for $service_name..."
    while ! nc -z $host $port; do
        echo "  $service_name not ready, waiting..."
        sleep 2
    done
    echo "$service_name is ready!"
}

# Wait for dependencies
wait_for_service kafka 9092 "Kafka"
wait_for_service postgres 5432 "PostgreSQL"

# Start the messaging service
echo "Starting messaging service..."
cd /app

# Start Flask API server in background
echo "Starting HTTP API server on port 8000..."
python -m src.api_server &
API_PID=$!

# Start main FastAPI service
echo "Starting main messaging service on port 50054..."
python -m src.main &
MAIN_PID=$!

# Wait for either process to exit
wait -n

# Kill remaining processes
kill $API_PID $MAIN_PID 2>/dev/null

echo "Messaging service stopped"