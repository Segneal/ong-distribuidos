#!/usr/bin/env python3
"""
Test script for donation offers functionality
"""
import sys
import os
import json
import requests
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_offer_api():
    """Test the offer API endpoints"""
    base_url = "http://localhost:50054"
    
    print("🧪 Testing Donation Offers API")
    print("=" * 50)
    
    # Test health check first
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Messaging service is healthy")
        else:
            print("❌ Messaging service health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to messaging service: {e}")
        return False
    
    # Test creating a donation offer
    print("\n📤 Testing offer creation...")
    offer_data = {
        "donations": [
            {
                "category": "ALIMENTOS",
                "description": "Conservas de atún",
                "quantity": "10 latas"
            },
            {
                "category": "ROPA",
                "description": "Camisetas talla M",
                "quantity": "5 unidades"
            }
        ],
        "userId": 1,
        "notes": "Ofertas disponibles para organizaciones de la red"
    }
    
    try:
        response = requests.post(f"{base_url}/api/createDonationOffer", json=offer_data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Offer created successfully: {result.get('offer_id')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Failed to create offer: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating offer: {e}")
        return False
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Test getting external offers
    print("\n📥 Testing external offers retrieval...")
    try:
        response = requests.post(f"{base_url}/api/getExternalOffers", json={"activeOnly": True})
        
        if response.status_code == 200:
            result = response.json()
            offers = result.get('offers', [])
            print(f"✅ Retrieved {len(offers)} external offers")
            
            for i, offer in enumerate(offers[:3]):  # Show first 3 offers
                print(f"   Offer {i+1}:")
                print(f"     ID: {offer.get('offer_id')}")
                print(f"     Organization: {offer.get('organization_id')}")
                print(f"     Donations: {len(offer.get('donations', []))} items")
        else:
            print(f"❌ Failed to get external offers: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting external offers: {e}")
        return False
    
    print("\n✅ All offer API tests passed!")
    return True


def test_database_offers():
    """Test database operations for offers"""
    print("\n🗄️ Testing Database Offers")
    print("=" * 50)
    
    try:
        # Import network repository
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
        from network_repository import NetworkRepository
        
        repo = NetworkRepository()
        
        # Test getting active external offers
        print("📋 Getting active external offers from database...")
        offers = repo.get_active_external_offers()
        
        print(f"✅ Found {len(offers)} active external offers in database")
        
        for i, offer in enumerate(offers[:3]):  # Show first 3 offers
            print(f"   Offer {i+1}:")
            print(f"     ID: {offer.get('oferta_id')}")
            print(f"     Organization: {offer.get('organizacion_donante')}")
            print(f"     Created: {offer.get('fecha_creacion')}")
            
            # Parse donations
            try:
                donations = json.loads(offer.get('donaciones', '[]'))
                print(f"     Donations: {len(donations)} items")
            except:
                print(f"     Donations: Could not parse")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database offers: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting Donation Offers Tests")
    print("=" * 60)
    
    # Test database operations
    db_success = test_database_offers()
    
    # Test API endpoints
    api_success = test_offer_api()
    
    print("\n" + "=" * 60)
    if db_success and api_success:
        print("🎉 All tests passed successfully!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)