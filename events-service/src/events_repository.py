"""
Events Repository for database operations
"""
import sys
import os

# Add shared models to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database_fixed import get_db_connection
from datetime import datetime
from typing import Optional, List, Dict, Any

class EventsRepository:
    """Repository for events database operations"""
    
    def create_event(self, name: str, description: str, event_date: str, participant_ids: List[int] = None) -> Optional[Dict[str, Any]]:
        """Create a new event"""
        try:
            # Parse event date
            event_datetime = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
            
            # Validate future date
            if event_datetime <= datetime.now():
                return None
            
            # Create event
            query = """
                INSERT INTO eventos (nombre, descripcion, fecha_evento)
                VALUES (%s, %s, %s)
                RETURNING id, nombre, descripcion, fecha_evento, fecha_creacion, fecha_actualizacion
            """
            params = (name, description, event_datetime)
            
            result = execute_query(query, params)
            if not result:
                return None
            
            event_data = dict(result[0])
            
            # Add participants if provided
            if participant_ids:
                for user_id in participant_ids:
                    self.add_participant(event_data['id'], user_id)
            
            return event_data
            
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get event by ID"""
        try:
            query = "SELECT * FROM eventos WHERE id = %s"
            result = execute_query(query, (event_id,))
            
            if result:
                return dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error getting event: {e}")
            return None
    
    def update_event(self, event_id: int, name: str, description: str, event_date: str) -> Optional[Dict[str, Any]]:
        """Update an existing event"""
        try:
            # Parse event date
            event_datetime = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
            
            # Validate future date for new date
            if event_datetime <= datetime.now():
                return None
            
            query = """
                UPDATE eventos 
                SET nombre = %s, descripcion = %s, fecha_evento = %s
                WHERE id = %s
                RETURNING id, nombre, descripcion, fecha_evento, fecha_creacion, fecha_actualizacion
            """
            params = (name, description, event_datetime, event_id)
            
            result = execute_query(query, params)
            if result:
                return dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error updating event: {e}")
            return None
    
    def delete_event(self, event_id: int) -> bool:
        """Delete event (only if future event)"""
        try:
            # Check if event exists and is in the future
            event = self.get_event_by_id(event_id)
            if not event:
                return False
            
            event_date = event['fecha_evento']
            if event_date <= datetime.now():
                return False  # Cannot delete past events
            
            # Delete participants first (cascade should handle this, but being explicit)
            execute_query("DELETE FROM participantes_evento WHERE evento_id = %s", (event_id,), fetch=False)
            
            # Delete event
            result = execute_query("DELETE FROM eventos WHERE id = %s", (event_id,), fetch=False)
            return result > 0
            
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    def list_events(self, include_past_events: bool = True, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List events with optional filters"""
        try:
            if user_id:
                # Get events where user is participant
                query = """
                    SELECT e.* FROM eventos e
                    JOIN participantes_evento pe ON e.id = pe.evento_id
                    WHERE pe.usuario_id = %s
                """
                params = [user_id]
                
                if not include_past_events:
                    query += " AND e.fecha_evento > CURRENT_TIMESTAMP"
                
                query += " ORDER BY e.fecha_evento DESC"
                
                result = execute_query(query, tuple(params))
            else:
                # Get all events
                if include_past_events:
                    query = "SELECT * FROM eventos ORDER BY fecha_evento DESC"
                    result = execute_query(query)
                else:
                    query = """
                        SELECT * FROM eventos 
                        WHERE fecha_evento > CURRENT_TIMESTAMP 
                        ORDER BY fecha_evento ASC
                    """
                    result = execute_query(query)
            
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            print(f"Error listing events: {e}")
            return []
    
    def add_participant(self, event_id: int, user_id: int) -> bool:
        """Add participant to event"""
        try:
            # Check if user is active
            user_query = "SELECT activo FROM usuarios WHERE id = %s"
            user_result = execute_query(user_query, (user_id,))
            
            if not user_result or not user_result[0]['activo']:
                return False
            
            query = """
                INSERT INTO participantes_evento (evento_id, usuario_id)
                VALUES (%s, %s)
                ON CONFLICT (evento_id, usuario_id) DO NOTHING
            """
            execute_query(query, (event_id, user_id), fetch=False)
            return True
            
        except Exception as e:
            print(f"Error adding participant: {e}")
            return False
    
    def remove_participant(self, event_id: int, user_id: int) -> bool:
        """Remove participant from event"""
        try:
            query = "DELETE FROM participantes_evento WHERE evento_id = %s AND usuario_id = %s"
            result = execute_query(query, (event_id, user_id), fetch=False)
            return result > 0
            
        except Exception as e:
            print(f"Error removing participant: {e}")
            return False
    
    def list_participants(self, event_id: int) -> List[Dict[str, Any]]:
        """Get event participants"""
        try:
            query = """
                SELECT u.id, u.nombre_usuario, u.nombre, u.apellido, u.email, u.telefono, u.rol,
                       pe.fecha_adhesion
                FROM usuarios u
                JOIN participantes_evento pe ON u.id = pe.usuario_id
                WHERE pe.evento_id = %s AND u.activo = TRUE
                ORDER BY u.nombre, u.apellido
            """
            
            result = execute_query(query, (event_id,))
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            print(f"Error listing participants: {e}")
            return []
    
    def register_distributed_donations(self, event_id: int, donations: List[Dict[str, Any]], user_id: int) -> List[Dict[str, Any]]:
        """Register donations distributed in this event"""
        try:
            # Check if event exists and is in the past
            event = self.get_event_by_id(event_id)
            if not event or event['fecha_evento'] > datetime.now():
                return []
            
            queries = []
            distributed_donations = []
            
            for donation_data in donations:
                donation_id = donation_data.get('donation_id')
                cantidad_repartida = donation_data.get('quantity', 0)
                
                if cantidad_repartida <= 0:
                    continue
                
                # Check if donation exists and has enough quantity
                donation_query = "SELECT * FROM donaciones WHERE id = %s AND eliminado = FALSE"
                donation_result = execute_query(donation_query, (donation_id,))
                
                if not donation_result or donation_result[0]['cantidad'] < cantidad_repartida:
                    continue
                
                # Register distributed donation
                queries.append((
                    """
                    INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (event_id, donation_id, cantidad_repartida, user_id)
                ))
                
                # Reduce inventory
                queries.append((
                    """
                    UPDATE donaciones 
                    SET cantidad = cantidad - %s,
                        fecha_modificacion = CURRENT_TIMESTAMP,
                        usuario_modificacion = %s
                    WHERE id = %s
                    """,
                    (cantidad_repartida, user_id, donation_id)
                ))
                
                distributed_donations.append({
                    'event_id': event_id,
                    'donation_id': donation_id,
                    'distributed_quantity': cantidad_repartida,
                    'registered_by': user_id,
                    'donation_description': donation_result[0]['descripcion']
                })
            
            if queries:
                execute_transaction(queries)
            
            return distributed_donations
            
        except Exception as e:
            print(f"Error registering distributed donations: {e}")
            return []
    
    def get_distributed_donations(self, event_id: int) -> List[Dict[str, Any]]:
        """Get donations distributed in this event"""
        try:
            query = """
                SELECT dr.*, d.categoria, d.descripcion, u.nombre, u.apellido
                FROM donaciones_repartidas dr
                JOIN donaciones d ON dr.donacion_id = d.id
                JOIN usuarios u ON dr.usuario_registro = u.id
                WHERE dr.evento_id = %s
                ORDER BY dr.fecha_registro DESC
            """
            
            result = execute_query(query, (event_id,))
            return [dict(row) for row in result] if result else []
            
        except Exception as e:
            print(f"Error getting distributed donations: {e}")
            return []