#!/usr/bin/env python3
"""
Test script for ONG Management System models
"""
import os
import sys
from datetime import datetime, timedelta

# Add shared directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import User, UserRole
from models.donation import Donation, DonationCategory
from models.event import Event
from models.external import ExternalDonationRequest, ExternalEvent

def test_user_model():
    """Test User model basic operations"""
    print("Testing User model...")
    
    try:
        # Test creating a user
        user = User(
            nombre_usuario="test_user",
            nombre="Test",
            apellido="User",
            email="test@example.com",
            password_hash="hashed_password",
            rol=UserRole.VOLUNTARIO
        )
        
        print(f"Created user: {user}")
        
        # Test getting all users
        users = User.get_all()
        print(f"Found {len(users)} users in database")
        
        # Test getting users by role
        presidentes = User.get_by_role(UserRole.PRESIDENTE)
        print(f"Found {len(presidentes)} presidents")
        
        print("User model test completed successfully")
        
    except Exception as e:
        print(f"User model test failed: {e}")

def test_donation_model():
    """Test Donation model basic operations"""
    print("\nTesting Donation model...")
    
    try:
        # Test creating a donation
        donation = Donation(
            categoria=DonationCategory.ALIMENTOS,
            descripcion="Test donation",
            cantidad=10
        )
        
        print(f"Created donation: {donation}")
        
        # Test getting all donations
        donations = Donation.get_all()
        print(f"Found {len(donations)} donations in database")
        
        # Test getting by category
        alimentos = Donation.get_by_category(DonationCategory.ALIMENTOS)
        print(f"Found {len(alimentos)} food donations")
        
        # Test inventory summary
        summary = Donation.get_inventory_summary()
        print(f"Inventory summary: {summary}")
        
        print("Donation model test completed successfully")
        
    except Exception as e:
        print(f"Donation model test failed: {e}")

def test_event_model():
    """Test Event model basic operations"""
    print("\nTesting Event model...")
    
    try:
        # Test creating an event
        event = Event(
            nombre="Test Event",
            descripcion="Test event description",
            fecha_evento=datetime.now() + timedelta(days=7)
        )
        
        print(f"Created event: {event}")
        
        # Test getting all events
        events = Event.get_all()
        print(f"Found {len(events)} events in database")
        
        # Test getting future events
        future_events = Event.get_future_events()
        print(f"Found {len(future_events)} future events")
        
        # Test getting past events
        past_events = Event.get_past_events()
        print(f"Found {len(past_events)} past events")
        
        print("Event model test completed successfully")
        
    except Exception as e:
        print(f"Event model test failed: {e}")

def test_external_models():
    """Test External models basic operations"""
    print("\nTesting External models...")
    
    try:
        # Test external donation request
        request = ExternalDonationRequest(
            organizacion_solicitante="test-org",
            solicitud_id="TEST-001",
            donaciones=[
                {"categoria": "ALIMENTOS", "descripcion": "Test food"}
            ]
        )
        
        print(f"Created external request: {request}")
        
        # Test external event
        external_event = ExternalEvent(
            organizacion_id="test-org",
            evento_id="EVT-001",
            nombre="Test External Event",
            descripcion="Test description",
            fecha_evento=datetime.now() + timedelta(days=10)
        )
        
        print(f"Created external event: {external_event}")
        
        # Test getting active requests
        active_requests = ExternalDonationRequest.get_active_requests()
        print(f"Found {len(active_requests)} active requests")
        
        # Test getting active future events
        active_events = ExternalEvent.get_active_future_events()
        print(f"Found {len(active_events)} active future events")
        
        print("External models test completed successfully")
        
    except Exception as e:
        print(f"External models test failed: {e}")

def main():
    """Main test function"""
    print("Starting ONG Management System models test...")
    print("=" * 50)
    
    # Set environment variable for database connection
    if not os.getenv('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://ong_user:ong_pass@localhost:5432/ong_management'
    
    try:
        test_user_model()
        test_donation_model()
        test_event_model()
        test_external_models()
        
        print("\n" + "=" * 50)
        print("All model tests completed!")
        
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()