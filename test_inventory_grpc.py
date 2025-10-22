#!/usr/bin/env python3
"""
Script de prueba para el servicio gRPC de inventario
"""
import grpc
import sys
import os

# Agregar el path del servicio de inventario
sys.path.append(os.path.join(os.path.dirname(__file__), 'inventory-service', 'src'))

try:
    import inventory_pb2
    import inventory_pb2_grpc
    print("✅ Protobuf imports successful")
except ImportError as e:
    print(f"❌ Error importing protobuf: {e}")
    sys.exit(1)

def test_inventory_service():
    """Probar el servicio de inventario"""
    try:
        # Crear canal gRPC
        channel = grpc.insecure_channel('localhost:50052')
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)
        
        print("🔗 Conectado al servicio de inventario")
        
        # Probar ListDonations
        print("\n📋 Probando ListDonations...")
        request = inventory_pb2.ListDonationsRequest()
        response = stub.ListDonations(request)
        
        print(f"✅ ListDonations exitoso:")
        print(f"   Success: {response.success}")
        print(f"   Message: {response.message}")
        print(f"   Donations count: {len(response.donations)}")
        
        for i, donation in enumerate(response.donations[:3]):  # Solo mostrar primeras 3
            print(f"   Donation {i+1}: ID={donation.id}, Category={donation.category}, Quantity={donation.quantity}")
        
        # Probar CreateDonation
        print("\n➕ Probando CreateDonation...")
        create_request = inventory_pb2.CreateDonationRequest(
            category=inventory_pb2.ALIMENTOS,
            description="Prueba desde script Python",
            quantity=10,
            created_by=1,
            organization="empuje-comunitario"
        )
        
        create_response = stub.CreateDonation(create_request)
        print(f"✅ CreateDonation exitoso:")
        print(f"   Success: {create_response.success}")
        print(f"   Message: {create_response.message}")
        if create_response.donation:
            print(f"   Created ID: {create_response.donation.id}")
        
        channel.close()
        print("\n🎉 Todas las pruebas completadas exitosamente")
        
    except grpc.RpcError as e:
        print(f"❌ Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_inventory_service()