"""
Test script for donation request functionality
"""
import json
import time
from datetime import datetime

from .donation_request_producer import DonationRequestProducer
from .donation_request_consumer import DonationRequestConsumer
from .request_cancellation_consumer import RequestCancellationConsumer
from .database import test_database_connection, initialize_database_tables
from .config import settings

def test_donation_request_flow():
    """Test the complete donation request flow"""
    print("=== Testing Donation Request Flow ===")
    
    # Test database connection
    print("1. Testing database connection...")
    if test_database_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
        return False
    
    # Initialize database tables
    print("2. Initializing database tables...")
    try:
        initialize_database_tables()
        print("✓ Database tables initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    
    # Test donation request creation
    print("3. Testing donation request creation...")
    producer = DonationRequestProducer()
    
    test_donations = [
        {
            "category": "ALIMENTOS",
            "description": "Conservas de atún"
        },
        {
            "category": "ROPA",
            "description": "Ropa de abrigo para niños"
        }
    ]
    
    result = producer.create_donation_request(test_donations, user_id=1)
    
    if result["success"]:
        print(f"✓ Donation request created: {result['request_id']}")
        request_id = result["request_id"]
    else:
        print(f"✗ Donation request creation failed: {result['error']}")
        return False
    
    # Test getting active requests
    print("4. Testing get active requests...")
    active_requests = producer.get_active_requests()
    print(f"✓ Found {len(active_requests)} active requests")
    
    # Test request cancellation
    print("5. Testing request cancellation...")
    cancel_result = producer.cancel_donation_request(request_id, user_id=1)
    
    if cancel_result["success"]:
        print("✓ Donation request cancelled successfully")
    else:
        print(f"✗ Request cancellation failed: {cancel_result['error']}")
        return False
    
    # Test external request processing
    print("6. Testing external request processing...")
    consumer = DonationRequestConsumer()
    
    # Simulate external message
    external_message = {
        "message_id": "test-msg-001",
        "message_type": "donation_request",
        "organization_id": "test-org",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "organization_id": "test-org",
            "request_id": "EXT-REQ-001",
            "donations": [
                {
                    "category": "JUGUETES",
                    "description": "Juegos educativos"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if consumer.process_message(external_message):
        print("✓ External request processed successfully")
    else:
        print("✗ External request processing failed")
        return False
    
    # Test getting external requests
    print("7. Testing get external requests...")
    external_requests = consumer.get_external_requests()
    print(f"✓ Found {len(external_requests)} external requests")
    
    # Test cancellation processing
    print("8. Testing cancellation processing...")
    cancellation_consumer = RequestCancellationConsumer()
    
    # Simulate cancellation message
    cancellation_message = {
        "message_id": "test-cancel-001",
        "message_type": "request_cancellation",
        "organization_id": "test-org",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "organization_id": "test-org",
            "request_id": "EXT-REQ-001",
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if cancellation_consumer.process_message(cancellation_message):
        print("✓ Cancellation processed successfully")
    else:
        print("✗ Cancellation processing failed")
        return False
    
    print("=== All tests passed! ===")
    return True

def test_validation():
    """Test input validation"""
    print("=== Testing Input Validation ===")
    
    producer = DonationRequestProducer()
    
    # Test invalid donations
    print("1. Testing invalid donations...")
    
    # Empty donations
    result = producer.create_donation_request([], user_id=1)
    if not result["success"]:
        print("✓ Empty donations rejected")
    else:
        print("✗ Empty donations should be rejected")
        return False
    
    # Invalid category
    invalid_donations = [
        {
            "category": "INVALID_CATEGORY",
            "description": "Test item"
        }
    ]
    
    result = producer.create_donation_request(invalid_donations, user_id=1)
    if not result["success"]:
        print("✓ Invalid category rejected")
    else:
        print("✗ Invalid category should be rejected")
        return False
    
    # Missing description
    missing_desc_donations = [
        {
            "category": "ALIMENTOS"
        }
    ]
    
    result = producer.create_donation_request(missing_desc_donations, user_id=1)
    if not result["success"]:
        print("✓ Missing description rejected")
    else:
        print("✗ Missing description should be rejected")
        return False
    
    print("=== Validation tests passed! ===")
    return True

if __name__ == "__main__":
    print(f"Organization ID: {settings.organization_id}")
    print(f"Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    print()
    
    # Run tests
    if test_validation() and test_donation_request_flow():
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)