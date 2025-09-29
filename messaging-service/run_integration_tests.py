#!/usr/bin/env python3
"""
Integration test runner for messaging service
"""
import sys
import os
import subprocess
from pathlib import Path
import time


def check_kafka_availability():
    """Check if Kafka is available for testing"""
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers='localhost:9093',
            request_timeout_ms=5000
        )
        producer.close()
        return True
    except Exception:
        return False


def check_database_availability():
    """Check if test database is available"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv('TEST_DB_HOST', 'localhost'),
            port=os.getenv('TEST_DB_PORT', '5432'),
            database=os.getenv('TEST_DB_NAME', 'test_ong_management'),
            user=os.getenv('TEST_DB_USER', 'test_user'),
            password=os.getenv('TEST_DB_PASSWORD', 'test_pass'),
            connect_timeout=5
        )
        conn.close()
        return True
    except Exception:
        return False


def run_integration_tests():
    """Run integration tests with proper setup"""
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["KAFKA_TEST_BROKERS"] = os.getenv("KAFKA_TEST_BROKERS", "localhost:9093")
    os.environ["ORGANIZATION_ID"] = "test-org"
    os.environ["KAFKA_GROUP_ID"] = "test-integration-group"
    
    # Database configuration
    os.environ["TEST_DB_HOST"] = os.getenv("TEST_DB_HOST", "localhost")
    os.environ["TEST_DB_PORT"] = os.getenv("TEST_DB_PORT", "5432")
    os.environ["TEST_DB_NAME"] = os.getenv("TEST_DB_NAME", "test_ong_management")
    os.environ["TEST_DB_USER"] = os.getenv("TEST_DB_USER", "test_user")
    os.environ["TEST_DB_PASSWORD"] = os.getenv("TEST_DB_PASSWORD", "test_pass")
    
    print("Checking prerequisites for integration tests...")
    
    # Check Kafka availability
    if not check_kafka_availability():
        print("WARNING: Kafka not available at localhost:9093")
        print("Integration tests requiring Kafka will be skipped")
        print("To run full integration tests, ensure Kafka is running on localhost:9093")
    else:
        print("✓ Kafka is available")
    
    # Check database availability
    if not check_database_availability():
        print("WARNING: Test database not available")
        print("Integration tests requiring database will be skipped")
        print("To run full integration tests, ensure test database is configured")
    else:
        print("✓ Test database is available")
    
    # Run pytest with integration tests
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
        "--cov=messaging",
        "--cov-report=term-missing",
        "--cov-append",  # Append to existing coverage
        "-m", "integration",
        "--durations=10"
    ]
    
    print("\nRunning integration tests...")
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


def run_all_tests():
    """Run both unit and integration tests"""
    
    print("=" * 60)
    print("Running Unit Tests")
    print("=" * 60)
    
    # Run unit tests first
    unit_result = subprocess.run([
        sys.executable, "run_unit_tests.py"
    ], cwd=Path(__file__).parent)
    
    print("\n" + "=" * 60)
    print("Running Integration Tests")
    print("=" * 60)
    
    # Run integration tests
    integration_result = run_integration_tests()
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    print(f"Unit Tests: {'PASSED' if unit_result.returncode == 0 else 'FAILED'}")
    print(f"Integration Tests: {'PASSED' if integration_result == 0 else 'FAILED'}")
    
    # Return non-zero if any tests failed
    return max(unit_result.returncode, integration_result)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run messaging service tests")
    parser.add_argument("--integration-only", action="store_true", 
                       help="Run only integration tests")
    parser.add_argument("--all", action="store_true", 
                       help="Run both unit and integration tests")
    
    args = parser.parse_args()
    
    if args.all:
        exit_code = run_all_tests()
    elif args.integration_only:
        exit_code = run_integration_tests()
    else:
        # Default: run integration tests only
        exit_code = run_integration_tests()
    
    sys.exit(exit_code)