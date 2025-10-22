"""
GraphQL Filter types
"""
import strawberry
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json


@strawberry.enum
class FilterTypeEnum(Enum):
    """Filter type enumeration for GraphQL"""
    DONACIONES = "DONACIONES"
    EVENTOS = "EVENTOS"


@strawberry.type
class SavedFilterType:
    """GraphQL Saved Filter type"""
    id: int
    usuario_id: int
    nombre: str
    tipo: FilterTypeEnum
    configuracion: str  # JSON string representation
    fecha_creacion: Optional[datetime]
    fecha_actualizacion: Optional[datetime]
    
    @strawberry.field
    def configuracion_parsed(self) -> str:
        """Parse configuration JSON for display"""
        try:
            config = json.loads(self.configuracion)
            return json.dumps(config, indent=2)
        except (json.JSONDecodeError, TypeError):
            return self.configuracion


@strawberry.input
class SavedFilterInput:
    """Input type for saving filters"""
    nombre: str
    tipo: FilterTypeEnum
    configuracion: str  # JSON string


def saved_filter_to_graphql(saved_filter) -> SavedFilterType:
    """Convert SQLAlchemy SavedFilter model to GraphQL SavedFilterType"""
    return SavedFilterType(
        id=saved_filter.id,
        usuario_id=saved_filter.usuario_id,
        nombre=saved_filter.nombre,
        tipo=FilterTypeEnum(saved_filter.tipo.value),
        configuracion=saved_filter.configuracion,
        fecha_creacion=saved_filter.fecha_creacion,
        fecha_actualizacion=saved_filter.fecha_actualizacion
    )