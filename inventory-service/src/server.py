#!/usr/bin/env python3
"""
Inventory Service Server
Main entry point for the Inventory gRPC service
"""
import os
import sys

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inventory_service import serve

if __name__ == '__main__':
    print("Starting ONG Inventory Service...")
    serve()