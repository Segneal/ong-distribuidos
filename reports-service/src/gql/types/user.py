"""
GraphQL User types
"""
import strawberry
from typing import Optional
from datetime import datetime
from enum import Enum


@strawberry.enum
class UserRoleType(Enum):
    """User role enumeration for GraphQL"""
    PRESIDENTE = "PRESIDENTE"
    VOCAL = "VOCAL"
    COORDINADOR = "COORDINADOR"
    VOLUNTARIO = "VOLUNTARIO"


@strawberry.type
class UserType:
    """GraphQL User type"""
    id: int
    nombre_usuario: str
    nombre: str
    apellido: str
    telefono: Optional[str]
    email: str
    rol: UserRoleType
    activo: bool
    fecha_creacion: Optional[datetime]
    fecha_actualizacion: Optional[datetime]
    
    @strawberry.field
    def nombre_completo(self) -> str:
        """Full name of the user"""
        return f"{self.nombre} {self.apellido}"
    
    @strawberry.field
    def can_access_donation_reports(self) -> bool:
        """Check if user can access donation reports"""
        return self.rol in [UserRoleType.PRESIDENTE, UserRoleType.VOCAL]
    
    @strawberry.field
    def can_access_all_event_reports(self) -> bool:
        """Check if user can access all users' event reports"""
        return self.rol in [UserRoleType.PRESIDENTE, UserRoleType.COORDINADOR]
    
    @strawberry.field
    def can_access_soap_consultation(self) -> bool:
        """Check if user can access SOAP consultation"""
        return self.rol == UserRoleType.PRESIDENTE


def user_to_graphql(user) -> UserType:
    """Convert SQLAlchemy User model to GraphQL UserType"""
    return UserType(
        id=user.id,
        nombre_usuario=user.nombre_usuario,
        nombre=user.nombre,
        apellido=user.apellido,
        telefono=user.telefono,
        email=user.email,
        rol=UserRoleType(user.rol.value),
        activo=user.activo,
        fecha_creacion=user.fecha_creacion,
        fecha_actualizacion=user.fecha_actualizacion
    )