#!/usr/bin/env python3
"""
Debug directo del TransferService
"""
import sys
import os

# Agregar el path del messaging service
sys.path.append('messaging-service/src')

from messaging.services.transfer_service import TransferService

def test_transfer_service():
    """Test directo del TransferService"""
    print("=== TESTING TRANSFER SERVICE DIRECTLY ===")
    
    try:
        service = TransferService()
        
        # Test con esperanza-social
        transfers = service.get_transfer_history("esperanza-social", 10)
        
        print(f"Transfers returned: {len(transfers)}")
        
        for transfer in transfers:
            print(f"  - ID: {transfer.get('id')}")
            print(f"    Tipo: {transfer.get('tipo')}")
            print(f"    Contraparte: {transfer.get('organizacion_contraparte')}")
        
        return len(transfers) > 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_transfer_service()