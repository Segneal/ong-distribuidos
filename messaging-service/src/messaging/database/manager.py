"""
Database manager for messaging service operations
"""
import mysql.connector
import structlog

from ..config import settings

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """Database manager for messaging service operations"""
    
    def __init__(self):
        pass
    
    def get_connection(self):
        """Get a database connection"""
        try:
            conn = mysql.connector.connect(
                host=settings.db_host,
                database=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
                port=settings.db_port,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            return conn
        except Exception as e:
            logger.error("Error getting database connection", error=str(e))
            return None