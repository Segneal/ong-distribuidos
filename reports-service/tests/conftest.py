"""
Pytest configuration and fixtures for reports-service tests.
"""
import pytest
import sys
import os
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    from src.models.user import User, UserRole
    
    user = User()
    user.id = 1
    user.nombre = "Test User"
    user.email = "test@example.com"
    user.rol = UserRole.PRESIDENTE
    user.activo = True
    return user

@pytest.fixture
def mock_voluntario():
    """Create a mock voluntario user for testing."""
    from src.models.user import User, UserRole
    
    user = User()
    user.id = 2
    user.nombre = "Test Voluntario"
    user.email = "voluntario@example.com"
    user.rol = UserRole.VOLUNTARIO
    user.activo = True
    return user

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return Mock()

@pytest.fixture
def mock_graphql_context(mock_user, mock_db_session):
    """Create a mock GraphQL context."""
    from src.gql.context import GraphQLContext
    return GraphQLContext(user=mock_user, db=mock_db_session)