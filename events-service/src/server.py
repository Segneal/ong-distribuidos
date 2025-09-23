#!/usr/bin/env python3
"""
Events Service gRPC Server
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add shared models to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from events_service import serve

if __name__ == '__main__':
    print("Starting Events Service...")
    serve()