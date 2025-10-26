#!/usr/bin/env python3
"""
Script to wake up the SOAP service if it's sleeping.
This is common with free tier services on platforms like Render.com.
"""
import requests
import time
import sys

def wake_up_soap_service():
    """Attempt to wake up the SOAP service by making multiple requests."""
    print("🌅 Attempting to wake up SOAP service...")
    
    base_url = "https://soap-app-latest.onrender.com"
    
    # Try multiple approaches to wake up the service
    attempts = [
        ("GET WSDL", f"{base_url}/?wsdl", "GET"),
        ("GET Root", f"{base_url}/", "GET"),
        ("GET Health", f"{base_url}/health", "GET"),
    ]
    
    for attempt_name, url, method in attempts:
        print(f"\n📡 {attempt_name}: {url}")
        
        for i in range(3):  # Try 3 times for each endpoint
            try:
                print(f"   Attempt {i+1}/3...", end=" ")
                
                if method == "GET":
                    response = requests.get(url, timeout=45)  # Longer timeout for sleeping services
                else:
                    response = requests.post(url, timeout=45)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ {attempt_name} successful!")
                    
                    # If WSDL request was successful, the service is likely awake
                    if "wsdl" in url.lower():
                        print(f"   📄 WSDL content length: {len(response.text)} characters")
                        if len(response.text) > 1000:  # Valid WSDL should be substantial
                            print("   🎉 SOAP service appears to be awake!")
                            return True
                    
                    # Wait a bit before next attempt
                    time.sleep(2)
                    break
                    
                elif response.status_code in [502, 503, 504]:
                    print(f"   ⏳ Service starting up (HTTP {response.status_code})")
                    time.sleep(5)  # Wait longer for startup
                    
                else:
                    print(f"   ⚠️  Unexpected status: {response.status_code}")
                    time.sleep(2)
                    
            except requests.exceptions.Timeout:
                print("Timeout")
                if i < 2:  # Not the last attempt
                    print("   ⏳ Service may be starting up, waiting...")
                    time.sleep(10)  # Wait longer between timeout attempts
                    
            except requests.exceptions.ConnectionError as e:
                print(f"Connection Error: {e}")
                time.sleep(3)
                
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(2)
    
    print("\n⚠️  Service may still be starting up or experiencing issues")
    return False

def test_soap_functionality():
    """Test basic SOAP functionality after wake-up attempt."""
    print("\n🧪 Testing SOAP functionality...")
    
    try:
        # Import our SOAP client
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.soap.client import SOAPClient
        
        client = SOAPClient()
        
        # Test connection
        print("   Testing connection...")
        is_connected = client.test_connection()
        
        if is_connected:
            print("   ✅ SOAP connection successful!")
            
            # Test a simple query
            print("   Testing simple query...")
            try:
                result = client.get_combined_data([5, 6])
                print(f"   📊 Query result: {result.get('total_presidents', 0)} presidents, {result.get('total_organizations', 0)} organizations")
                print("   🎉 SOAP service is fully functional!")
                return True
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
                return False
        else:
            print("   ❌ SOAP connection failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing SOAP functionality: {e}")
        return False

def main():
    """Main function to wake up and test SOAP service."""
    print("🚀 SOAP Service Wake-Up Script")
    print("=" * 50)
    
    # Attempt to wake up the service
    wake_success = wake_up_soap_service()
    
    # Wait a bit for the service to fully start
    if wake_success:
        print("\n⏳ Waiting for service to fully initialize...")
        time.sleep(5)
    
    # Test functionality
    test_success = test_soap_functionality()
    
    # Summary
    print("\n" + "=" * 50)
    if test_success:
        print("🎉 SOAP service is awake and functional!")
        print("✅ You can now use the network consultation feature")
        return True
    else:
        print("⚠️  SOAP service may need more time to start up")
        print("💡 Try running this script again in a few minutes")
        print("💡 Or check the service status at: https://soap-app-latest.onrender.com")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)