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
    ALIMENTOS = "ALIMENTOS"
    ROPA = "ROPA"
    MEDICAMENTOS = "MEDICAMENTOS"
    JUGUETES = "JUGUETES"
    LIBROS = "LIBROS"
    ELECTRODOMESTICOS = "ELECTRODOMESTICOS"
    MUEBLES = "MUEBLES"
    OTROS = "OTROS"
    UTILES_ESCOLARES = "UTILES_ESCOLARES"


@strawberry.type
class DonationType:
    """GraphQL Donation type"""
    id: int
    categoria: DonationCategoryType
    descripcion: Optional[str]
    cantidad: int
    eliminado: bool
    fechaAlta: Optional[datetime]
    fechaModificacion: Optional[datetime]
    usuarioAlta: Optional[UserType]
    usuarioModificacion: Optional[UserType]
    
    @strawberry.field
    def categoria_display(self) -> str:
        """Human-readable category name"""
        category_names = {
            DonationCategoryType.ALIMENTOS: "Alimentos",
            DonationCategoryType.ROPA: "Ropa",
            DonationCategoryType.MEDICAMENTOS: "Medicamentos",
            DonationCategoryType.JUGUETES: "Juguetes",
            DonationCategoryType.LIBROS: "Libros",
            DonationCategoryType.ELECTRODOMESTICOS: "Electrodomésticos",
            DonationCategoryType.MUEBLES: "Muebles",
            DonationCategoryType.OTROS: "Otros",
            DonationCategoryType.UTILES_ESCOLARES: "Útiles Escolares"
        }
        return category_names.get(self.categoria, self.categoria.value)


@strawberry.type
class DonationReportType:
    """GraphQL Donation Report type for grouped results"""
    categoria: DonationCategoryType
    eliminado: bool
    totalCantidad: int
    registros: List[DonationType]
    
    @strawberry.field
    def categoria_display(self) -> str:
        """Human-readable category name"""
        category_names = {
            DonationCategoryType.ALIMENTOS: "Alimentos",
            DonationCategoryType.ROPA: "Ropa",
            DonationCategoryType.MEDICAMENTOS: "Medicamentos",
            DonationCategoryType.JUGUETES: "Juguetes",
            DonationCategoryType.LIBROS: "Libros",
            DonationCategoryType.ELECTRODOMESTICOS: "Electrodomésticos",
            DonationCategoryType.MUEBLES: "Muebles",
            DonationCategoryType.OTROS: "Otros",
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
    """Convert donation data (dict or SQLAlchemy model) to GraphQL DonationType"""
    # Handle both dictionary and SQLAlchemy object formats
    if isinstance(donation, dict):
        # Dictionary format from event service
        return DonationType(
            id=donation['id'],
            categoria=DonationCategoryType(donation['categoria']),
            descripcion=donation['descripcion'] or "",
            cantidad=donation['cantidad'],
            eliminado=donation['eliminado'],
            fechaAlta=donation['fecha_alta'],
            fechaModificacion=donation['fecha_modificacion'],
            usuarioAlta=None,
            usuarioModificacion=None
        )
    else:
        # SQLAlchemy object format (for other uses)
        categoria_value = donation.categoria
        if hasattr(categoria_value, 'value'):
            categoria_value = categoria_value.value
        
        return DonationType(
            id=donation.id,
            categoria=DonationCategoryType(categoria_value),
            descripcion=donation.descripcion or "",
            cantidad=donation.cantidad,
            eliminado=donation.eliminado,
            fechaAlta=donation.fecha_alta,
            fechaModificacion=donation.fecha_modificacion,
            usuarioAlta=None,
            usuarioModificacion=None
        )