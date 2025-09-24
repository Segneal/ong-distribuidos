#!/usr/bin/env python3
"""
Simple Events Service Startup Script
"""
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Starting ONG Events Service...")

try:
    from events_service import serve
    serve()
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)