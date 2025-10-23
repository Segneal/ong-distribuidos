"""
GraphQL context provider
"""
from typing import Optional
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext
from src.models.database import get_db
from src.models.user import User
from src.utils.auth import get_current_user_from_token, GraphQLContext, AuthenticationError
import logging

logger = logging.getLogger(__name__)


class Context(BaseContext):
    """Custom GraphQL context"""
    
    def __init__(self, user: Optional[User] = None, db: Optional[Session] = None):
        self.user = user
        self.db = db
        self.auth_context = GraphQLContext(user=user, db=db)
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.user is not None


async def get_graphql_context(
    request: Request,
    db: Session = Depends(get_db)
) -> Context:
    """
    Create GraphQL context with optional authentication
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Context object with user and database session
    """
    user = None
    
    # Try to get user from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            from src.utils.auth import decode_jwt_token
            payload = decode_jwt_token(token)
            
            # Extract user ID from token
            user_id = payload.get("sub") or payload.get("user_id")
            if user_id:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user and not user.activo:
                    user = None  # Inactive users are treated as unauthenticated
                    
        except Exception as e:
            logger.warning(f"Failed to authenticate user from token: {e}")
            # Continue without authentication - some queries might be public
    
    return Context(user=user, db=db)