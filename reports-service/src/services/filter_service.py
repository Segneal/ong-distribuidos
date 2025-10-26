"""
Filter service for managing saved filters for donations and events.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.filter import SavedFilter, FilterType
from ..models.user import User
from ..utils.database_utils import get_db_session
import json


class FilterService:
    """Service for managing saved filters"""
    
    def __init__(self):
        pass
    
    def create_filter(
        self,
        usuario_id: int,
        nombre: str,
        tipo: FilterType,
        configuracion: Dict[str, Any]
    ) -> SavedFilter:
        """
        Create a new saved filter.
        
        Args:
            usuario_id: ID of the user creating the filter
            nombre: Name for the filter
            tipo: Type of filter (DONACIONES or EVENTOS)
            configuracion: Filter configuration as dictionary
        
        Returns:
            Created SavedFilter object
        
        Raises:
            ValueError: If filter name already exists for user and type
        """
        with get_db_session() as session:
            # Check if filter name already exists for this user and type
            existing_filter = session.query(SavedFilter).filter(
                and_(
                    SavedFilter.usuario_id == usuario_id,
                    SavedFilter.nombre == nombre,
                    SavedFilter.tipo == tipo
                )
            ).first()
            
            if existing_filter:
                raise ValueError(f"Filter with name '{nombre}' already exists for this user and type")
            
            # Validate and serialize configuration
            validated_config = self._validate_filter_configuration(configuracion, tipo)
            
            # Create new filter
            new_filter = SavedFilter(
                usuario_id=usuario_id,
                nombre=nombre,
                tipo=tipo,
                configuracion=validated_config
            )
            
            session.add(new_filter)
            session.commit()
            session.refresh(new_filter)
            
            return new_filter
    
    def get_user_filters(
        self,
        usuario_id: int,
        tipo: Optional[FilterType] = None
    ) -> List[SavedFilter]:
        """
        Get all saved filters for a user.
        
        Args:
            usuario_id: ID of the user
            tipo: Optional filter type to filter by
        
        Returns:
            List of SavedFilter objects
        """
        with get_db_session() as session:
            query = session.query(SavedFilter).filter(
                SavedFilter.usuario_id == usuario_id
            )
            
            if tipo is not None:
                query = query.filter(SavedFilter.tipo == tipo)
            
            # Order by creation date descending
            query = query.order_by(SavedFilter.fecha_creacion.desc())
            
            return query.all()
    
    def get_filter_by_id(
        self,
        filter_id: int,
        usuario_id: Optional[int] = None
    ) -> Optional[SavedFilter]:
        """
        Get a saved filter by ID.
        
        Args:
            filter_id: ID of the filter
            usuario_id: Optional user ID to ensure ownership
        
        Returns:
            SavedFilter object or None if not found
        """
        with get_db_session() as session:
            query = session.query(SavedFilter).filter(
                SavedFilter.id == filter_id
            )
            
            if usuario_id is not None:
                query = query.filter(SavedFilter.usuario_id == usuario_id)
            
            return query.first()
    
    def update_filter(
        self,
        filter_id: int,
        usuario_id: int,
        nombre: Optional[str] = None,
        configuracion: Optional[Dict[str, Any]] = None
    ) -> SavedFilter:
        """
        Update an existing saved filter.
        
        Args:
            filter_id: ID of the filter to update
            usuario_id: ID of the user (for ownership validation)
            nombre: New name for the filter (optional)
            configuracion: New configuration for the filter (optional)
        
        Returns:
            Updated SavedFilter object
        
        Raises:
            ValueError: If filter not found or name already exists
        """
        with get_db_session() as session:
            # Get existing filter
            existing_filter = session.query(SavedFilter).filter(
                and_(
                    SavedFilter.id == filter_id,
                    SavedFilter.usuario_id == usuario_id
                )
            ).first()
            
            if not existing_filter:
                raise ValueError(f"Filter with ID {filter_id} not found for user {usuario_id}")
            
            # Check if new name conflicts with existing filters
            if nombre is not None and nombre != existing_filter.nombre:
                name_conflict = session.query(SavedFilter).filter(
                    and_(
                        SavedFilter.usuario_id == usuario_id,
                        SavedFilter.nombre == nombre,
                        SavedFilter.tipo == existing_filter.tipo,
                        SavedFilter.id != filter_id
                    )
                ).first()
                
                if name_conflict:
                    raise ValueError(f"Filter with name '{nombre}' already exists for this user and type")
                
                existing_filter.nombre = nombre
            
            # Update configuration if provided
            if configuracion is not None:
                validated_config = self._validate_filter_configuration(configuracion, existing_filter.tipo)
                existing_filter.configuracion = validated_config
            
            # Update timestamp
            existing_filter.fecha_actualizacion = datetime.utcnow()
            
            session.commit()
            session.refresh(existing_filter)
            
            return existing_filter
    
    def delete_filter(
        self,
        filter_id: int,
        usuario_id: int
    ) -> bool:
        """
        Delete a saved filter.
        
        Args:
            filter_id: ID of the filter to delete
            usuario_id: ID of the user (for ownership validation)
        
        Returns:
            True if filter was deleted, False if not found
        """
        with get_db_session() as session:
            # Get existing filter
            existing_filter = session.query(SavedFilter).filter(
                and_(
                    SavedFilter.id == filter_id,
                    SavedFilter.usuario_id == usuario_id
                )
            ).first()
            
            if not existing_filter:
                return False
            
            session.delete(existing_filter)
            session.commit()
            
            return True
    
    def _validate_filter_configuration(
        self,
        configuracion: Dict[str, Any],
        tipo: FilterType
    ) -> Dict[str, Any]:
        """
        Validate and normalize filter configuration.
        
        Args:
            configuracion: Filter configuration to validate
            tipo: Type of filter
        
        Returns:
            Validated and normalized configuration
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(configuracion, dict):
            raise ValueError("Configuration must be a dictionary")
        
        validated_config = {}
        
        if tipo == FilterType.DONACIONES:
            # Validate donation filter configuration
            allowed_keys = ['categoria', 'fecha_desde', 'fecha_hasta', 'eliminado']
            
            for key, value in configuracion.items():
                if key not in allowed_keys:
                    continue  # Skip unknown keys
                
                if key == 'categoria' and value is not None:
                    # Validate category enum value
                    from ..models.donation import DonationCategory
                    if value not in [cat.value for cat in DonationCategory]:
                        raise ValueError(f"Invalid donation category: {value}")
                    validated_config[key] = value
                
                elif key in ['fecha_desde', 'fecha_hasta'] and value is not None:
                    # Validate date format
                    if isinstance(value, str):
                        try:
                            datetime.fromisoformat(value.replace('Z', '+00:00'))
                            validated_config[key] = value
                        except ValueError:
                            raise ValueError(f"Invalid date format for {key}: {value}")
                    elif isinstance(value, datetime):
                        validated_config[key] = value.isoformat()
                    else:
                        raise ValueError(f"Invalid date type for {key}: {type(value)}")
                
                elif key == 'eliminado' and value is not None:
                    # Validate boolean
                    if not isinstance(value, bool):
                        raise ValueError(f"Invalid boolean value for eliminado: {value}")
                    validated_config[key] = value
        
        elif tipo == FilterType.EVENTOS:
            # Validate event filter configuration
            allowed_keys = ['fecha_desde', 'fecha_hasta', 'usuario_id', 'repartodonaciones']
            
            for key, value in configuracion.items():
                if key not in allowed_keys:
                    continue  # Skip unknown keys
                
                if key in ['fecha_desde', 'fecha_hasta'] and value is not None:
                    # Validate date format
                    if isinstance(value, str):
                        try:
                            datetime.fromisoformat(value.replace('Z', '+00:00'))
                            validated_config[key] = value
                        except ValueError:
                            raise ValueError(f"Invalid date format for {key}: {value}")
                    elif isinstance(value, datetime):
                        validated_config[key] = value.isoformat()
                    else:
                        raise ValueError(f"Invalid date type for {key}: {type(value)}")
                
                elif key == 'usuario_id' and value is not None:
                    # Validate user ID
                    if not isinstance(value, int) or value <= 0:
                        raise ValueError(f"Invalid user ID: {value}")
                    validated_config[key] = value
                
                elif key == 'repartodonaciones' and value is not None:
                    # Validate boolean
                    if not isinstance(value, bool):
                        raise ValueError(f"Invalid boolean value for repartodonaciones: {value}")
                    validated_config[key] = value
        
        return validated_config
    
    def deserialize_filter_configuration(
        self,
        saved_filter: SavedFilter
    ) -> Dict[str, Any]:
        """
        Deserialize filter configuration for use in queries.
        
        Args:
            saved_filter: SavedFilter object
        
        Returns:
            Deserialized configuration with proper data types
        """
        config = saved_filter.configuracion.copy()
        
        # Convert date strings back to datetime objects
        for date_key in ['fecha_desde', 'fecha_hasta']:
            if date_key in config and config[date_key] is not None:
                if isinstance(config[date_key], str):
                    config[date_key] = datetime.fromisoformat(config[date_key].replace('Z', '+00:00'))
        
        # Convert category string back to enum if needed
        if saved_filter.tipo == FilterType.DONACIONES and 'categoria' in config and config['categoria'] is not None:
            from ..models.donation import DonationCategory
            config['categoria'] = DonationCategory(config['categoria'])
        
        return config
    
    def get_filter_summary(self, usuario_id: int) -> Dict[str, Any]:
        """
        Get summary of saved filters for a user.
        
        Args:
            usuario_id: ID of the user
        
        Returns:
            Dictionary with filter summary statistics
        """
        with get_db_session() as session:
            # Count filters by type
            donation_filters = session.query(SavedFilter).filter(
                and_(
                    SavedFilter.usuario_id == usuario_id,
                    SavedFilter.tipo == FilterType.DONACIONES
                )
            ).count()
            
            event_filters = session.query(SavedFilter).filter(
                and_(
                    SavedFilter.usuario_id == usuario_id,
                    SavedFilter.tipo == FilterType.EVENTOS
                )
            ).count()
            
            total_filters = donation_filters + event_filters
            
            return {
                'total_filters': total_filters,
                'donation_filters': donation_filters,
                'event_filters': event_filters
            }