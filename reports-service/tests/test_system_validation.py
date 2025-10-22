"""
System validation tests to ensure all components are properly configured.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestSystemValidation:
    """Test system components are properly configured."""
    
    def test_imports_work(self):
        """Test that all main imports work correctly."""
        # Test service imports
        from src.services.donation_service import DonationService
        from src.services.event_service import EventService
        from src.services.filter_service import FilterService
        from src.services.excel_service import ExcelService
        from src.services.soap_service import get_soap_service
        
        # Test model imports
        from src.models.donation import Donation, DonationCategory
        from src.models.event import Event
        from src.models.filter import SavedFilter, FilterType
        from src.models.user import User, UserRole
        
        # Test GraphQL imports
        from src.gql.schema import schema
        from src.gql.context import GraphQLContext
        
        # Test REST imports
        from src.rest.router import router
        
        # Test SOAP imports
        from src.soap.client import get_soap_client
        
        assert True  # If we get here, all imports worked
    
    def test_services_instantiate(self):
        """Test that services can be instantiated."""
        from src.services.donation_service import DonationService
        from src.services.event_service import EventService
        from src.services.filter_service import FilterService
        from src.services.excel_service import ExcelService
        
        # Test service instantiation
        donation_service = DonationService()
        event_service = EventService()
        filter_service = FilterService()
        excel_service = ExcelService()
        
        assert donation_service is not None
        assert event_service is not None
        assert filter_service is not None
        assert excel_service is not None
    
    def test_enums_available(self):
        """Test that enums are properly defined."""
        from src.models.donation import DonationCategory
        from src.models.user import UserRole
        from src.models.filter import FilterType
        
        # Test donation categories
        categories = list(DonationCategory)
        assert len(categories) > 0
        assert DonationCategory.ROPA in categories
        
        # Test user roles
        roles = list(UserRole)
        assert len(roles) > 0
        assert UserRole.PRESIDENTE in roles
        assert UserRole.VOLUNTARIO in roles
        
        # Test filter types
        filter_types = list(FilterType)
        assert len(filter_types) > 0
        assert FilterType.DONACIONES in filter_types
        assert FilterType.EVENTOS in filter_types
    
    def test_graphql_schema_exists(self):
        """Test that GraphQL schema is properly configured."""
        from src.gql.schema import schema
        
        assert schema is not None
        
        # Check that schema has basic structure
        schema_str = str(schema)
        assert "Query" in schema_str or "query" in schema_str.lower()
    
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