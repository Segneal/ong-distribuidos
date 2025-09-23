"""
Event model for ONG Management System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from .database import execute_query, execute_transaction

class Event:
    """Event model class"""
    
    def __init__(self, id: Optional[int] = None, nombre: str = "", descripcion: Optional[str] = None,
                 fecha_evento: Optional[datetime] = None, fecha_creacion: Optional[datetime] = None,
                 fecha_actualizacion: Optional[datetime] = None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_evento = fecha_evento
        self.fecha_creacion = fecha_creacion
        self.fecha_actualizacion = fecha_actualizacion
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create Event instance from dictionary"""
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion'),
            fecha_evento=data.get('fecha_evento'),
            fecha_creacion=data.get('fecha_creacion'),
            fecha_actualizacion=data.get('fecha_actualizacion')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Event instance to dictionary"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_evento': self.fecha_evento,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }
    
    def save(self) -> 'Event':
        """Save event to database"""
        if self.id is None:
            return self._create()
        else:
            return self._update()
    
    def _create(self) -> 'Event':
        """Create new event in database"""
        query = """
            INSERT INTO eventos (nombre, descripcion, fecha_evento)
            VALUES (%s, %s, %s)
            RETURNING id, fecha_creacion, fecha_actualizacion
        """
        params = (self.nombre, self.descripcion, self.fecha_evento)
        
        result = execute_query(query, params)
        if result:
            self.id = result[0]['id']
            self.fecha_creacion = result[0]['fecha_creacion']
            self.fecha_actualizacion = result[0]['fecha_actualizacion']
        
        return self
    
    def _update(self) -> 'Event':
        """Update existing event in database"""
        query = """
            UPDATE eventos 
            SET nombre = %s, descripcion = %s, fecha_evento = %s
            WHERE id = %s
            RETURNING fecha_actualizacion
        """
        params = (self.nombre, self.descripcion, self.fecha_evento, self.id)
        
        result = execute_query(query, params)
        if result:
            self.fecha_actualizacion = result[0]['fecha_actualizacion']
        
        return self
    
    def delete(self) -> bool:
        """Delete event (only if future event)"""
        if self.id is None:
            return False
        
        # Check if event is in the future
        if self.fecha_evento and self.fecha_evento <= datetime.now():
            return False  # Cannot delete past events
        
        # Delete participants first (cascade should handle this, but being explicit)
        execute_query("DELETE FROM participantes_evento WHERE evento_id = %s", (self.id,), fetch=False)
        
        # Delete event
        execute_query("DELETE FROM eventos WHERE id = %s", (self.id,), fetch=False)
        
        return True
    
    def is_future_event(self) -> bool:
        """Check if event is in the future"""
        if self.fecha_evento is None:
            return False
        return self.fecha_evento > datetime.now()
    
    def is_past_event(self) -> bool:
        """Check if event is in the past"""
        if self.fecha_evento is None:
            return False
        return self.fecha_evento <= datetime.now()
    
    def add_participant(self, user_id: int) -> bool:
        """Add participant to event"""
        if self.id is None:
            return False
        
        try:
            query = """
                INSERT INTO participantes_evento (evento_id, usuario_id)
                VALUES (%s, %s)
                ON CONFLICT (evento_id, usuario_id) DO NOTHING
            """
            execute_query(query, (self.id, user_id), fetch=False)
            return True
        except Exception as e:
            print(f"Error adding participant: {e}")
            return False
    
    def remove_participant(self, user_id: int) -> bool:
        """Remove participant from event"""
        if self.id is None:
            return False
        
        try:
            query = "DELETE FROM participantes_evento WHERE evento_id = %s AND usuario_id = %s"
            result = execute_query(query, (self.id, user_id), fetch=False)
            return result > 0
        except Exception as e:
            print(f"Error removing participant: {e}")
            return False
    
    def get_participants(self) -> List[Dict[str, Any]]:
        """Get event participants"""
        if self.id is None:
            return []
        
        query = """
            SELECT u.id, u.nombre_usuario, u.nombre, u.apellido, u.email, u.telefono, u.rol,
                   pe.fecha_adhesion
            FROM usuarios u
            JOIN participantes_evento pe ON u.id = pe.usuario_id
            WHERE pe.evento_id = %s AND u.activo = TRUE
            ORDER BY u.nombre, u.apellido
        """
        
        result = execute_query(query, (self.id,))
        return [dict(row) for row in result] if result else []
    
    def register_distributed_donations(self, donations: List[Dict[str, Any]], user_id: int) -> bool:
        """Register donations distributed in this event"""
        if self.id is None or not self.is_past_event():
            return False
        
        queries = []
        
        for donation_data in donations:
            donation_id = donation_data.get('donation_id')
            cantidad_repartida = donation_data.get('cantidad_repartida', 0)
            
            if cantidad_repartida <= 0:
                continue
            
            # Register distributed donation
            queries.append((
                """
                INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro)
                VALUES (%s, %s, %s, %s)
                """,
                (self.id, donation_id, cantidad_repartida, user_id)
            ))
            
            # Reduce inventory
            queries.append((
                """
                UPDATE donaciones 
                SET cantidad = cantidad - %s,
                    fecha_modificacion = CURRENT_TIMESTAMP,
                    usuario_modificacion = %s
                WHERE id = %s AND cantidad >= %s AND eliminado = FALSE
                """,
                (cantidad_repartida, user_id, donation_id, cantidad_repartida)
            ))
        
        try:
            execute_transaction(queries)
            return True
        except Exception as e:
            print(f"Error registering distributed donations: {e}")
            return False
    
    def get_distributed_donations(self) -> List[Dict[str, Any]]:
        """Get donations distributed in this event"""
        if self.id is None:
            return []
        
        query = """
            SELECT dr.*, d.categoria, d.descripcion, u.nombre, u.apellido
            FROM donaciones_repartidas dr
            JOIN donaciones d ON dr.donacion_id = d.id
            JOIN usuarios u ON dr.usuario_registro = u.id
            WHERE dr.evento_id = %s
            ORDER BY dr.fecha_registro DESC
        """
        
        result = execute_query(query, (self.id,))
        return [dict(row) for row in result] if result else []
    
    @classmethod
    def get_by_id(cls, event_id: int) -> Optional['Event']:
        """Get event by ID"""
        query = "SELECT * FROM eventos WHERE id = %s"
        result = execute_query(query, (event_id,))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_all(cls) -> List['Event']:
        """Get all events"""
        query = "SELECT * FROM eventos ORDER BY fecha_evento DESC"
        result = execute_query(query)
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    @classmethod
    def get_future_events(cls) -> List['Event']:
        """Get future events"""
        query = """
            SELECT * FROM eventos 
            WHERE fecha_evento > CURRENT_TIMESTAMP 
            ORDER BY fecha_evento ASC
        """
        result = execute_query(query)
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    @classmethod
    def get_past_events(cls) -> List['Event']:
        """Get past events"""
        query = """
            SELECT * FROM eventos 
            WHERE fecha_evento <= CURRENT_TIMESTAMP 
            ORDER BY fecha_evento DESC
        """
        result = execute_query(query)
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    @classmethod
    def get_user_events(cls, user_id: int, future_only: bool = False) -> List['Event']:
        """Get events where user is participant"""
        query = """
            SELECT e.* FROM eventos e
            JOIN participantes_evento pe ON e.id = pe.evento_id
            WHERE pe.usuario_id = %s
        """
        params = [user_id]
        
        if future_only:
            query += " AND e.fecha_evento > CURRENT_TIMESTAMP"
        
        query += " ORDER BY e.fecha_evento DESC"
        
        result = execute_query(query, tuple(params))
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    def __str__(self):
        return f"Event(id={self.id}, name={self.nombre}, date={self.fecha_evento})"
    
    def __repr__(self):
        return self.__str__()