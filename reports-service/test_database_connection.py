#!/usr/bin/env python3
"""
Simple script to test database connection and model functionality.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models import test_connection, init_database
from src.utils.database_utils import check_database_health
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test database connection and setup"""
    print("Testing database connection...")
    
    try:
        # Test basic connection
        if test_connection():
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
            return False
        
        # Check health
        health = check_database_health()
        print(f"Database health: {health}")
        
        # Try to initialize database
        print("Initializing database...")
        init_database()
        print("✓ Database initialization successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)