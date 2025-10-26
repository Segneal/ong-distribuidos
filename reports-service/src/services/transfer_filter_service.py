"""
Service for handling saved transfer filters
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.filter import SavedFilter, FilterType
from ..models.user import User
from ..utils.database_utils import get_db_session
import json


class TransferFilterService:
    """Service for handling saved transfer filters"""
    
    def __init__(self):
        pass
    
    def get_saved_filters(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all saved transfer filters for a user
        
        Args:
            user_id: ID of the user
        
        Returns:
            List of saved filters
        """
        with get_db_session() as session:
            filters = session.query(SavedFilter).filter(
                SavedFilter.usuario_id == user_id,
                SavedFilter.tipo == FilterType.DONACIONES  # Reusing DONACIONES type for transfers
            ).order_by(SavedFilter.fecha_creacion.desc()).all()
            
            result = []
            for filter_obj in filters:
                try:
                    filtros_data = filter_obj.configuracion if filter_obj.configuracion else {}
                    # Only include transfer filters (those with filter_subtype = 'TRANSFER')
                    if filtros_data.get('filter_subtype') == 'TRANSFER':
                        result.append({
                            'id': str(filter_obj.id),
                            'nombre': filter_obj.nombre,
                            'filtros': {
                                'tipo': filtros_data.get('tipo'),
                                'fechaDesde': filtros_data.get('fecha_desde'),
                                'fechaHasta': filtros_data.get('fecha_hasta'),
                                'estado': filtros_data.get('estado')
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
        Save a new transfer filter
        
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
            
            # Create filter data with transfer identifier
            configuracion = {
                'filter_subtype': 'TRANSFER',  # Identifier for transfer filters
                'tipo': filtros.get('tipo'),
                'fecha_desde': filtros.get('fechaDesde'),
                'fecha_hasta': filtros.get('fechaHasta'),
                'estado': filtros.get('estado')
            }
            
            # Create new filter
            new_filter = SavedFilter(
                nombre=nombre,
                tipo=FilterType.DONACIONES,  # Reusing DONACIONES type
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
                    'tipo': filtros.get('tipo'),
                    'fechaDesde': filtros.get('fechaDesde'),
                    'fechaHasta': filtros.get('fechaHasta'),
                    'estado': filtros.get('estado')
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
        Update an existing transfer filter
        
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
                SavedFilter.tipo == FilterType.DONACIONES
            ).first()
            
            if not filter_obj:
                raise ValueError(f"Filter with ID {filter_id} not found or access denied")
            
            # Check if it's a transfer filter
            if not filter_obj.configuracion or filter_obj.configuracion.get('filter_subtype') != 'TRANSFER':
                raise ValueError(f"Filter with ID {filter_id} is not a transfer filter")
            
            # Update fields
            if nombre is not None:
                filter_obj.nombre = nombre
            
            if filtros is not None:
                configuracion = {
                    'filter_subtype': 'TRANSFER',  # Maintain transfer identifier
                    'tipo': filtros.get('tipo'),
                    'fecha_desde': filtros.get('fechaDesde'),
                    'fecha_hasta': filtros.get('fechaHasta'),
                    'estado': filtros.get('estado')
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
                    'tipo': filtros_data.get('tipo'),
                    'fechaDesde': filtros_data.get('fecha_desde'),
                    'fechaHasta': filtros_data.get('fecha_hasta'),
                    'estado': filtros_data.get('estado')
                },
                'fechaCreacion': filter_obj.fecha_creacion
            }
    
    def delete_filter(self, filter_id: str, user_id: int) -> bool:
        """
        Delete a transfer filter
        
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
                SavedFilter.tipo == FilterType.DONACIONES
            ).first()
            
            if not filter_obj:
                raise ValueError(f"Filter with ID {filter_id} not found or access denied")
            
            # Check if it's a transfer filter
            if not filter_obj.configuracion or filter_obj.configuracion.get('filter_subtype') != 'TRANSFER':
                raise ValueError(f"Filter with ID {filter_id} is not a transfer filter")
            
            session.delete(filter_obj)
            session.commit()
            
            return True