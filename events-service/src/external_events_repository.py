"""
Repository para gestionar eventos externos de la red de ONGs
Extiende la funcionalidad del events-service para manejar eventos de otras organizaciones
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import sys
import os

# Agregar el directorio padre al path para importar database_fixed
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'user-service', 'src'))
from database_fixed import get_db_connection


class ExternalEventsRepository:
    def __init__(self):
        self.db = get_db_connection()
    
    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, 
                      fetch_all: bool = False, commit: bool = False) -> Any:
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

    # ==================== EVENTOS EXTERNOS ====================
    
    def create_external_event(self, organizacion_id: str, evento_id: str, nombre: str,
                            descripcion: str, fecha_evento: datetime) -> Optional[Dict]:
        """Crea o actualiza un evento externo"""
        query = """
            INSERT INTO eventos_externos (organizacion_id, evento_id, nombre, descripcion, fecha_evento)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (organizacion_id, evento_id) 
            DO UPDATE SET 
                nombre = EXCLUDED.nombre,
                descripcion = EXCLUDED.descripcion,
                fecha_evento = EXCLUDED.fecha_evento,
                activo = true,
                fecha_creacion = CURRENT_TIMESTAMP
            RETURNING id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo, fecha_creacion
        """
        return self._execute_query(
            query, 
            (organizacion_id, evento_id, nombre, descripcion, fecha_evento), 
            fetch_one=True, 
            commit=True
        )
    
    def get_active_external_events(self, include_past: bool = False) -> List[Dict]:
        """Obtiene todos los eventos externos activos"""
        if include_past:
            query = """
                SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, fecha_creacion
                FROM eventos_externos 
                WHERE activo = true 
                ORDER BY fecha_evento ASC
            """
        else:
            query = """
                SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, fecha_creacion
                FROM eventos_externos 
                WHERE activo = true AND fecha_evento > CURRENT_TIMESTAMP
                ORDER BY fecha_evento ASC
            """
        
        return self._execute_query(query, fetch_all=True) or []
    
    def get_external_event_by_id(self, organizacion_id: str, evento_id: str) -> Optional[Dict]:
        """Obtiene un evento específico por organización y ID"""
        query = """
            SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo, fecha_creacion
            FROM eventos_externos 
            WHERE organizacion_id = %s AND evento_id = %s
        """
        return self._execute_query(query, (organizacion_id, evento_id), fetch_one=True)
    
    def get_external_event_by_internal_id(self, internal_id: int) -> Optional[Dict]:
        """Obtiene un evento externo por su ID interno"""
        query = """
            SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo, fecha_creacion
            FROM eventos_externos 
            WHERE id = %s
        """
        return self._execute_query(query, (internal_id,), fetch_one=True)
    
    def deactivate_external_event(self, organizacion_id: str, evento_id: str) -> bool:
        """Desactiva un evento externo (cuando se da de baja)"""
        query = """
            UPDATE eventos_externos 
            SET activo = false
            WHERE organizacion_id = %s AND evento_id = %s
        """
        result = self._execute_query(query, (organizacion_id, evento_id), commit=True)
        return result is not None and result > 0
    
    def get_events_by_organization(self, organizacion_id: str, active_only: bool = True) -> List[Dict]:
        """Obtiene eventos de una organización específica"""
        if active_only:
            query = """
                SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, fecha_creacion
                FROM eventos_externos 
                WHERE organizacion_id = %s AND activo = true
                ORDER BY fecha_evento ASC
            """
        else:
            query = """
                SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo, fecha_creacion
                FROM eventos_externos 
                WHERE organizacion_id = %s
                ORDER BY fecha_evento ASC
            """
        
        return self._execute_query(query, (organizacion_id,), fetch_all=True) or []
    
    def get_upcoming_events(self, days_ahead: int = 30) -> List[Dict]:
        """Obtiene eventos próximos en los siguientes X días"""
        query = """
            SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, fecha_creacion
            FROM eventos_externos 
            WHERE activo = true 
            AND fecha_evento BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '%s days'
            ORDER BY fecha_evento ASC
        """
        return self._execute_query(query, (days_ahead,), fetch_all=True) or []
    
    def search_events(self, search_term: str, active_only: bool = True) -> List[Dict]:
        """Busca eventos por nombre o descripción"""
        if active_only:
            query = """
                SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, fecha_creacion
                FROM eventos_externos 
                WHERE activo = true 
                AND (nombre ILIKE %s OR descripcion ILIKE %s)
                ORDER BY fecha_evento ASC
            """
        else:
            query = """
                SELECT id, organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo, fecha_creacion
                FROM eventos_externos 
                WHERE (nombre ILIKE %s OR descripcion ILIKE %s)
                ORDER BY fecha_evento ASC
            """
        
        search_pattern = f'%{search_term}%'
        return self._execute_query(query, (search_pattern, search_pattern), fetch_all=True) or []

    # ==================== ADHESIONES A EVENTOS EXTERNOS ====================
    
    def get_event_adhesions_count(self, evento_externo_id: int) -> int:
        """Obtiene el número de adhesiones a un evento externo"""
        query = """
            SELECT COUNT(*) as count
            FROM adhesiones_eventos_externos 
            WHERE evento_externo_id = %s AND estado != 'CANCELADA'
        """
        result = self._execute_query(query, (evento_externo_id,), fetch_one=True)
        return result['count'] if result else 0
    
    def get_volunteer_adhesion_status(self, evento_externo_id: int, voluntario_id: int) -> Optional[str]:
        """Obtiene el estado de adhesión de un voluntario a un evento específico"""
        query = """
            SELECT estado FROM adhesiones_eventos_externos 
            WHERE evento_externo_id = %s AND voluntario_id = %s
        """
        result = self._execute_query(query, (evento_externo_id, voluntario_id), fetch_one=True)
        return result['estado'] if result else None
    
    def can_volunteer_join_event(self, evento_externo_id: int, voluntario_id: int) -> Dict:
        """Verifica si un voluntario puede adherirse a un evento externo"""
        result = {
            'can_join': False,
            'reason': '',
            'event_info': None
        }
        
        # Obtener información del evento
        event = self.get_external_event_by_internal_id(evento_externo_id)
        if not event:
            result['reason'] = 'Evento no encontrado'
            return result
        
        result['event_info'] = event
        
        # Verificar si el evento está activo
        if not event['activo']:
            result['reason'] = 'El evento no está activo'
            return result
        
        # Verificar si el evento ya pasó
        if event['fecha_evento'] < datetime.now():
            result['reason'] = 'El evento ya ha pasado'
            return result
        
        # Verificar si ya está adherido
        current_status = self.get_volunteer_adhesion_status(evento_externo_id, voluntario_id)
        if current_status == 'CONFIRMADA':
            result['reason'] = 'Ya está adherido a este evento'
            return result
        elif current_status == 'PENDIENTE':
            result['reason'] = 'Ya tiene una adhesión pendiente'
            return result
        
        # Verificar conflictos con eventos locales
        conflict_query = """
            SELECT e.nombre, e.fecha_evento
            FROM eventos e
            JOIN participantes_evento pe ON e.id = pe.evento_id
            WHERE pe.usuario_id = %s
            AND e.fecha_evento::date = %s::date
        """
        conflicts = self._execute_query(
            conflict_query, 
            (voluntario_id, event['fecha_evento']), 
            fetch_all=True
        ) or []
        
        if conflicts:
            result['reason'] = f'Conflicto con evento local: {conflicts[0]["nombre"]}'
            return result
        
        result['can_join'] = True
        result['reason'] = 'Puede adherirse al evento'
        return result

    # ==================== LIMPIEZA Y MANTENIMIENTO ====================
    
    def cleanup_old_events(self, days_old: int = 90) -> int:
        """Limpia eventos externos antiguos (más de X días después de su fecha)"""
        query = """
            DELETE FROM eventos_externos 
            WHERE fecha_evento < CURRENT_TIMESTAMP - INTERVAL '%s days'
            AND activo = false
        """
        result = self._execute_query(query, (days_old,), commit=True)
        return result if result is not None else 0
    
    def deactivate_past_events(self) -> int:
        """Desactiva eventos que ya pasaron"""
        query = """
            UPDATE eventos_externos 
            SET activo = false
            WHERE fecha_evento < CURRENT_TIMESTAMP - INTERVAL '1 day'
            AND activo = true
        """
        result = self._execute_query(query, commit=True)
        return result if result is not None else 0

    # ==================== ESTADÍSTICAS ====================
    
    def get_events_statistics(self) -> Dict:
        """Obtiene estadísticas de eventos externos"""
        stats = {
            'total_active': 0,
            'total_inactive': 0,
            'upcoming_events': 0,
            'by_organization': {},
            'total_adhesions': 0
        }
        
        # Total de eventos activos e inactivos
        query = """
            SELECT activo, COUNT(*) as count
            FROM eventos_externos
            GROUP BY activo
        """
        results = self._execute_query(query, fetch_all=True) or []
        
        for result in results:
            if result['activo']:
                stats['total_active'] = result['count']
            else:
                stats['total_inactive'] = result['count']
        
        # Eventos próximos (próximos 30 días)
        query = """
            SELECT COUNT(*) as count
            FROM eventos_externos
            WHERE activo = true 
            AND fecha_evento BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '30 days'
        """
        result = self._execute_query(query, fetch_one=True)
        stats['upcoming_events'] = result['count'] if result else 0
        
        # Por organización
        query = """
            SELECT organizacion_id, COUNT(*) as count
            FROM eventos_externos
            WHERE activo = true
            GROUP BY organizacion_id
            ORDER BY count DESC
        """
        org_results = self._execute_query(query, fetch_all=True) or []
        stats['by_organization'] = {r['organizacion_id']: r['count'] for r in org_results}
        
        # Total de adhesiones
        query = """
            SELECT COUNT(*) as count
            FROM adhesiones_eventos_externos
            WHERE estado != 'CANCELADA'
        """
        result = self._execute_query(query, fetch_one=True)
        stats['total_adhesions'] = result['count'] if result else 0
        
        return stats