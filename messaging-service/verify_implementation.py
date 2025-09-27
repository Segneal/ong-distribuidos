#!/usr/bin/env python3
"""
Verification script for donation request implementation
Tests the core functionality without requiring Kafka/Database connections
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_models():
    """Test the data models"""
    print("=== Testing Data Models ===")
    
    try:
        from models import DonationRequest, DonationItem, RequestCancellation
        
        # Test DonationItem
        item = DonationItem(category="ALIMENTOS", description="Conservas de atún")
        item_dict = item.to_dict()
        item_restored = DonationItem.from_dict(item_dict)
        
        assert item.category == item_restored.category
        assert item.description == item_restored.description
        print("✓ DonationItem serialization works")
        
        # Test DonationRequest
        request = DonationRequest(
            organization_id="test-org",
            request_id="REQ-001",
            donations=[item],
            timestamp=datetime.utcnow().isoformat()
        )
        
        request_dict = request.to_dict()
        request_restored = DonationRequest.from_dict(request_dict)
        
        assert request.organization_id == request_restored.organization_id
        assert request.request_id == request_restored.request_id
        assert len(request.donations) == len(request_restored.donations)
        print("✓ DonationRequest serialization works")
        
        # Test RequestCancellation
        cancellation = RequestCancellation(
            organization_id="test-org",
            request_id="REQ-001",
            timestamp=datetime.utcnow().isoformat()
        )
        
        cancel_dict = cancellation.to_dict()
        cancel_restored = RequestCancellation.from_dict(cancel_dict)
        
        assert cancellation.organization_id == cancel_restored.organization_id
        assert cancellation.request_id == cancel_restored.request_id
        print("✓ RequestCancellation serialization works")
        
        return True
        
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False

def test_schemas():
    """Test the JSON schemas"""
    print("\n=== Testing JSON Schemas ===")
    
    try:
        from schemas import MessageValidator
        
        # Test valid donation request
        valid_request = {
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Conservas de atún"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        MessageValidator.validate_message("donation_request", valid_request)
        print("✓ Valid donation request passes validation")
        
        # Test invalid donation request (missing field)
        invalid_request = {
            "organization_id": "test-org",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Conservas de atún"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            MessageValidator.validate_message("donation_request", invalid_request)
            print("✗ Invalid request should fail validation")
            return False
        except:
            print("✓ Invalid donation request fails validation as expected")
        
        # Test valid cancellation
        valid_cancellation = {
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        MessageValidator.validate_message("request_cancellation", valid_cancellation)
        print("✓ Valid cancellation passes validation")
        
        return True
        
    except Exception as e:
        print(f"✗ Schema test failed: {e}")
        return False

def test_producer_logic():
    """Test producer logic without Kafka"""
    print("\n=== Testing Producer Logic ===")
    
    try:
        from donation_request_producer import DonationRequestProducer
        
        # Mock the Kafka publishing
        class MockProducer(DonationRequestProducer):
            def _publish_message(self, topic, message, key=None):
                print(f"  Mock publish to {topic}: {message.get('type', 'unknown')}")
                return True
            
            def _store_request_in_database(self, request_id, donations, user_id):
                print(f"  Mock store in DB: {request_id}")
                return {"success": True}
            
            def _update_request_status(self, request_id, status, user_id=None):
                print(f"  Mock update status: {request_id} -> {status}")
                return {"success": True}
            
            def _get_request_from_database(self, request_id):
                return {
                    "solicitud_id": request_id,
                    "donaciones": [],
                    "estado": "ACTIVA",
                    "fecha_creacion": datetime.utcnow(),
                    "notas": None
                }
        
        producer = MockProducer()
        
        # Test valid request creation
        donations = [
            {"category": "ALIMENTOS", "description": "Conservas"},
            {"category": "ROPA", "description": "Ropa de abrigo"}
        ]
        
        result = producer.create_donation_request(donations, user_id=1)
        
        if result["success"]:
            print("✓ Donation request creation logic works")
            request_id = result["request_id"]
        else:
            print(f"✗ Request creation failed: {result['error']}")
            return False
        
        # Test request cancellation
        cancel_result = producer.cancel_donation_request(request_id, user_id=1)
        
        if cancel_result["success"]:
            print("✓ Request cancellation logic works")
        else:
            print(f"✗ Cancellation failed: {cancel_result['error']}")
            return False
        
        # Test validation
        invalid_donations = [{"category": "INVALID", "description": "Test"}]
        invalid_result = producer.create_donation_request(invalid_donations, user_id=1)
        
        if not invalid_result["success"]:
            print("✓ Invalid donations are rejected")
        else:
            print("✗ Invalid donations should be rejected")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Producer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_consumer_logic():
    """Test consumer logic without Kafka"""
    print("\n=== Testing Consumer Logic ===")
    
    try:
        from donation_request_consumer import DonationRequestConsumer
        from request_cancellation_consumer import RequestCancellationConsumer
        
        # Mock the database operations
        class MockRequestConsumer(DonationRequestConsumer):
            def _store_external_request(self, donation_request):
                print(f"  Mock store external: {donation_request.organization_id}/{donation_request.request_id}")
                return True
            
            def _log_message_processing(self, message, status, error_detail=None):
                print(f"  Mock log: {status}")
        
        class MockCancellationConsumer(RequestCancellationConsumer):
            def _process_request_cancellation(self, cancellation):
                print(f"  Mock cancel: {cancellation.organization_id}/{cancellation.request_id}")
                return True
            
            def _log_message_processing(self, message, status, error_detail=None):
                print(f"  Mock log: {status}")
        
        # Test donation request processing
        request_consumer = MockRequestConsumer()
        
        external_message = {
            "message_id": "test-001",
            "message_type": "donation_request",
            "organization_id": "external-org",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "organization_id": "external-org",
                "request_id": "EXT-REQ-001",
                "donations": [
                    {"category": "JUGUETES", "description": "Juegos educativos"}
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if request_consumer.process_message(external_message):
            print("✓ External request processing logic works")
        else:
            print("✗ External request processing failed")
            return False
        
        # Test cancellation processing
        cancellation_consumer = MockCancellationConsumer()
        
        cancellation_message = {
            "message_id": "test-cancel-001",
            "message_type": "request_cancellation",
            "organization_id": "external-org",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "organization_id": "external-org",
                "request_id": "EXT-REQ-001",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if cancellation_consumer.process_message(cancellation_message):
            print("✓ Cancellation processing logic works")
        else:
            print("✗ Cancellation processing failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Consumer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_structure():
    """Test API server structure"""
    print("\n=== Testing API Structure ===")
    
    try:
        from api_server import app
        
        # Check if Flask app was created
        if app:
            print("✓ Flask app created successfully")
        else:
            print("✗ Flask app creation failed")
            return False
        
        # Check routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = [
            '/health',
            '/api/createDonationRequest',
            '/api/getActiveRequests',
            '/api/cancelDonationRequest',
            '/api/getExternalRequests'
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"✓ Route {route} exists")
            else:
                print(f"✗ Route {route} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ API structure test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🔍 Verifying Donation Request Implementation")
    print("=" * 50)
    
    tests = [
        test_models,
        test_schemas,
        test_producer_logic,
        test_consumer_logic,
        test_api_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verification tests passed!")
        print("\n✅ Implementation Summary:")
        print("  • Donation request producer with Kafka publishing")
        print("  • External request consumer with database storage")
        print("  • Request cancellation producer and consumer")
        print("  • JSON schema validation for all message types")
        print("  • HTTP API endpoints for API Gateway integration")
        print("  • Database integration with proper error handling")
        print("  • Message audit logging for compliance")
        return True
    else:
        print("❌ Some verification tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)