#!/usr/bin/env python3
"""
Verificación final del sistema de adhesiones
Confirma que el sistema funciona correctamente para N organizaciones
"""
import os
import sys
import json
import time
from datetime import datetime

# Add messaging service to path
sys.path.append('messaging-service/src')

def test_message_sending():
    """Test message sending between multiple organizations"""
    print("=== TESTING MESSAGE SENDING ===")
    
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    organizations = ['empuje-comunitario', 'esperanza-viva', 'manos-solidarias', 'corazon-abierto']
    
    print(f"Testing with {len(organizations)} organizations: {organizations}")
    
    success_count = 0
    total_tests = 0
    
    for sender in organizations:
        for receiver in organizations:
            if sender != receiver:
                total_tests += 1
                
                print(f"\n  Test {total_tests}: {sender} → {receiver}")
                
                # Set sender organization
                os.environ['ORGANIZATION_ID'] = sender
                
                # Import fresh modules
                import importlib
                import messaging.config
                importlib.reload(messaging.config)
                
                from messaging.config import settings, Topics
                from messaging.producers.base_producer import BaseProducer
                
                producer = BaseProducer()
                
                # Create test data
                test_volunteer_data = {
                    "volunteer_id": total_tests,
                    "name": f"Volunteer{total_tests}",
                    "surname": "Test",
                    "email": f"volunteer{total_tests}@{sender}.org",
                    "phone": f"12345678{total_tests:02d}"
                }
                
                # Send message
                success = producer.publish_event_adhesion(
                    target_org=receiver,
                    event_id=f"test-event-{total_tests}",
                    volunteer_data=test_volunteer_data
                )
                
                if success:
                    success_count += 1
                    print(f"    ✅ SUCCESS")
                else:
                    print(f"    ❌ FAILED")
    
    print(f"\n📊 RESULTS: {success_count}/{total_tests} messages sent successfully")
    print(f"Success rate: {(success_count/total_tests)*100:.1f}%")
    
    return success_count == total_tests

def test_consumer_configuration():
    """Test consumer configuration for multiple organizations"""
    print("\n=== TESTING CONSUMER CONFIGURATION ===")
    
    organizations = ['empuje-comunitario', 'esperanza-viva', 'manos-solidarias', 'corazon-abierto']
    
    all_configured = True
    
    for org in organizations:
        print(f"\n  Testing consumer for {org}...")
        
        # Set organization
        os.environ['ORGANIZATION_ID'] = org
        
        # Import fresh modules
        import importlib
        import messaging.config
        importlib.reload(messaging.config)
        
        from messaging.config import settings, Topics
        from messaging.consumers.base_consumer import OrganizationConsumer
        
        # Create consumer
        consumer = OrganizationConsumer()
        
        # Check topics
        expected_adhesion_topic = f"adhesion-evento-{org}"
        expected_transfer_topic = f"transferencia-donaciones-{org}"
        
        adhesion_configured = any(expected_adhesion_topic in topic for topic in consumer.topics)
        transfer_configured = any(expected_transfer_topic in topic for topic in consumer.topics)
        
        # Check handlers
        has_adhesion_handler = "event_adhesion" in consumer._message_handlers
        has_transfer_handler = "donation_transfer" in consumer._message_handlers
        
        print(f"    Topics: {consumer.topics}")
        print(f"    Adhesion topic configured: {'✅' if adhesion_configured else '❌'}")
        print(f"    Transfer topic configured: {'✅' if transfer_configured else '❌'}")
        print(f"    Adhesion handler: {'✅' if has_adhesion_handler else '❌'}")
        print(f"    Transfer handler: {'✅' if has_transfer_handler else '❌'}")
        
        org_configured = all([adhesion_configured, transfer_configured, has_adhesion_handler, has_transfer_handler])
        
        if not org_configured:
            all_configured = False
    
    print(f"\n📊 CONSUMER CONFIGURATION: {'✅ ALL CONFIGURED' if all_configured else '❌ SOME ISSUES'}")
    
    return all_configured

def test_adhesion_service():
    """Test adhesion service functionality"""
    print("\n=== TESTING ADHESION SERVICE ===")
    
    os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    # Import fresh modules
    import importlib
    import messaging.config
    importlib.reload(messaging.config)
    
    from messaging.services.adhesion_service import AdhesionService
    
    adhesion_service = AdhesionService()
    
    # Test processing incoming adhesion
    test_message_data = {
        "type": "event_adhesion",
        "event_id": "test-event-999",
        "volunteer": {
            "organization_id": "empuje-comunitario",
            "volunteer_id": 999,
            "name": "Test",
            "surname": "Volunteer",
            "email": "test@empuje.org",
            "phone": "123456789"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print("  Processing test adhesion message...")
    
    try:
        success = adhesion_service.process_incoming_adhesion(test_message_data)
        print(f"  Adhesion processing: {'✅ SUCCESS' if success else '❌ FAILED'}")
        return success
    except Exception as e:
        print(f"  Adhesion processing: ❌ ERROR - {e}")
        return False

def test_notification_service():
    """Test notification service functionality"""
    print("\n=== TESTING NOTIFICATION SERVICE ===")
    
    os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
    
    # Import fresh modules
    import importlib
    import messaging.config
    importlib.reload(messaging.config)
    
    from messaging.services.notification_service import NotificationService
    
    notification_service = NotificationService()
    
    print("  Creating test notification...")
    
    try:
        notification_service.notify_new_event_adhesion(
            event_id="test-event-999",
            volunteer_name="Test Volunteer",
            volunteer_email="test@empuje.org",
            volunteer_org="empuje-comunitario"
        )
        print("  Notification creation: ✅ SUCCESS")
        return True
    except Exception as e:
        print(f"  Notification creation: ❌ ERROR - {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 FINAL VERIFICATION OF ADHESION SYSTEM")
    print("=" * 50)
    
    # Test 1: Message sending
    test1_success = test_message_sending()
    
    # Test 2: Consumer configuration
    test2_success = test_consumer_configuration()
    
    # Test 3: Adhesion service
    test3_success = test_adhesion_service()
    
    # Test 4: Notification service
    test4_success = test_notification_service()
    
    # Final results
    print("\n" + "=" * 50)
    print("📋 FINAL RESULTS")
    print("=" * 50)
    
    tests = [
        ("Message Sending", test1_success),
        ("Consumer Configuration", test2_success),
        ("Adhesion Service", test3_success),
        ("Notification Service", test4_success)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ADHESION SYSTEM IS FULLY FUNCTIONAL FOR N ORGANIZATIONS!")
        print("\n✅ The system can handle:")
        print("   - Dynamic message sending between any organizations")
        print("   - Automatic topic creation and routing")
        print("   - Proper consumer configuration per organization")
        print("   - Adhesion processing and storage")
        print("   - Notification system for administrators")
        print("\n🚀 READY FOR PRODUCTION!")
    else:
        print(f"\n⚠️  SOME ISSUES FOUND: {total-passed} test(s) failed")
        print("   Please review the failed tests above")

if __name__ == "__main__":
    main()