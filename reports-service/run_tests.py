#!/usr/bin/env python3
"""
Test runner script for reports-service.
This script runs basic validation tests to ensure the system is properly configured.
"""
import sys
import os
import subprocess

def run_validation_tests():
    """Run the existing validation test scripts."""
    print("🧪 Running Reports Service Validation Tests")
    print("=" * 50)
    
    test_scripts = [
        "test_database_connection.py",
        "test_donation_service.py", 
        "test_event_service.py",
        "test_filter_service.py",
        "test_graphql_setup.py",
        "test_soap_client.py"
    ]
    
    results = {}
    
    for script in test_scripts:
        print(f"\n📋 Running {script}...")
        print("-" * 30)
        
        try:
            result = subprocess.run([sys.executable, script], 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=os.path.dirname(__file__))
            
            if result.returncode == 0:
                print(f"✅ {script} - PASSED")
                results[script] = "PASSED"
            else:
                print(f"❌ {script} - FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                results[script] = "FAILED"
                
        except Exception as e:
            print(f"❌ {script} - ERROR: {e}")
            results[script] = "ERROR"
    
    return results

def run_pytest_tests():
    """Run pytest tests if available."""
    print(f"\n🔬 Running Pytest Tests")
    print("-" * 30)
    
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, 
                              text=True,
                              cwd=os.path.dirname(__file__))
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Pytest execution failed: {e}")
        return False

def main():
    """Main test runner."""
    print("🚀 Reports Service Test Suite")
    print("=" * 50)
    
    # Run validation tests
    validation_results = run_validation_tests()
    
    # Run pytest tests
    pytest_success = run_pytest_tests()
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for result in validation_results.values() if result == "PASSED")
    total = len(validation_results)
    
    print(f"Validation Tests: {passed}/{total} passed")
    print(f"Pytest Tests: {'PASSED' if pytest_success else 'FAILED'}")
    
    for script, result in validation_results.items():
        status_emoji = "✅" if result == "PASSED" else "❌"
        print(f"  {status_emoji} {script}: {result}")
    
    # Overall result
    overall_success = (passed == total) and pytest_success
    
    if overall_success:
        print(f"\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())