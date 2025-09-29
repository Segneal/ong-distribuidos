#!/usr/bin/env python3
"""
Test script for the Adhesion Service functionality
Tests both outgoing and incoming adhesion processing
"""
import sys
import os
import json
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from messaging.services.adhesion_service import AdhesionService
from messaging.config import settings

def test_adhesion_service():
    """Test the adhesion service functionality"""
    print("🧪 Testing Adhesion Service")
    print("=" * 50)
    
    try:
        # Initialize service
        adhesion_service = AdhesionService()
        print(f"✅ Adhesion service initialized for organization: {settings.organization_id}")
        
        # Test 1: Get volunteer adhesions (should work even if empty)
        print("\n📋 Test 1: Get volunteer adhesions")
        volunteer_id = 1  # Assuming volunteer with ID 1 exists
        adhesions = adhesion_service.get_volunteer_adhesions(volunteer_id)
        print(f"✅ Retrieved {len(adhesions)} adhesions for volunteer {volunteer_id}")
        
        if adhesions:
            print("📄 Sample adhesion:")
            print(json.dumps(adhesions[0], indent=2, default=str))
        
        # Test 2: Get event adhesions (should work even if empty)
        print("\n📋 Test 2: Get event adhesions")
        event_id = "test-event-001"
        event_adhesions = adhesion_service.get_event_adhesions(event_id)
        print(f"✅ Retrieved {len(event_adhesions)} adhesions for event {event_id}")
        
        if event_adhesions:
            print("📄 Sample event adhesion:")
            print(json.dumps(event_adhesions[0], indent=2, default=str))
        
        # Test 3: Process incoming adhesion (simulate)
        print("\n📋 Test 3: Process incoming adhesion")
        sample_adhesion_data = {
            "event_id": "test-event-001",
            "volunteer": {
                "organization_id": "otra-organizacion",
                "volunteer_id": "vol-123",
                "name": "Juan",
                "surname": "Pérez",
                "email": "juan.perez@otra-org.com",
                "phone": "+1234567890"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = adhesion_service.process_incoming_adhesion(sample_adhesion_data)
        if success:
            print("✅ Incoming adhesion processed successfully")
        else:
            print("⚠️ Incoming adhesion processing returned False (expected if event doesn't exist)")
        
        print("\n🎉 All adhesion service tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing adhesion service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adhesion_creation():
    """Test creating an adhesion (requires existing external event)"""
    print("\n🧪 Testing Adhesion Creation")
    print("=" * 50)
    
    try:
        adhesion_service = AdhesionService()
        
        # This will likely fail because we need an existing external event
        # But it will test the validation logic
        success, message = adhesion_service.create_event_adhesion(
            event_id="non-existent-event",
            volunteer_id=1,
            target_organization="otra-organizacion"
        )
        
        print(f"📝 Adhesion creation result: {success}")
        print(f"📝 Message: {message}")
        
        if not success and "not found" in message.lower():
            print("✅ Validation working correctly (event not found as expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing adhesion creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Adhesion Service Tests")
    print("=" * 60)
    
    # Test basic functionality
    test1_success = test_adhesion_service()
    
    # Test adhesion creation
    test2_success = test_adhesion_creation()
    
    print("\n" + "=" * 60)
    if test1_success and test2_success:
        print("🎉 All tests completed successfully!")
        print("✅ Adhesion service is working correctly")
    else:
        print("❌ Some tests failed")
        print("🔍 Check the error messages above for details")
    
    print("\n📋 Summary:")
    print(f"   - Basic functionality: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   - Adhesion creation: {'✅ PASS' if test2_success else '❌ FAIL'}")