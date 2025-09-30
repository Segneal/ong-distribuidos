#!/bin/bash
# wait-for-services.sh

set -e

hosts=()
cmd=()
parsing_hosts=true

for arg in "$@"; do
    if [ "$parsing_hosts" = true ]; then
        if [ "$arg" = "--" ]; then
            parsing_hosts=false
        else
            hosts+=("$arg")
        fi
    else
        cmd+=("$arg")
    fi
done

if [ ${#cmd[@]} -eq 0 ]; then
    echo "Usage: $0 host:port [host:port ...] -- command [args...]"
    exit 1
fi

echo "Waiting for services to be ready..."

for host_port in "${hosts[@]}"; do
    host=$(echo "$host_port" | cut -d: -f1)
    port=$(echo "$host_port" | cut -d: -f2)
    
    echo "Waiting for $host:$port..."
    
    timeout=60
    while ! nc -z "$host" "$port"; do
        timeout=$((timeout - 1))
        if [ $timeout -eq 0 ]; then
            echo "Timeout waiting for $host:$port"
            exit 1
        fi
        sleep 1
    done
    
    echo "$host:$port is ready!"
done

echo "All services are ready. Starting application..."
exec "${cmd[@]}"