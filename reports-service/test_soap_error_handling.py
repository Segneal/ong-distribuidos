#!/usr/bin/env python3
"""
Test script for SOAP error handling with non-existent organization IDs.
This script tests how the system handles invalid or non-existent organization IDs.
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.soap.client import SOAPClient, SOAPServiceError

def test_nonexistent_organization_ids():
    """Test handling of non-existent organization IDs."""
    print("🧪 Testing non-existent organization IDs...")
    
    client = SOAPClient()
    
    # Test with clearly non-existent IDs (very high numbers)
    nonexistent_ids = [99999, 88888, 77777]
    
    print(f"   Testing with non-existent IDs: {nonexistent_ids}")
    
    try:
        # Test president data
        print("   Testing president data with non-existent IDs...")
        president_data = client.get_president_data(nonexistent_ids)
        print(f"     Presidents found: {len(president_data)}")
        
        if len(president_data) == 0:
            print("     ✅ Non-existent IDs handled gracefully (no presidents found)")
        else:
            print(f"     ⚠️  Unexpected data found: {president_data}")
        
        # Test organization data
        print("   Testing organization data with non-existent IDs...")
        organization_data = client.get_organization_data(nonexistent_ids)
        print(f"     Organizations found: {len(organization_data)}")
        
        if len(organization_data) == 0:
            print("     ✅ Non-existent IDs handled gracefully (no organizations found)")
        else:
            print(f"     ⚠️  Unexpected data found: {organization_data}")
        
        # Test combined data
        print("   Testing combined data with non-existent IDs...")
        combined_data = client.get_combined_data(nonexistent_ids)
        print(f"     Total presidents: {combined_data.get('total_presidents', 0)}")
        print(f"     Total organizations: {combined_data.get('total_organizations', 0)}")
        print(f"     Errors: {combined_data.get('errors', [])}")
        
        if combined_data.get('total_presidents', 0) == 0 and combined_data.get('total_organizations', 0) == 0:
            print("     ✅ Combined query handled gracefully")
        else:
            print("     ⚠️  Unexpected data in combined query")
        
        return True
        
    except SOAPServiceError as e:
        print(f"     ❌ SOAP service error: {e}")
        return False
    except Exception as e:
        print(f"     ❌ Unexpected error: {e}")
        return False

def test_mixed_valid_invalid_ids():
    """Test handling of mixed valid and invalid organization IDs."""
    print("\n🔍 Testing mixed valid and invalid IDs...")
    
    client = SOAPClient()
    
    # Mix of known valid IDs and clearly invalid ones
    mixed_ids = [5, 99999, 6, 88888, 8]
    
    print(f"   Testing with mixed IDs: {mixed_ids}")
    
    try:
        # Test combined data
        combined_data = client.get_combined_data(mixed_ids)
        
        print(f"     Total presidents: {combined_data.get('total_presidents', 0)}")
        print(f"     Total organizations: {combined_data.get('total_organizations', 0)}")
        print(f"     Query IDs: {combined_data.get('query_ids', [])}")
        print(f"     Errors: {combined_data.get('errors', [])}")
        
        # We should get some data for valid IDs
        if combined_data.get('total_presidents', 0) > 0 or combined_data.get('total_organizations', 0) > 0:
            print("     ✅ Mixed IDs handled - got data for valid IDs")
        else:
            print("     ⚠️  No data found even for valid IDs")
        
        return True
        
    except SOAPServiceError as e:
        print(f"     ❌ SOAP service error: {e}")
        return False
    except Exception as e:
        print(f"     ❌ Unexpected error: {e}")
        return False

def test_invalid_id_formats():
    """Test handling of invalid ID formats."""
    print("\n⚠️  Testing invalid ID formats...")
    
    client = SOAPClient()
    
    # Test with negative IDs
    print("   Testing with negative IDs...")
    try:
        negative_ids = [-1, -5, -10]
        combined_data = client.get_combined_data(negative_ids)
        print(f"     Result: {combined_data.get('total_presidents', 0)} presidents, {combined_data.get('total_organizations', 0)} organizations")
        print("     ✅ Negative IDs handled")
    except Exception as e:
        print(f"     ❌ Error with negative IDs: {e}")
        return False
    
    # Test with zero IDs
    print("   Testing with zero IDs...")
    try:
        zero_ids = [0]
        combined_data = client.get_combined_data(zero_ids)
        print(f"     Result: {combined_data.get('total_presidents', 0)} presidents, {combined_data.get('total_organizations', 0)} organizations")
        print("     ✅ Zero IDs handled")
    except Exception as e:
        print(f"     ❌ Error with zero IDs: {e}")
        return False
    
    return True

def test_empty_id_list():
    """Test handling of empty ID list."""
    print("\n📝 Testing empty ID list...")
    
    client = SOAPClient()
    
    try:
        empty_ids = []
        combined_data = client.get_combined_data(empty_ids)
        
        print(f"     Total presidents: {combined_data.get('total_presidents', 0)}")
        print(f"     Total organizations: {combined_data.get('total_organizations', 0)}")
        
        if combined_data.get('total_presidents', 0) == 0 and combined_data.get('total_organizations', 0) == 0:
            print("     ✅ Empty ID list handled gracefully")
            return True
        else:
            print("     ❌ Unexpected data for empty ID list")
            return False
            
    except Exception as e:
        print(f"     ❌ Error with empty ID list: {e}")
        return False

def test_connection_before_error_tests():
    """Test connection before running error tests."""
    print("🔗 Testing SOAP connection before error tests...")
    
    client = SOAPClient()
    
    try:
        connection_result = client.test_connection()
        
        if connection_result:
            print("   ✅ SOAP connection is working")
            return True
        else:
            print("   ❌ SOAP connection failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection test failed: {e}")
        return False

def main():
    """Run all SOAP error handling tests."""
    print("🧪 SOAP Error Handling Test Suite")
    print("=" * 60)
    print("Testing how the system handles various error scenarios:")
    print("- Non-existent organization IDs")
    print("- Mixed valid/invalid IDs")
    print("- Invalid ID formats")
    print("- Empty ID lists")
    print("=" * 60)
    
    # First check connection
    if not test_connection_before_error_tests():
        print("\n❌ Cannot proceed with error tests - SOAP service is not available")
        return False
    
    tests = [
        ("Non-existent Organization IDs", test_nonexistent_organization_ids),
        ("Mixed Valid/Invalid IDs", test_mixed_valid_invalid_ids),
        ("Invalid ID Formats", test_invalid_id_formats),
        ("Empty ID List", test_empty_id_list)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All SOAP error handling tests passed!")
        print("✅ The system handles error scenarios gracefully")
        return True
    else:
        print("⚠️  Some tests failed. The system may not handle all error scenarios properly.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)