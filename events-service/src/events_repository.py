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
    
    def __init__(self):
        self.db = get_db_connection()
    
    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """Método helper para ejecutar queries con manejo de errores"""
        conn = None
        cursor = None
        try:
            conn = self.db.connect()
            if not conn:
                print("❌ No se pudo establecer conexión a la base de datos")
                return None
                
            cursor = self.db.get_cursor()
            if not cursor:
                print("❌ No se pudo obtener cursor de la base de datos")
                return None
            
            cursor.execute(query, params or ())
            
            result = None
            if fetch_one:
                result = cursor.fetchone()
                result = dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                result = [dict(row) for row in results]
            else:
                result = cursor.rowcount
            
            if commit:
                conn.commit()
            
            return result
            
        except Exception as e:
            print(f"❌ Error ejecutando query: {e}")
            if conn and commit:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.db.close()
    
    def create_event(self, name: str, description: str, event_date: str, participant_ids: List[int] = None) -> Optional[Dict[str, Any]]:
        """Create a new event"""
        try:
            # Parse event date
            event_datetime = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
            
            # Validate future date
            if event_datetime <= datetime.now():
                return None
            
            # Create event (MySQL no soporta RETURNING)
            query = """
                INSERT INTO eventos (nombre, descripcion, fecha_evento)
                VALUES (%s, %s, %s)
            """
            params = (name, description, event_datetime)
            
            # Execute insert and get the ID
            conn = self.db.connect()
            if not conn:
                return None
            
            cursor = self.db.get_cursor()
            cursor.execute(query, params)
            event_id = cursor.lastrowid
            conn.commit()
            
            # Fetch the created event
            select_query = """
                SELECT id, nombre, descripcion, fecha_evento, fecha_creacion, fecha_actualizacion, expuesto_red
                FROM eventos WHERE id = %s
            """
            cursor.execute(select_query, (event_id,))
            result = cursor.fetchone()
            cursor.close()
            self.db.close()
            if not result:
                return None
            
            # Add participants if provided
            if participant_ids:
                for user_id in participant_ids:
                    self.add_participant(result['id'], user_id)
            
            return result
            
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get event by ID"""
        try:
            query = "SELECT * FROM eventos WHERE id = %s"
            result = self._execute_query(query, (event_id,), fetch_one=True)
            return result
            
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
            
            # Update event (MySQL no soporta RETURNING)
            query = """
                UPDATE eventos 
                SET nombre = %s, descripcion = %s, fecha_evento = %s
                WHERE id = %s
            """
            params = (name, description, event_datetime, event_id)
            
            # Execute update
            conn = self.db.connect()
            if not conn:
                return None
            
            cursor = self.db.get_cursor()
            cursor.execute(query, params)
            conn.commit()
            
            # Fetch the updated event
            select_query = """
                SELECT id, nombre, descripcion, fecha_evento, fecha_creacion, fecha_actualizacion, expuesto_red
                FROM eventos WHERE id = %s
            """
            cursor.execute(select_query, (event_id,))
            result = cursor.fetchone()
            cursor.close()
            self.db.close()
            
            return result
            
            result = self._execute_query(query, params, fetch_one=True, commit=True)
            return result
            
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
            
            # Use direct connection like other fixed methods
            conn = self.db.connect()
            if not conn:
                return False
            
            cursor = self.db.get_cursor()
            
            # Delete participants first (cascade should handle this, but being explicit)
            cursor.execute("DELETE FROM participantes_evento WHERE evento_id = %s", (event_id,))
            
            # Delete event
            cursor.execute("DELETE FROM eventos WHERE id = %s", (event_id,))
            success = cursor.rowcount > 0
            
            conn.commit()
            cursor.close()
            self.db.close()
            
            return success
            
        except Exception as e:
            print(f"Error deleting event: {e}")
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                self.db.close()
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
                
                result = self._execute_query(query, tuple(params), fetch_all=True)
            else:
                # Get all events
                if include_past_events:
                    query = "SELECT * FROM eventos ORDER BY fecha_evento DESC"
                    result = self._execute_query(query, fetch_all=True)
                else:
                    query = """
                        SELECT * FROM eventos 
                        WHERE fecha_evento > CURRENT_TIMESTAMP 
                        ORDER BY fecha_evento ASC
                    """
                    result = self._execute_query(query, fetch_all=True)
            
            return result if result else []
            
        except Exception as e:
            print(f"Error listing events: {e}")
            return []
    
    def add_participant(self, event_id: int, user_id: int) -> bool:
        """Add participant to event"""
        try:
            # Check if user is active
            user_query = "SELECT activo FROM usuarios WHERE id = %s"
            user_result = self._execute_query(user_query, (user_id,), fetch_one=True)
            
            if not user_result or not user_result['activo']:
                return False
            
            query = """
                INSERT IGNORE INTO participantes_evento (evento_id, usuario_id)
                VALUES (%s, %s)
            """
            self._execute_query(query, (event_id, user_id), commit=True)
            return True
            
        except Exception as e:
            print(f"Error adding participant: {e}")
            return False
    
    def remove_participant(self, event_id: int, user_id: int) -> bool:
        """Remove participant from event"""
        try:
            query = "DELETE FROM participantes_evento WHERE evento_id = %s AND usuario_id = %s"
            result = self._execute_query(query, (event_id, user_id), commit=True)
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
            
            result = self._execute_query(query, (event_id,), fetch_all=True)
            return result if result else []
            
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
            
            registered_donations = []
            
            for donation in donations:
                donation_id = donation['donation_id']
                quantity = donation['quantity']
                
                # Check available quantity first
                check_query = """
                    SELECT cantidad FROM donaciones WHERE id = %s AND eliminado = FALSE
                """
                donation_check = self._execute_query(check_query, (donation_id,), fetch_one=True)
                
                if not donation_check or donation_check['cantidad'] < quantity:
                    print(f"Insufficient quantity for donation {donation_id}. Available: {donation_check['cantidad'] if donation_check else 0}, Requested: {quantity}")
                    continue
                
                # Insert distributed donation record (MySQL no soporta RETURNING)
                insert_query = """
                    INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro)
                    VALUES (%s, %s, %s, %s)
                """
                
                # Execute insert
                conn = self.db.connect()
                if not conn:
                    continue
                
                cursor = self.db.get_cursor()
                cursor.execute(insert_query, (event_id, donation_id, quantity, user_id))
                distributed_id = cursor.lastrowid
                conn.commit()
                
                if distributed_id:
                    # Decrement the donation quantity in inventory
                    update_query = """
                        UPDATE donaciones 
                        SET cantidad = cantidad - %s,
                            fecha_modificacion = CURRENT_TIMESTAMP,
                            usuario_modificacion = %s
                        WHERE id = %s
                    """
                    cursor.execute(update_query, (quantity, user_id, donation_id))
                    conn.commit()
                    print(f"Updated donation {donation_id}: decreased by {quantity}")
                    
                    # Get the created distributed donation record
                    select_query = """
                        SELECT id, evento_id, donacion_id, cantidad_repartida, usuario_registro, fecha_registro
                        FROM donaciones_repartidas WHERE id = %s
                    """
                    cursor.execute(select_query, (distributed_id,))
                    result = cursor.fetchone()
                    
                    # Get donation details for response
                    donation_query = """
                        SELECT d.descripcion, d.categoria
                        FROM donaciones d
                        WHERE d.id = %s
                    """
                    cursor.execute(donation_query, (donation_id,))
                    donation_details = cursor.fetchone()
                    
                    registered_donation = {
                        'id': result['id'],
                        'event_id': result['evento_id'],
                        'donation_id': result['donacion_id'],
                        'donation_description': donation_details['descripcion'] if donation_details else '',
                        'donation_category': donation_details['categoria'] if donation_details else '',
                        'distributed_quantity': result['cantidad_repartida'],
                        'registered_by': result['usuario_registro'],
                        'registration_date': str(result['fecha_registro'])
                    }
                    registered_donations.append(registered_donation)
                
                cursor.close()
                self.db.close()
            
            return registered_donations
            
        except Exception as e:
            print(f"Error registering distributed donations: {e}")
            return []
    
    def get_distributed_donations(self, event_id: int) -> List[Dict[str, Any]]:
        """Get donations distributed in this event"""
        try:
            query = """
                SELECT dr.id, dr.evento_id as event_id, dr.donacion_id as donation_id, 
                       dr.cantidad_repartida as distributed_quantity, dr.usuario_registro as registered_by,
                       dr.fecha_registro as registration_date, d.categoria, d.descripcion as donation_description,
                       u.nombre as registered_by_name, u.apellido as registered_by_lastname
                FROM donaciones_repartidas dr
                JOIN donaciones d ON dr.donacion_id = d.id
                JOIN usuarios u ON dr.usuario_registro = u.id
                WHERE dr.evento_id = %s
                ORDER BY dr.fecha_registro DESC
            """
            
            result = self._execute_query(query, (event_id,), fetch_all=True)
            return result if result else []
            
        except Exception as e:
            print(f"Error getting distributed donations: {e}")
            return []