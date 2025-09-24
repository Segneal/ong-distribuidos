"""
Inventory Service gRPC Server
Implements the InventoryService defined in inventory.proto
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

import grpc
from concurrent import futures
from datetime import datetime
from typing import Optional

# Import generated protobuf classes
import inventory_pb2
import inventory_pb2_grpc

# Import repository and models
from inventory_repository import InventoryRepository
from models.donation import DonationCategory

class InventoryServiceImpl(inventory_pb2_grpc.InventoryServiceServicer):
    """Implementation of the InventoryService gRPC service"""
    
    def __init__(self):
        self.repository = InventoryRepository()
    
    def _category_proto_to_enum(self, proto_category):
        """Convert protobuf Category to DonationCategory enum"""
        category_map = {
            inventory_pb2.ROPA: DonationCategory.ROPA,
            inventory_pb2.ALIMENTOS: DonationCategory.ALIMENTOS,
            inventory_pb2.JUGUETES: DonationCategory.JUGUETES,
            inventory_pb2.UTILES_ESCOLARES: DonationCategory.UTILES_ESCOLARES
        }
        return category_map.get(proto_category, DonationCategory.ALIMENTOS)
    
    def _category_enum_to_proto(self, category_enum):
        """Convert DonationCategory enum to protobuf Category"""
        print(f"CATEGORY_ENUM_TO_PROTO: Input = {category_enum} (type: {type(category_enum)})")
        
        # Si viene como string, convertir a enum primero
        if isinstance(category_enum, str):
            try:
                category_enum = DonationCategory(category_enum)
                print(f"CATEGORY_ENUM_TO_PROTO: Converted string to enum = {category_enum}")
            except ValueError:
                print(f"CATEGORY_ENUM_TO_PROTO: Invalid string category, using default")
                category_enum = DonationCategory.ALIMENTOS
        
        category_map = {
            DonationCategory.ROPA: inventory_pb2.ROPA,
            DonationCategory.ALIMENTOS: inventory_pb2.ALIMENTOS,
            DonationCategory.JUGUETES: inventory_pb2.JUGUETES,
            DonationCategory.UTILES_ESCOLARES: inventory_pb2.UTILES_ESCOLARES
        }
        
        result = category_map.get(category_enum, inventory_pb2.ALIMENTOS)
        print(f"CATEGORY_ENUM_TO_PROTO: Final result = {result} (type: {type(result)})")
        return result
    
    def _donation_to_proto(self, donation):
        """Convert Donation model to protobuf Donation message"""
        print(f"CONVERTING TO PROTO: donation.categoria = {donation.categoria} (type: {type(donation.categoria)})")
        category_proto = self._category_enum_to_proto(donation.categoria)
        print(f"CONVERTING TO PROTO: category_proto = {category_proto} (type: {type(category_proto)})")
        
        return inventory_pb2.Donation(
            id=donation.id,
            category=category_proto,
            description=donation.descripcion or "",
            quantity=donation.cantidad,
            deleted=donation.eliminado,
            created_at=donation.fecha_alta.isoformat() if donation.fecha_alta else "",
            updated_at=donation.fecha_modificacion.isoformat() if donation.fecha_modificacion else "",
            created_by=donation.usuario_alta or 0,
            updated_by=donation.usuario_modificacion or 0
        )
    
    def CreateDonation(self, request, context):
        """Create a new donation"""
        print("=== INVENTORY SERVICE: CreateDonation STARTED ===")
        try:
            print(f"INVENTORY SERVICE: 1. CreateDonation request received")
            print(f"INVENTORY SERVICE: 2. Request object: {request}")
            print(f"INVENTORY SERVICE: 3. Request category: {request.category} (type: {type(request.category)})")
            print(f"INVENTORY SERVICE: 4. Request description: '{request.description}' (type: {type(request.description)})")
            print(f"INVENTORY SERVICE: 5. Request quantity: {request.quantity} (type: {type(request.quantity)})")
            print(f"INVENTORY SERVICE: 6. Request created_by: {request.created_by} (type: {type(request.created_by)})")
            
            # Validate quantity is not negative
            print(f"INVENTORY SERVICE: 7. Validating quantity...")
            if request.quantity < 0:
                print(f"INVENTORY SERVICE: 8. Quantity validation failed")
                return inventory_pb2.DonationResponse(
                    success=False,
                    message="La cantidad no puede ser negativa"
                )
            
            # Convert protobuf category to enum
            print(f"INVENTORY SERVICE: 9. Converting category to enum...")
            category = self._category_proto_to_enum(request.category)
            print(f"INVENTORY SERVICE: 10. Converted category: {category} (type: {type(category)})")
            
            # Create donation
            print(f"INVENTORY SERVICE: 11. Calling repository.create_donation...")
            donation = self.repository.create_donation(
                category=category,
                description=request.description,
                quantity=request.quantity,
                created_by=request.created_by
            )
            print(f"INVENTORY SERVICE: 12. Repository returned: {donation}")
            
            if donation:
                print(f"INVENTORY SERVICE: 13. Success! Converting donation to proto...")
                proto_donation = self._donation_to_proto(donation)
                print(f"INVENTORY SERVICE: 14. Proto donation: {proto_donation}")
                response = inventory_pb2.DonationResponse(
                    success=True,
                    message="Donación creada exitosamente",
                    donation=proto_donation
                )
                print(f"INVENTORY SERVICE: 15. Returning success response")
                return response
            else:
                print(f"INVENTORY SERVICE: 16. Repository returned None - creation failed")
                return inventory_pb2.DonationResponse(
                    success=False,
                    message="Error al crear la donación"
                )
                
        except Exception as e:
            print(f"INVENTORY SERVICE: 17. EXCEPTION in CreateDonation: {e}")
            print(f"INVENTORY SERVICE: 18. Exception type: {type(e)}")
            import traceback
            print(f"INVENTORY SERVICE: 19. Exception traceback: {traceback.format_exc()}")
            return inventory_pb2.DonationResponse(
                success=False,
                message=f"Error interno del servidor: {str(e)}"
            )
        finally:
            print("=== INVENTORY SERVICE: CreateDonation ENDED ===")
    
    def GetDonation(self, request, context):
        """Get donation by ID"""
        try:
            donation = self.repository.get_donation_by_id(request.id)
            
            if donation:
                return inventory_pb2.DonationResponse(
                    success=True,
                    message="Donación encontrada",
                    donation=self._donation_to_proto(donation)
                )
            else:
                return inventory_pb2.DonationResponse(
                    success=False,
                    message="Donación no encontrada"
                )
                
        except Exception as e:
            print(f"Error in GetDonation: {e}")
            return inventory_pb2.DonationResponse(
                success=False,
                message=f"Error interno del servidor: {str(e)}"
            )
    
    def UpdateDonation(self, request, context):
        """Update existing donation"""
        print("=== INVENTORY SERVICE: UpdateDonation STARTED ===")
        try:
            print(f"INVENTORY SERVICE: 1. UpdateDonation request received")
            print(f"INVENTORY SERVICE: 2. Request object: {request}")
            print(f"INVENTORY SERVICE: 3. Request id: {request.id}")
            print(f"INVENTORY SERVICE: 4. Request description: '{request.description}'")
            print(f"INVENTORY SERVICE: 5. Request quantity: {request.quantity}")
            print(f"INVENTORY SERVICE: 6. Request updated_by: {request.updated_by}")
            print(f"INVENTORY SERVICE: 7. Request has category field: {request.HasField('category')}")
            if request.HasField('category'):
                print(f"INVENTORY SERVICE: 8. Request category: {request.category}")
            
            # Validate quantity is not negative
            if request.quantity < 0:
                print(f"INVENTORY SERVICE: 9. Quantity validation failed")
                return inventory_pb2.DonationResponse(
                    success=False,
                    message="La cantidad no puede ser negativa"
                )
            
            # Convert category if provided
            category = None
            if request.HasField('category'):
                print(f"INVENTORY SERVICE: 10. Converting category...")
                category = self._category_proto_to_enum(request.category)
                print(f"INVENTORY SERVICE: 11. Converted category: {category}")
            else:
                print(f"INVENTORY SERVICE: 12. No category field in request")
            
            # Update donation
            print(f"INVENTORY SERVICE: 13. Calling repository.update_donation...")
            donation = self.repository.update_donation(
                donation_id=request.id,
                description=request.description,
                quantity=request.quantity,
                updated_by=request.updated_by,
                category=category
            )
            print(f"INVENTORY SERVICE: 14. Repository returned: {donation}")
            
            if donation:
                return inventory_pb2.DonationResponse(
                    success=True,
                    message="Donación actualizada exitosamente",
                    donation=self._donation_to_proto(donation)
                )
            else:
                return inventory_pb2.DonationResponse(
                    success=False,
                    message="Error al actualizar la donación o donación no encontrada"
                )
                
        except Exception as e:
            print(f"Error in UpdateDonation: {e}")
            return inventory_pb2.DonationResponse(
                success=False,
                message=f"Error interno del servidor: {str(e)}"
            )
    
    def DeleteDonation(self, request, context):
        """Delete donation (logical delete)"""
        try:
            success = self.repository.delete_donation(
                donation_id=request.id,
                deleted_by=request.deleted_by
            )
            
            if success:
                return inventory_pb2.DeleteDonationResponse(
                    success=True,
                    message="Donación eliminada exitosamente"
                )
            else:
                return inventory_pb2.DeleteDonationResponse(
                    success=False,
                    message="Error al eliminar la donación o donación no encontrada"
                )
                
        except Exception as e:
            print(f"Error in DeleteDonation: {e}")
            return inventory_pb2.DeleteDonationResponse(
                success=False,
                message=f"Error interno del servidor: {str(e)}"
            )
    
    def ListDonations(self, request, context):
        """List donations with optional filters"""
        try:
            # Convert category filter if provided
            category = None
            if request.HasField('category'):
                category = self._category_proto_to_enum(request.category)
            
            # Get include_deleted flag
            include_deleted = request.include_deleted if request.HasField('include_deleted') else False
            
            # Get donations
            donations = self.repository.list_donations(
                category=category,
                include_deleted=include_deleted
            )
            
            # Convert to protobuf messages
            proto_donations = [self._donation_to_proto(donation) for donation in donations]
            
            return inventory_pb2.ListDonationsResponse(
                success=True,
                message=f"Se encontraron {len(donations)} donaciones",
                donations=proto_donations
            )
            
        except Exception as e:
            print(f"Error in ListDonations: {e}")
            return inventory_pb2.ListDonationsResponse(
                success=False,
                message=f"Error interno del servidor: {str(e)}",
                donations=[]
            )
    
    def TransferDonations(self, request, context):
        """Transfer donations to another organization"""
        try:
            # Convert protobuf transfers to dict format
            transfers = []
            for transfer in request.donations:
                transfers.append({
                    'donation_id': transfer.donation_id,
                    'quantity': transfer.quantity
                })
            
            # Execute transfers
            transfer_ids = self.repository.transfer_donations(
                transfers=transfers,
                target_organization=request.target_organization,
                transferred_by=request.transferred_by
            )
            
            if transfer_ids:
                return inventory_pb2.TransferDonationsResponse(
                    success=True,
                    message=f"Se transfirieron {len(transfer_ids)} donaciones exitosamente",
                    transfer_ids=transfer_ids
                )
            else:
                return inventory_pb2.TransferDonationsResponse(
                    success=False,
                    message="No se pudieron transferir las donaciones",
                    transfer_ids=[]
                )
                
        except Exception as e:
            print(f"Error in TransferDonations: {e}")
            return inventory_pb2.TransferDonationsResponse(
                success=False,
                message=f"Error interno del servidor: {str(e)}",
                transfer_ids=[]
            )

def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryServiceImpl(), server)
    
    # Configure server to listen on port 50052
    listen_addr = '0.0.0.0:50052'
    server.add_insecure_port(listen_addr)
    
    print(f"Starting Inventory Service gRPC server on {listen_addr}")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down Inventory Service...")
        server.stop(0)

if __name__ == '__main__':
    serve()