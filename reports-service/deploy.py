#!/usr/bin/env python3
"""
Deployment script for Reports Service
Automates the setup and verification process
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import mysql.connector
from mysql.connector import Error
import requests
import time

def print_step(step_name):
    """Print a formatted step name"""
    print(f"\n{'='*50}")
    print(f"STEP: {step_name}")
    print(f"{'='*50}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def check_python_version():
    """Check if Python version is compatible"""
    print_step("Checking Python Version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error(f"Python 3.9+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print_success(f"Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_mysql_connection():
    """Check MySQL connection"""
    print_step("Checking MySQL Connection")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL', '')
    if not database_url:
        print_error("DATABASE_URL not found in environment variables")
        return False
    
    # Parse database URL
    try:
        # Format: mysql+pymysql://user:password@host:port/database
        url_parts = database_url.replace('mysql+pymysql://', '').split('/')
        connection_part = url_parts[0]
        database_name = url_parts[1] if len(url_parts) > 1 else 'ong_management'
        
        if '@' in connection_part:
            auth_part, host_part = connection_part.split('@')
            user, password = auth_part.split(':')
            host_port = host_part.split(':')
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 3306
        else:
            print_error("Invalid DATABASE_URL format")
            return False
        
        # Test connection
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database_name
        )
        
        if connection.is_connected():
            print_success(f"Connected to MySQL database '{database_name}' at {host}:{port}")
            connection.close()
            return True
            
    except Error as e:
        print_error(f"MySQL connection failed: {e}")
        return False
    except Exception as e:
        print_error(f"Error parsing DATABASE_URL: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print_step("Installing Dependencies")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True, check=True)
        
        print_success("Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e.stderr}")
        return False

def setup_directories():
    """Create necessary directories"""
    print_step("Setting Up Directories")
    
    directories = [
        'storage/excel',
        'logs'
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print_success(f"Directory created: {directory}")
        except Exception as e:
            print_error(f"Failed to create directory {directory}: {e}")
            return False
    
    return True

def setup_environment():
    """Setup environment file"""
    print_step("Setting Up Environment")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print_success("Created .env file from .env.example")
            print_warning("Please edit .env file with your specific configuration")
        else:
            print_error(".env.example file not found")
            return False
    else:
        print_success(".env file already exists")
    
    return True

def initialize_database():
    """Initialize database tables"""
    print_step("Initializing Database")
    
    try:
        # Import and run database initialization
        sys.path.append('src')
        from models import init_database
        
        init_database()
        print_success("Database initialized successfully")
        return True
        
    except Exception as e:
        print_error(f"Database initialization failed: {e}")
        return False

def test_service_startup():
    """Test if the service starts correctly"""
    print_step("Testing Service Startup")
    
    try:
        # Start the service in background
        process = subprocess.Popen([
            sys.executable, '-m', 'src.main'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            # Test health endpoint
            try:
                response = requests.get('http://localhost:8000/health', timeout=10)
                if response.status_code == 200:
                    print_success("Service started successfully and health check passed")
                    process.terminate()
                    process.wait()
                    return True
                else:
                    print_error(f"Health check failed with status {response.status_code}")
            except requests.RequestException as e:
                print_error(f"Failed to connect to service: {e}")
        else:
            stdout, stderr = process.communicate()
            print_error(f"Service failed to start: {stderr.decode()}")
        
        # Cleanup
        if process.poll() is None:
            process.terminate()
            process.wait()
        
        return False
        
    except Exception as e:
        print_error(f"Error testing service startup: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print_step("Running Tests")
    
    try:
        # Run validation script
        result = subprocess.run([
            sys.executable, 'validate_system.py'
        ], capture_output=True, text=True, check=True)
        
        print_success("System validation passed")
        
        # Run basic tests if available
        if Path('run_tests.py').exists():
            result = subprocess.run([
                sys.executable, 'run_tests.py'
            ], capture_output=True, text=True, check=True)
            
            print_success("Basic tests passed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Tests failed: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Reports Service Deployment Script")
    print("This script will set up and validate the Reports Service")
    
    steps = [
        ("Python Version", check_python_version),
        ("Environment Setup", setup_environment),
        ("Dependencies", install_dependencies),
        ("Directories", setup_directories),
        ("MySQL Connection", check_mysql_connection),
        ("Database Initialization", initialize_database),
        ("Service Startup Test", test_service_startup),
        ("Tests", run_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print_error(f"Unexpected error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    print_step("Deployment Summary")
    
    if not failed_steps:
        print_success("🎉 Deployment completed successfully!")
        print("\nNext steps:")
        print("1. Review and update .env file with your specific configuration")
        print("2. Start the service: python -m src.main")
        print("3. Access GraphQL: http://localhost:8000/api/graphql")
        print("4. Access API docs: http://localhost:8000/docs")
        print("5. Check health: http://localhost:8000/health")
    else:
        print_error("❌ Deployment completed with errors!")
        print(f"Failed steps: {', '.join(failed_steps)}")
        print("\nPlease fix the errors and run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()