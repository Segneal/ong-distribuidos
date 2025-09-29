#!/usr/bin/env python3
"""
Test verification script for messaging service
Verifies that the test suite is properly configured and can run
"""
import sys
import os
from pathlib import Path
import importlib.util


def check_test_files():
    """Check that all test files exist and are importable"""
    test_files = [
        "tests/conftest.py",
        "tests/test_producers.py",
        "tests/test_consumers.py", 
        "tests/test_models.py",
        "tests/test_kafka_connection.py",
        "tests/test_message_validation.py",
        "tests/integration/conftest.py",
        "tests/integration/test_kafka_integration.py",
        "tests/integration/test_database_integration.py",
        "tests/integration/test_end_to_end_flows.py",
        "tests/integration/test_error_handling.py"
    ]
    
    missing_files = []
    import_errors = []
    
    for test_file in test_files:
        file_path = Path(__file__).parent / test_file
        
        # Check if file exists
        if not file_path.exists():
            missing_files.append(test_file)
            continue
        
        # Try to import the file
        try:
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        except Exception as e:
            import_errors.append((test_file, str(e)))
    
    return missing_files, import_errors


def check_dependencies():
    """Check that required test dependencies are available"""
    required_packages = [
        "pytest",
        "pytest_mock", 
        "pytest_cov",
        "unittest.mock"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "pytest_mock":
                import pytest_mock
            elif package == "pytest_cov":
                import pytest_cov
            elif package == "unittest.mock":
                import unittest.mock
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages


def check_test_configuration():
    """Check test configuration files"""
    config_files = [
        "pytest.ini",
        "run_unit_tests.py",
        "run_integration_tests.py"
    ]
    
    missing_configs = []
    
    for config_file in config_files:
        file_path = Path(__file__).parent / config_file
        if not file_path.exists():
            missing_configs.append(config_file)
    
    return missing_configs


def run_basic_test():
    """Run a basic test to verify pytest works"""
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "--collect-only", 
            "tests/test_models.py"
        ], 
        cwd=Path(__file__).parent,
        capture_output=True, 
        text=True,
        timeout=30
        )
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    """Main verification function"""
    print("Messaging Service Test Suite Verification")
    print("=" * 50)
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    all_good = True
    
    # Check test files
    print("\n1. Checking test files...")
    missing_files, import_errors = check_test_files()
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        all_good = False
    else:
        print("✅ All test files present")
    
    if import_errors:
        print(f"❌ Import errors in test files:")
        for file, error in import_errors:
            print(f"   {file}: {error}")
        all_good = False
    else:
        print("✅ All test files importable")
    
    # Check dependencies
    print("\n2. Checking test dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("   Install with: pip install pytest pytest-mock pytest-cov")
        all_good = False
    else:
        print("✅ All test dependencies available")
    
    # Check configuration
    print("\n3. Checking test configuration...")
    missing_configs = check_test_configuration()
    
    if missing_configs:
        print(f"❌ Missing config files: {missing_configs}")
        all_good = False
    else:
        print("✅ All configuration files present")
    
    # Run basic test
    print("\n4. Running basic test collection...")
    test_success, stdout, stderr = run_basic_test()
    
    if test_success:
        print("✅ Basic test collection successful")
        # Count collected tests
        if "collected" in stdout:
            import re
            match = re.search(r'(\d+) items? collected', stdout)
            if match:
                count = match.group(1)
                print(f"   Found {count} test items")
    else:
        print("❌ Basic test collection failed")
        if stderr:
            print(f"   Error: {stderr}")
        all_good = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("✅ Test suite verification PASSED")
        print("\nYou can now run tests with:")
        print("  python run_unit_tests.py")
        print("  python run_integration_tests.py")
        return 0
    else:
        print("❌ Test suite verification FAILED")
        print("\nPlease fix the issues above before running tests")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)