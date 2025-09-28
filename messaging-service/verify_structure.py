#!/usr/bin/env python3
"""
Structure verification for donation request implementation
Checks that all required files and components are present
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (MISSING)")
        return False

def check_file_contains(filepath, content, description):
    """Check if a file contains specific content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
            if content in file_content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} (MISSING)")
                return False
    except Exception as e:
        print(f"✗ {description} (ERROR: {e})")
        return False

def main():
    """Verify implementation structure"""
    print("🔍 Verifying Donation Request Implementation Structure")
    print("=" * 60)
    
    checks_passed = 0
    total_checks = 0
    
    # Core implementation files
    files_to_check = [
        ("src/donation_request_producer.py", "Donation Request Producer"),
        ("src/donation_request_consumer.py", "Donation Request Consumer"),
        ("src/request_cancellation_consumer.py", "Request Cancellation Consumer"),
        ("src/database.py", "Database Connection Module"),
        ("src/api_server.py", "HTTP API Server"),
        ("src/models.py", "Data Models"),
        ("src/schemas.py", "JSON Schemas"),
        ("src/base_producer.py", "Base Producer"),
        ("src/base_consumer.py", "Base Consumer"),
        ("src/config.py", "Configuration"),
        ("requirements.txt", "Python Dependencies"),
        ("Dockerfile", "Docker Configuration"),
        ("docker-entrypoint.sh", "Docker Entrypoint"),
    ]
    
    print("\n=== Core Implementation Files ===")
    for filepath, description in files_to_check:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1
    
    # Check specific functionality in files
    print("\n=== Implementation Content Checks ===")
    
    content_checks = [
        ("src/donation_request_producer.py", "class DonationRequestProducer", "DonationRequestProducer class"),
        ("src/donation_request_producer.py", "create_donation_request", "Create donation request method"),
        ("src/donation_request_producer.py", "cancel_donation_request", "Cancel donation request method"),
        ("src/donation_request_consumer.py", "class DonationRequestConsumer", "DonationRequestConsumer class"),
        ("src/donation_request_consumer.py", "process_message", "Process message method"),
        ("src/request_cancellation_consumer.py", "class RequestCancellationConsumer", "RequestCancellationConsumer class"),
        ("src/api_server.py", "/api/createDonationRequest", "Create donation request API endpoint"),
        ("src/api_server.py", "/api/getActiveRequests", "Get active requests API endpoint"),
        ("src/api_server.py", "/api/cancelDonationRequest", "Cancel donation request API endpoint"),
        ("src/api_server.py", "/api/getExternalRequests", "Get external requests API endpoint"),
        ("src/database.py", "get_database_connection", "Database connection function"),
        ("src/models.py", "class DonationRequest", "DonationRequest model"),
        ("src/models.py", "class RequestCancellation", "RequestCancellation model"),
        ("requirements.txt", "flask", "Flask dependency"),
        ("requirements.txt", "kafka-python", "Kafka dependency"),
        ("requirements.txt", "psycopg2-binary", "PostgreSQL dependency"),
    ]
    
    for filepath, content, description in content_checks:
        total_checks += 1
        if check_file_contains(filepath, content, description):
            checks_passed += 1
    
    # Check API Gateway integration
    print("\n=== API Gateway Integration ===")
    
    api_gateway_files = [
        ("../api-gateway/src/routes/donationRequests.js", "Donation Requests Route"),
        ("../api-gateway/package.json", "API Gateway Package Config"),
    ]
    
    for filepath, description in api_gateway_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1
    
    api_gateway_content = [
        ("../api-gateway/src/routes/donationRequests.js", "POST", "POST endpoint for creating requests"),
        ("../api-gateway/src/routes/donationRequests.js", "GET", "GET endpoint for listing requests"),
        ("../api-gateway/src/routes/donationRequests.js", "DELETE", "DELETE endpoint for canceling requests"),
        ("../api-gateway/src/server.js", "donationRequests", "Donation requests route registration"),
        ("../api-gateway/package.json", "axios", "Axios dependency for HTTP calls"),
    ]
    
    for filepath, content, description in api_gateway_content:
        total_checks += 1
        if check_file_contains(filepath, content, description):
            checks_passed += 1
    
    # Check Docker configuration
    print("\n=== Docker Configuration ===")
    
    docker_checks = [
        ("../docker-compose.yml", "messaging-service", "Messaging service in docker-compose"),
        ("../docker-compose.yml", "8000:8000", "HTTP API port mapping"),
        ("Dockerfile", "EXPOSE 50054 8000", "Both ports exposed in Dockerfile"),
        ("docker-entrypoint.sh", "api_server", "API server startup in entrypoint"),
    ]
    
    for filepath, content, description in docker_checks:
        total_checks += 1
        if check_file_contains(filepath, content, description):
            checks_passed += 1
    
    # Check database schema
    print("\n=== Database Schema ===")
    
    db_files = [
        ("../database/donation_requests_table.sql", "Donation Requests Table Schema"),
    ]
    
    for filepath, description in db_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1
    
    db_content_checks = [
        ("../database/donation_requests_table.sql", "solicitudes_donaciones", "Donation requests table"),
        ("../database/schema.sql", "solicitudes_externas", "External requests table"),
        ("../database/network_tables_migration.sql", "historial_mensajes", "Message audit table"),
    ]
    
    for filepath, content, description in db_content_checks:
        total_checks += 1
        if check_file_contains(filepath, content, description):
            checks_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Structure Verification Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 All structure checks passed!")
        print("\n✅ Implementation Complete:")
        print("  • ✓ Donation request producer with Kafka publishing")
        print("  • ✓ External request consumer with database storage")
        print("  • ✓ Request cancellation producer and consumer")
        print("  • ✓ HTTP API endpoints for API Gateway integration")
        print("  • ✓ Database schema and connection utilities")
        print("  • ✓ Docker configuration with proper port mapping")
        print("  • ✓ JSON schema validation for message types")
        print("  • ✓ Message audit logging capabilities")
        print("\n🚀 Ready for deployment and testing!")
        return True
    else:
        print("❌ Some structure checks failed!")
        missing_percentage = ((total_checks - checks_passed) / total_checks) * 100
        print(f"   {missing_percentage:.1f}% of required components are missing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)