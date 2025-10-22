"""
Database utility functions for the reports service.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models import get_db, test_connection, init_database
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

def get_database_session() -> Optional[Session]:
    """
    Get a database session for manual operations.
    Remember to close the session when done.
    """
    try:
        db_generator = get_db()
        return next(db_generator)
    except SQLAlchemyError as e:
        logger.error(f"Failed to get database session: {e}")
        return None


@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Automatically handles session cleanup.
    """
    db_generator = get_db()
    session = next(db_generator)
    try:
        yield session
    finally:
        session.close()

def check_database_health() -> dict:
    """
    Check database health and return status information.
    """
    health_status = {
        "database_connected": False,
        "tables_exist": False,
        "error": None
    }
    
    try:
        # Test basic connection
        if test_connection():
            health_status["database_connected"] = True
            
            # Check if tables exist by trying to query usuarios table
            db = get_database_session()
            if db:
                try:
                    from ..models import User
                    db.query(User).first()
                    health_status["tables_exist"] = True
                except SQLAlchemyError as e:
                    logger.warning(f"Tables may not exist: {e}")
                finally:
                    db.close()
        
    except Exception as e:
        health_status["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_status

def run_migrations():
    """
    Run database migrations to create new tables.
    This is a simple implementation - in production you might want to use Alembic.
    """
    try:
        init_database()
        logger.info("Database migrations completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database migrations failed: {e}")
        return False