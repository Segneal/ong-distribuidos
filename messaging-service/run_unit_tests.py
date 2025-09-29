#!/usr/bin/env python3
"""
Unit test runner for messaging service
"""
import sys
import os
import subprocess
from pathlib import Path

def run_unit_tests():
    """Run unit tests with coverage reporting"""
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Also set PYTHONPATH environment variable
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if current_pythonpath:
        os.environ["PYTHONPATH"] = f"{src_path}{os.pathsep}{current_pythonpath}"
    else:
        os.environ["PYTHONPATH"] = str(src_path)
    
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["KAFKA_BROKERS"] = "localhost:9092"
    os.environ["ORGANIZATION_ID"] = "test-org"
    os.environ["KAFKA_GROUP_ID"] = "test-group"
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=messaging",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=80",
        "-m", "not integration"  # Only run unit tests, not integration tests
    ]
    
    print("Running unit tests...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_unit_tests()
    sys.exit(exit_code)