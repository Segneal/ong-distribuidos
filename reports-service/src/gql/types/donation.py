"""
GraphQL Donation types
"""
import strawberry
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .user import UserType, user_to_graphql


@strawberry.enum
class DonationCategoryType(Enum):
    """Donation category enumeration for GraphQL"""
    ROPA = "ROPA"
    ALIMENTOS = "ALIMENTOS"
    JUGUETES = "JUGUETES"
    UTILES_ESCOLARES = "UTILES_ESCOLARES"


@strawberry.type
class DonationType:
    """GraphQL Donation type"""
    id: int
    categoria: DonationCategoryType
    descripcion: Optional[str]
    cantidad: int
    eliminado: bool
    fecha_alta: Optional[datetime]
    fecha_modificacion: Optional[datetime]
    usuario_creador: Optional[UserType]
    usuario_modificador: Optional[UserType]
    
    @strawberry.field
    def categoria_display(self) -> str:
        """Human-readable category name"""
        category_names = {
            DonationCategoryType.ROPA: "Ropa",
            DonationCategoryType.ALIMENTOS: "Alimentos",
            DonationCategoryType.JUGUETES: "Juguetes",
            DonationCategoryType.UTILES_ESCOLARES: "Útiles Escolares"
        }
        return category_names.get(self.categoria, self.categoria.value)


@strawberry.type
class DonationReportType:
    """GraphQL Donation Report type for grouped results"""
    categoria: DonationCategoryType
    eliminado: bool
    total_cantidad: int
    registros: List[DonationType]
    
    @strawberry.field
    def categoria_display(self) -> str:
        """Human-readable category name"""
        category_names = {
            DonationCategoryType.ROPA: "Ropa",
            DonationCategoryType.ALIMENTOS: "Alimentos",
            DonationCategoryType.JUGUETES: "Juguetes",
            DonationCategoryType.UTILES_ESCOLARES: "Útiles Escolares"
        }
        return category_names.get(self.categoria, self.categoria.value)


@strawberry.input
class DonationFilterInput:
    """Input type for donation filtering"""
    categoria: Optional[DonationCategoryType] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    eliminado: Optional[bool] = None


def donation_to_graphql(donation) -> DonationType:
    """Convert SQLAlchemy Donation model to GraphQL DonationType"""
    return DonationType(
        id=donation.id,
        categoria=DonationCategoryType(donation.categoria.value),
        descripcion=donation.descripcion,
        cantidad=donation.cantidad,
        eliminado=donation.eliminado,
        fecha_alta=donation.fecha_alta,
        fecha_modificacion=donation.fecha_modificacion,
        usuario_creador=user_to_graphql(donation.usuario_creador) if donation.usuario_creador else None,
        usuario_modificador=user_to_graphql(donation.usuario_modificador) if donation.usuario_modificador else None
    )