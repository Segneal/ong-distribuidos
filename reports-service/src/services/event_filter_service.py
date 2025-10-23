"""
Service for handling saved event filters
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.filter import SavedFilter, FilterType
from ..models.user import User
from ..utils.database_utils import get_db_session
import json
import uuid


class EventFilterService:
    """Service for handling saved event filters"""
    
    def __init__(self):
        pass
    
    def get_saved_filters(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all saved event filters for a user
        
        Args:
            user_id: ID of the user
        
        Returns:
            List of saved filters
        """
        with get_db_session() as session:
            filters = session.query(SavedFilter).filter(
                SavedFilter.usuario_id == user_id,
                SavedFilter.tipo == FilterType.EVENTOS
            ).order_by(SavedFilter.fecha_creacion.desc()).all()
            
            result = []
            for filter_obj in filters:
                try:
                    filtros_data = filter_obj.configuracion if filter_obj.configuracion else {}
                    # Only include event filters (those with filter_subtype = 'EVENT')
                    if filtros_data.get('filter_subtype') == 'EVENT':
                        result.append({
                            'id': str(filter_obj.id),
                            'nombre': filter_obj.nombre,
                            'filtros': {
                                'usuarioId': filtros_data.get('usuario_id'),
                                'fechaDesde': filtros_data.get('fecha_desde'),
                                'fechaHasta': filtros_data.get('fecha_hasta'),
                                'repartodonaciones': filtros_data.get('repartodonaciones')
                            },
                            'fechaCreacion': filter_obj.fecha_creacion
                        })
                except Exception:
                    # Skip invalid filters
                    continue
            
            return result
    
    def save_filter(
        self,
        user_id: int,
        nombre: str,
        filtros: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save a new event filter
        
        Args:
            user_id: ID of the user
            nombre: Name of the filter
            filtros: Filter parameters
        
        Returns:
            Saved filter data
        """
        with get_db_session() as session:
            # Check if user exists
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            
            # Create filter data with event identifier
            configuracion = {
                'filter_subtype': 'EVENT',  # Identifier for event filters
                'usuario_id': filtros.get('usuarioId'),
                'fecha_desde': filtros.get('fechaDesde'),
                'fecha_hasta': filtros.get('fechaHasta'),
                'repartodonaciones': filtros.get('repartodonaciones')
            }
            
            # Create new filter
            new_filter = SavedFilter(
                nombre=nombre,
                tipo=FilterType.EVENTOS,
                configuracion=configuracion,
                usuario_id=user_id
            )
            
            session.add(new_filter)
            session.commit()
            session.refresh(new_filter)
            
            return {
                'id': str(new_filter.id),
                'nombre': new_filter.nombre,
                'filtros': {
                    'usuarioId': filtros.get('usuarioId'),
                    'fechaDesde': filtros.get('fechaDesde'),
                    'fechaHasta': filtros.get('fechaHasta'),
                    'repartodonaciones': filtros.get('repartodonaciones')
                },
                'fechaCreacion': new_filter.fecha_creacion
            }
    
    def update_filter(
        self,
        filter_id: str,
        user_id: int,
        nombre: Optional[str] = None,
        filtros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing event filter
        
        Args:
            filter_id: ID of the filter to update
            user_id: ID of the user (for permission check)
            nombre: New name (optional)
            filtros: New filter parameters (optional)
        
        Returns:
            Updated filter data
        """
        with get_db_session() as session:
            # Get the filter
            filter_obj = session.query(SavedFilter).filter(
                SavedFilter.id == int(filter_id),
                SavedFilter.usuario_id == user_id,
                SavedFilter.tipo == FilterType.EVENTOS
            ).first()
            
            if not filter_obj:
                raise ValueError(f"Filter with ID {filter_id} not found or access denied")
            
            # Update fields
            if nombre is not None:
                filter_obj.nombre = nombre
            
            if filtros is not None:
                configuracion = {
                    'filter_subtype': 'EVENT',  # Maintain event identifier
                    'usuario_id': filtros.get('usuarioId'),
                    'fecha_desde': filtros.get('fechaDesde'),
                    'fecha_hasta': filtros.get('fechaHasta'),
                    'repartodonaciones': filtros.get('repartodonaciones')
                }
                filter_obj.configuracion = configuracion
            
            filter_obj.fecha_actualizacion = datetime.utcnow()
            
            session.commit()
            session.refresh(filter_obj)
            
            # Parse updated filtros
            filtros_data = filter_obj.configuracion if filter_obj.configuracion else {}
            
            return {
                'id': str(filter_obj.id),
                'nombre': filter_obj.nombre,
                'filtros': {
                    'usuarioId': filtros_data.get('usuario_id'),
                    'fechaDesde': filtros_data.get('fecha_desde'),
                    'fechaHasta': filtros_data.get('fecha_hasta'),
                    'repartodonaciones': filtros_data.get('repartodonaciones')
                },
                'fechaCreacion': filter_obj.fecha_creacion
            }
    
    def delete_filter(self, filter_id: str, user_id: int) -> bool:
        """
        Delete an event filter
        
        Args:
            filter_id: ID of the filter to delete
            user_id: ID of the user (for permission check)
        
        Returns:
            True if deleted successfully
        """
        with get_db_session() as session:
            # Get the filter
            filter_obj = session.query(SavedFilter).filter(
                SavedFilter.id == int(filter_id),
                SavedFilter.usuario_id == user_id,
                SavedFilter.tipo == FilterType.EVENTOS
            ).first()
            
            if not filter_obj:
                raise ValueError(f"Filter with ID {filter_id} not found or access denied")
            
            session.delete(filter_obj)
            session.commit()
            
            return True