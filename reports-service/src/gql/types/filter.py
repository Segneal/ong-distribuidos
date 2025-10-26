"""
GraphQL Filter types
"""
import strawberry
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json


# JSON scalar type for GraphQL
JSON = strawberry.scalar(
    Dict[str, Any],
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


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
    def fechaCreacion(self) -> Optional[datetime]:
        """Frontend-compatible field name for fecha_creacion"""
        return self.fecha_creacion
    
    @strawberry.field
    def configuracion_parsed(self) -> str:
        """Parse configuration JSON for display"""
        try:
            config = json.loads(self.configuracion)
            return json.dumps(config, indent=2)
        except (json.JSONDecodeError, TypeError):
            return self.configuracion
    
    @strawberry.field
    def filtros(self) -> JSON:
        """Parse configuration JSON as object for frontend compatibility"""
        try:
            return json.loads(self.configuracion)
        except (json.JSONDecodeError, TypeError):
            return {}


@strawberry.input
class SavedFilterInput:
    """Input type for saving filters"""
    nombre: str
    tipo: FilterTypeEnum
    configuracion: str  # JSON string


def saved_filter_to_graphql(saved_filter) -> SavedFilterType:
    """Convert SQLAlchemy SavedFilter model to GraphQL SavedFilterType"""
    # Ensure configuracion is a JSON string
    configuracion_str = saved_filter.configuracion
    if isinstance(configuracion_str, dict):
        configuracion_str = json.dumps(configuracion_str)
    
    return SavedFilterType(
        id=saved_filter.id,
        usuario_id=saved_filter.usuario_id,
        nombre=saved_filter.nombre,
        tipo=FilterTypeEnum(saved_filter.tipo.value),
        configuracion=configuracion_str,
        fecha_creacion=saved_filter.fecha_creacion,
        fecha_actualizacion=saved_filter.fecha_actualizacion
    )