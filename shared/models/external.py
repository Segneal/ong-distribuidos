"""
External network models for ONG Management System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
from .database import execute_query

class ExternalDonationRequest:
    """External donation request model"""
    
    def __init__(self, id: Optional[int] = None, organizacion_solicitante: str = "",
                 solicitud_id: str = "", donaciones: List[Dict[str, str]] = None,
                 activa: bool = True, fecha_creacion: Optional[datetime] = None):
        self.id = id
        self.organizacion_solicitante = organizacion_solicitante
        self.solicitud_id = solicitud_id
        self.donaciones = donaciones or []
        self.activa = activa
        self.fecha_creacion = fecha_creacion
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExternalDonationRequest':
        """Create instance from dictionary"""
        donaciones = data.get('donaciones', [])
        if isinstance(donaciones, str):
            donaciones = json.loads(donaciones)
        
        return cls(
            id=data.get('id'),
            organizacion_solicitante=data.get('organizacion_solicitante', ''),
            solicitud_id=data.get('solicitud_id', ''),
            donaciones=donaciones,
            activa=data.get('activa', True),
            fecha_creacion=data.get('fecha_creacion')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'organizacion_solicitante': self.organizacion_solicitante,
            'solicitud_id': self.solicitud_id,
            'donaciones': self.donaciones,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion
        }
    
    def save(self) -> 'ExternalDonationRequest':
        """Save to database"""
        if self.id is None:
            return self._create()
        else:
            return self._update()
    
    def _create(self) -> 'ExternalDonationRequest':
        """Create new request"""
        query = """
            INSERT INTO solicitudes_externas (organizacion_solicitante, solicitud_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (organizacion_solicitante, solicitud_id) DO UPDATE SET
                donaciones = EXCLUDED.donaciones,
                activa = EXCLUDED.activa
            RETURNING id, fecha_creacion
        """
        params = (
            self.organizacion_solicitante,
            self.solicitud_id,
            json.dumps(self.donaciones),
            self.activa
        )
        
        result = execute_query(query, params)
        if result:
            self.id = result[0]['id']
            self.fecha_creacion = result[0]['fecha_creacion']
        
        return self
    
    def _update(self) -> 'ExternalDonationRequest':
        """Update existing request"""
        query = """
            UPDATE solicitudes_externas 
            SET donaciones = %s, activa = %s
            WHERE id = %s
        """
        params = (json.dumps(self.donaciones), self.activa, self.id)
        execute_query(query, params, fetch=False)
        return self
    
    def deactivate(self) -> bool:
        """Deactivate request"""
        self.activa = False
        self._update()
        return True
    
    @classmethod
    def get_by_id(cls, request_id: int) -> Optional['ExternalDonationRequest']:
        """Get request by ID"""
        query = "SELECT * FROM solicitudes_externas WHERE id = %s"
        result = execute_query(query, (request_id,))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_by_org_and_request_id(cls, org_id: str, request_id: str) -> Optional['ExternalDonationRequest']:
        """Get request by organization and request ID"""
        query = """
            SELECT * FROM solicitudes_externas 
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """
        result = execute_query(query, (org_id, request_id))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_active_requests(cls) -> List['ExternalDonationRequest']:
        """Get all active requests"""
        query = """
            SELECT * FROM solicitudes_externas 
            WHERE activa = TRUE 
            ORDER BY fecha_creacion DESC
        """
        result = execute_query(query)
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    def __str__(self):
        return f"ExternalDonationRequest(org={self.organizacion_solicitante}, id={self.solicitud_id}, active={self.activa})"

class ExternalEvent:
    """External event model"""
    
    def __init__(self, id: Optional[int] = None, organizacion_id: str = "",
                 evento_id: str = "", nombre: str = "", descripcion: Optional[str] = None,
                 fecha_evento: Optional[datetime] = None, activo: bool = True,
                 fecha_creacion: Optional[datetime] = None):
        self.id = id
        self.organizacion_id = organizacion_id
        self.evento_id = evento_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_evento = fecha_evento
        self.activo = activo
        self.fecha_creacion = fecha_creacion
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExternalEvent':
        """Create instance from dictionary"""
        return cls(
            id=data.get('id'),
            organizacion_id=data.get('organizacion_id', ''),
            evento_id=data.get('evento_id', ''),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion'),
            fecha_evento=data.get('fecha_evento'),
            activo=data.get('activo', True),
            fecha_creacion=data.get('fecha_creacion')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'organizacion_id': self.organizacion_id,
            'evento_id': self.evento_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_evento': self.fecha_evento,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion
        }
    
    def save(self) -> 'ExternalEvent':
        """Save to database"""
        if self.id is None:
            return self._create()
        else:
            return self._update()
    
    def _create(self) -> 'ExternalEvent':
        """Create new event"""
        query = """
            INSERT INTO eventos_externos (organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (organizacion_id, evento_id) DO UPDATE SET
                nombre = EXCLUDED.nombre,
                descripcion = EXCLUDED.descripcion,
                fecha_evento = EXCLUDED.fecha_evento,
                activo = EXCLUDED.activo
            RETURNING id, fecha_creacion
        """
        params = (
            self.organizacion_id,
            self.evento_id,
            self.nombre,
            self.descripcion,
            self.fecha_evento,
            self.activo
        )
        
        result = execute_query(query, params)
        if result:
            self.id = result[0]['id']
            self.fecha_creacion = result[0]['fecha_creacion']
        
        return self
    
    def _update(self) -> 'ExternalEvent':
        """Update existing event"""
        query = """
            UPDATE eventos_externos 
            SET nombre = %s, descripcion = %s, fecha_evento = %s, activo = %s
            WHERE id = %s
        """
        params = (self.nombre, self.descripcion, self.fecha_evento, self.activo, self.id)
        execute_query(query, params, fetch=False)
        return self
    
    def deactivate(self) -> bool:
        """Deactivate event"""
        self.activo = False
        self._update()
        return True
    
    def is_future_event(self) -> bool:
        """Check if event is in the future"""
        if self.fecha_evento is None:
            return False
        return self.fecha_evento > datetime.now()
    
    @classmethod
    def get_by_id(cls, event_id: int) -> Optional['ExternalEvent']:
        """Get event by ID"""
        query = "SELECT * FROM eventos_externos WHERE id = %s"
        result = execute_query(query, (event_id,))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_by_org_and_event_id(cls, org_id: str, event_id: str) -> Optional['ExternalEvent']:
        """Get event by organization and event ID"""
        query = """
            SELECT * FROM eventos_externos 
            WHERE organizacion_id = %s AND evento_id = %s
        """
        result = execute_query(query, (org_id, event_id))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_active_future_events(cls, exclude_org: Optional[str] = None) -> List['ExternalEvent']:
        """Get active future events, optionally excluding own organization"""
        query = """
            SELECT * FROM eventos_externos 
            WHERE activo = TRUE AND fecha_evento > CURRENT_TIMESTAMP
        """
        params = []
        
        if exclude_org:
            query += " AND organizacion_id != %s"
            params.append(exclude_org)
        
        query += " ORDER BY fecha_evento ASC"
        
        result = execute_query(query, tuple(params) if params else None)
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    def __str__(self):
        return f"ExternalEvent(org={self.organizacion_id}, id={self.evento_id}, name={self.nombre}, active={self.activo})"