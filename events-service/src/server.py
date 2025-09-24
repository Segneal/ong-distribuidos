#!/usr/bin/env python3
"""
Events Service Server
Main entry point for the Events gRPC service
"""
import os
import sys

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from events_service import serve

if __name__ == '__main__':
    print("Starting ONG Events Service...")
    serve()