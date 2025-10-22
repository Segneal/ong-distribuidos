#!/usr/bin/env python3
"""
Simple startup script for Reports Service
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    if not Path('.env').exists():
        print("❌ .env file not found. Please run deploy.py first or copy .env.example to .env")
        return False
    
    if not Path('storage/excel').exists():
        print("⚠️  Creating storage/excel directory...")
        Path('storage/excel').mkdir(parents=True, exist_ok=True)
    
    return True

def start_development():
    """Start service in development mode"""
    print("🚀 Starting Reports Service in development mode...")
    
    env = os.environ.copy()
    env['DEBUG'] = 'true'
    
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'src.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ], env=env)
    except KeyboardInterrupt:
        print("\n👋 Service stopped")

def start_production():
    """Start service in production mode"""
    print("🚀 Starting Reports Service in production mode...")
    
    env = os.environ.copy()
    env['DEBUG'] = 'false'
    
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'src.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--workers', '4'
        ], env=env)
    except KeyboardInterrupt:
        print("\n👋 Service stopped")

def start_simple():
    """Start service with simple Python execution"""
    print("🚀 Starting Reports Service (simple mode)...")
    
    try:
        subprocess.run([sys.executable, '-m', 'src.main'])
    except KeyboardInterrupt:
        print("\n👋 Service stopped")

def main():
    parser = argparse.ArgumentParser(description='Start Reports Service')
    parser.add_argument(
        '--mode', 
        choices=['dev', 'prod', 'simple'], 
        default='dev',
        help='Startup mode (default: dev)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to run on (default: 8000)'
    )
    
    args = parser.parse_args()
    
    if not check_environment():
        sys.exit(1)
    
    print(f"Reports Service - {args.mode.upper()} mode")
    print(f"Port: {args.port}")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    if args.mode == 'dev':
        start_development()
    elif args.mode == 'prod':
        start_production()
    else:
        start_simple()

if __name__ == "__main__":
    main()