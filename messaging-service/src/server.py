#!/usr/bin/env python3
"""
Server entry point for the ONG Network Messaging Service
Maintains consistency with other services by using server.py
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def serve():
    """Start the messaging service"""
    try:
        # Import and run the main application
        from main import main
        
        print("🚀 Messaging Service iniciado")
        print(f"📊 Puerto HTTP: {os.getenv('HTTP_PORT', '8000')}")
        print(f"📊 Puerto gRPC: {os.getenv('SERVICE_PORT', '50054')}")
        print(f"📊 Kafka: {os.getenv('KAFKA_BROKERS', 'localhost:9092')}")
        
        # Run the main application
        main()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo Messaging Service...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error iniciando Messaging Service: {e}")
        sys.exit(1)

if __name__ == '__main__':
    serve()