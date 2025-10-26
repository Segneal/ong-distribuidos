"""
GraphQL Event types
"""
import strawberry
from typing import Optional, List
from datetime import datetime
from .user import UserType, user_to_graphql
from .donation import DonationType, donation_to_graphql


@strawberry.type
class EventType:
    """GraphQL Event type"""
    id: int
    nombre: str
    descripcion: Optional[str]
    fecha_evento: datetime
    fecha_creacion: Optional[datetime]
    fecha_actualizacion: Optional[datetime]
    participantes: List[UserType]
    
    @strawberry.field
    def tiene_donaciones_repartidas(self) -> bool:
        """Check if event has distributed donations"""
        # This will be populated by the resolver
        return getattr(self, '_tiene_donaciones_repartidas', False)


@strawberry.type
class EventDetailType:
    """GraphQL Event Detail type for participation reports"""
    dia: int
    nombre: str
    descripcion: Optional[str]
    donaciones: List[DonationType]


@strawberry.type
class EventParticipationReportType:
    """GraphQL Event Participation Report type for monthly grouped results"""
    mes: str
    eventos: List[EventDetailType]


@strawberry.input
class EventFilterInput:
    """Input type for event filtering"""
    fechaDesde: Optional[str] = None
    fechaHasta: Optional[str] = None
    usuarioId: Optional[int] = None
    repartodonaciones: Optional[bool] = None


@strawberry.type
class EventFilterType:
    """Output type for event filtering"""
    fechaDesde: Optional[str] = None
    fechaHasta: Optional[str] = None
    usuarioId: Optional[int] = None
    repartodonaciones: Optional[bool] = None


@strawberry.type
class SavedEventFilterType:
    """GraphQL Saved Event Filter type"""
    id: str
    nombre: str
    filtros: EventFilterType
    fechaCreacion: datetime


@strawberry.input
class SavedEventFilterInput:
    """Input type for saving event filters"""
    nombre: str
    filtros: EventFilterInput


def event_to_graphql(event) -> EventType:
    """Convert SQLAlchemy Event model to GraphQL EventType"""
    return EventType(
        id=event.id,
        nombre=event.nombre,
        descripcion=event.descripcion,
        fecha_evento=event.fecha_evento,
        fecha_creacion=event.fecha_creacion,
        fecha_actualizacion=event.fecha_actualizacion,
        participantes=[user_to_graphql(user) for user in event.participantes] if event.participantes else []
    )