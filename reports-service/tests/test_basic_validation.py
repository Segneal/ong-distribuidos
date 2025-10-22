"""
Basic validation tests for reports-service components.
These tests validate that the core components can be imported and instantiated.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestBasicValidation:
    """Basic validation tests for system components."""
    
    def test_model_imports(self):
        """Test that model classes can be imported."""
        from src.models.donation import Donation, DonationCategory
        from src.models.event import Event
        from src.models.filter import SavedFilter, FilterType
        from src.models.user import User, UserRole
        
        # Test enum values
        assert DonationCategory.ROPA is not None
        assert UserRole.PRESIDENTE is not None
        assert FilterType.DONACIONES is not None
        
    def test_service_imports(self):
        """Test that service classes can be imported."""
        from src.services.donation_service import DonationService
        from src.services.event_service import EventService
        from src.services.filter_service import FilterService
        from src.services.excel_service import ExcelExportService
        
        # Test instantiation
        donation_service = DonationService()
        event_service = EventService()
        filter_service = FilterService()
        excel_service = ExcelExportService()
        
        assert donation_service is not None
        assert event_service is not None
        assert filter_service is not None
        assert excel_service is not None
    
    def test_user_access_validation(self, mock_user, mock_voluntario):
        """Test user access validation logic."""
        from src.services.donation_service import DonationService
        from src.services.event_service import EventService
        
        donation_service = DonationService()
        event_service = EventService()
        
        # Test donation access (Presidente should have access)
        assert donation_service.validate_user_access(mock_user) == True
        
        # Test event access (both should have access to their own data)
        assert event_service.validate_user_access(mock_user, mock_user.id) == True
        assert event_service.validate_user_access(mock_voluntario, mock_voluntario.id) == True
        
        # Test cross-user access (only Presidente should access other's data)
        assert event_service.validate_user_access(mock_user, mock_voluntario.id) == True
        assert event_service.validate_user_access(mock_voluntario, mock_user.id) == False
    
    def test_filter_validation(self):
        """Test filter configuration validation."""
        from src.services.filter_service import FilterService
        from src.models.filter import FilterType
        
        filter_service = FilterService()
        
        # Test valid donation filter
        donation_config = {
            'categoria': 'ROPA',
            'fecha_desde': '2024-01-01T00:00:00',
            'fecha_hasta': '2024-12-31T23:59:59',
            'eliminado': False
        }
        
        validated_config = filter_service._validate_filter_configuration(
            donation_config, 
            FilterType.DONACIONES
        )
        assert len(validated_config) > 0
        
        # Test valid event filter
        event_config = {
            'fecha_desde': '2024-01-01T00:00:00',
            'fecha_hasta': '2024-12-31T23:59:59',
            'usuario_id': 1,
            'repartodonaciones': True
        }
        
        validated_config = filter_service._validate_filter_configuration(
            event_config, 
            FilterType.EVENTOS
        )
        assert len(validated_config) > 0
        
        # Test invalid configuration should raise ValueError
        invalid_config = {
            'categoria': 'INVALID_CATEGORY',
            'fecha_desde': 'invalid-date',
            'eliminado': 'not-a-boolean'
        }
        
        with pytest.raises(ValueError):
            filter_service._validate_filter_configuration(
                invalid_config, 
                FilterType.DONACIONES
            )
    
    def test_rest_router_import(self):
        """Test that REST router can be imported."""
        try:
            from src.rest.router import router
            assert router is not None
        except ImportError as e:
            if "cgi" in str(e):
                pytest.skip("REST router import skipped due to Python 3.13 compatibility issue")
            else:
                raise
    
    def test_config_import(self):
        """Test that configuration can be imported."""
        from src.config import settings
        assert settings is not None