"""
GraphQL types for donation transfers
"""
import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum
from src.models.transfer import DonationTransfer, TransferType, TransferStatus

@strawberry.enum
class TransferTypeEnum(Enum):
    ENVIADA = "ENVIADA"
    RECIBIDA = "RECIBIDA"

@strawberry.enum
class TransferStatusEnum(Enum):
    PENDIENTE = "PENDIENTE"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"

@strawberry.type
class DonationItemType:
    """Individual donation item within a transfer"""
    categoria: str
    descripcion: str
    cantidad: str
    inventory_id: Optional[int] = None

@strawberry.type
class DonationTransferType:
    """Donation transfer between organizations"""
    id: int
    tipo: TransferTypeEnum
    organizacion_contraparte: str
    organizacion_propietaria: str
    solicitud_id: Optional[str]
    donaciones: List[DonationItemType]
    estado: TransferStatusEnum
    fecha_transferencia: datetime
    usuario_registro: Optional[int]
    notas: Optional[str]
    total_items: int
    total_quantity: int
    
    @strawberry.field
    def usuario_nombre(self) -> Optional[str]:
        """Get user name who registered the transfer"""
        # This would be populated from the relationship
        return None

@strawberry.type
class TransferReportType:
    """Transfer report grouped by organization and type"""
    organizacion: str
    tipo: TransferTypeEnum
    total_transferencias: int
    total_items: int
    transferencias: List[DonationTransferType]

def transfer_to_graphql(transfer: DonationTransfer) -> DonationTransferType:
    """Convert SQLAlchemy Transfer model to GraphQL type"""
    
    # Parse donation items - handle both formats
    donation_items = []
    if isinstance(transfer.donaciones, list):
        for item in transfer.donaciones:
            # Handle both old format (categoria, descripcion, cantidad) and new format (category, description, quantity)
            categoria = item.get('categoria') or item.get('category', 'N/A')
            descripcion = item.get('descripcion') or item.get('description', 'N/A')
            cantidad = str(item.get('cantidad') or item.get('quantity', 'N/A'))
            inventory_id = item.get('inventoryId')
            
            donation_items.append(DonationItemType(
                categoria=categoria,
                descripcion=descripcion,
                cantidad=cantidad,
                inventory_id=inventory_id
            ))
    
    return DonationTransferType(
        id=transfer.id,
        tipo=TransferTypeEnum(transfer.tipo.value),
        organizacion_contraparte=transfer.organizacion_contraparte,
        organizacion_propietaria=transfer.organizacion_propietaria,
        solicitud_id=transfer.solicitud_id,
        donaciones=donation_items,
        estado=TransferStatusEnum(transfer.estado.value),
        fecha_transferencia=transfer.fecha_transferencia,
        usuario_registro=transfer.usuario_registro,
        notas=transfer.notas,
        total_items=len(donation_items),
        total_quantity=transfer.get_total_quantity()
    )