"""
Authentication utilities for JWT token validation
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.config import settings
from src.models.database import get_db
from src.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

# Security scheme for JWT
security = HTTPBearer()


class AuthenticationError(Exception):
    """Custom authentication error"""
    pass


class AuthorizationError(Exception):
    """Custom authorization error"""
    pass


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Dict containing token payload
        
    Raises:
        AuthenticationError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise AuthenticationError("Invalid token")


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode token
        payload = decode_jwt_token(credentials.credentials)
        
        # Extract user ID and organization from token
        user_id = payload.get("sub") or payload.get("user_id")
        organization = payload.get("organization", "empuje-comunitario")
        
        if user_id is None:
            raise AuthenticationError("Token missing user ID")
        
        # Get user from database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise AuthenticationError("User not found")
        
        if not user.activo:
            raise AuthenticationError("User account is inactive")
        
        # Set organization from JWT token
        user._organization = organization
        
        return user
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_donation_report_access(current_user: User = Depends(get_current_user_from_token)) -> User:
    """
    Require user to have donation report access (Presidente or Vocal)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if authorized
        
    Raises:
        HTTPException: If user doesn't have required permissions
    """
    if not current_user.can_access_donation_reports():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Presidentes and Vocales can access donation reports."
        )
    return current_user


def require_all_event_report_access(current_user: User = Depends(get_current_user_from_token)) -> User:
    """
    Require user to have access to all event reports (Presidente or Coordinador)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if authorized
        
    Raises:
        HTTPException: If user doesn't have required permissions
    """
    if not current_user.can_access_all_event_reports():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Presidentes and Coordinadores can access all event reports."
        )
    return current_user


def require_soap_consultation_access(current_user: User = Depends(get_current_user_from_token)) -> User:
    """
    Require user to have SOAP consultation access (only Presidente)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if authorized
        
    Raises:
        HTTPException: If user doesn't have required permissions
    """
    if not current_user.can_access_soap_consultation():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Presidentes can access SOAP consultation."
        )
    return current_user


def require_president_role(current_user: User) -> User:
    """
    Require user to have President role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if authorized
        
    Raises:
        HTTPException: If user doesn't have required permissions
    """
    if current_user.rol != UserRole.PRESIDENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Presidentes can access this resource."
        )
    return current_user


# Alias for compatibility
get_current_user = get_current_user_from_token


def validate_event_report_user_access(requested_user_id: int, current_user: User) -> bool:
    """
    Validate if current user can access event reports for the requested user
    
    Args:
        requested_user_id: ID of user whose reports are being requested
        current_user: Current authenticated user
        
    Returns:
        True if access is allowed
        
    Raises:
        HTTPException: If access is denied
    """
    # Presidentes and Coordinadores can access any user's reports
    if current_user.can_access_all_event_reports():
        return True
    
    # Other users can only access their own reports
    if current_user.id == requested_user_id:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied. You can only access your own event reports."
    )


# Context class for GraphQL
class GraphQLContext:
    """GraphQL context containing user and database session"""
    
    def __init__(self, user: Optional[User] = None, db: Optional[Session] = None):
        self.user = user
        self.db = db
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.user is not None
    
    def require_authentication(self) -> User:
        """Require user to be authenticated"""
        if not self.is_authenticated:
            raise AuthenticationError("Authentication required")
        return self.user
    
    def require_donation_access(self) -> User:
        """Require user to have donation report access"""
        user = self.require_authentication()
        if not user.can_access_donation_reports():
            raise AuthorizationError("Access denied. Only Presidentes and Vocales can access donation reports.")
        return user
    
    def require_all_event_access(self) -> User:
        """Require user to have access to all event reports"""
        user = self.require_authentication()
        if not user.can_access_all_event_reports():
            raise AuthorizationError("Access denied. Only Presidentes and Coordinadores can access all event reports.")
        return user
    
    def validate_event_user_access(self, requested_user_id: int) -> User:
        """Validate event report user access"""
        user = self.require_authentication()
        
        # Presidentes and Coordinadores can access any user's reports
        if user.can_access_all_event_reports():
            return user
        
        # Other users can only access their own reports
        if user.id == requested_user_id:
            return user
        
        raise AuthorizationError("Access denied. You can only access your own event reports.")