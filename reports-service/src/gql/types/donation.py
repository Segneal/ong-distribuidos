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
    """Convert SQLAlchemy Donation model to GraphQL DonationType"""
    try:
        # Handle user relationships safely
        usuario_creador = None
        if donation.usuario_creador:
            try:
                usuario_creador = user_to_graphql(donation.usuario_creador)
            except Exception as e:
                print(f"Warning: Could not convert usuario_creador: {e}")
        
        usuario_modificador = None
        if donation.usuario_modificador:
            try:
                usuario_modificador = user_to_graphql(donation.usuario_modificador)
            except Exception as e:
                print(f"Warning: Could not convert usuario_modificador: {e}")
        
        return DonationType(
            id=donation.id,
            categoria=DonationCategoryType(donation.categoria.value),
            descripcion=donation.descripcion,
            cantidad=donation.cantidad,
            eliminado=donation.eliminado,
            fechaAlta=donation.fecha_alta,
            fechaModificacion=donation.fecha_modificacion,
            usuarioAlta=usuario_creador,
            usuarioModificacion=usuario_modificador
        )
    except Exception as e:
        print(f"Error converting donation to GraphQL: {e}")
        raise e