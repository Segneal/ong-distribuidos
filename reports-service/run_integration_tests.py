#!/usr/bin/env python3
"""
Integration test runner for reports-service.
This script runs integration tests to validate database connectivity, 
Excel generation, and SOAP integration.
"""
import sys
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_integration_tests():
    """Run integration tests using pytest."""
    print("🔧 Running Reports Service Integration Tests")
    print("=" * 60)
    
    # Change to the reports-service directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run pytest with integration marker
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_integration.py",
        "-v",
        "-m", "integration",
        "--tb=short",
        "--color=yes"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Failed to run integration tests: {e}")
        return False

def run_specific_test_class(test_class):
    """Run a specific test class."""
    print(f"🎯 Running {test_class} tests")
    print("-" * 40)
    
    cmd = [
        sys.executable, "-m", "pytest", 
        f"tests/test_integration.py::{test_class}",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Failed to run {test_class} tests: {e}")
        return False

def main():
    """Main test runner."""
    print("🚀 Reports Service Integration Test Suite")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Run specific test class if provided
        test_class = sys.argv[1]
        valid_classes = [
            "TestDatabaseIntegration",
            "TestExcelIntegration", 
            "TestSOAPIntegration",
            "TestServiceIntegration"
        ]
        
        if test_class in valid_classes:
            success = run_specific_test_class(test_class)
        else:
            print(f"❌ Invalid test class: {test_class}")
            print(f"Valid options: {', '.join(valid_classes)}")
            return 1
    else:
        # Run all integration tests
        success = run_integration_tests()
    
    if success:
        print(f"\n🎉 Integration tests completed successfully!")
        return 0
    else:
        print(f"\n⚠️  Some integration tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())