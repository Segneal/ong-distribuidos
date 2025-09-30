"""
Database connection utilities for messaging service
"""
import mysql.connector
from contextlib import contextmanager
import structlog

from ..config import settings

logger = structlog.get_logger(__name__)


@contextmanager
def get_database_connection():
    """
    Context manager for database connections
    Automatically handles connection cleanup
    """
    conn = None
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
        
        logger.debug("Database connection established")
        yield conn
        
    except mysql.connector.Error as e:
        logger.error(
            "Database connection error",
            error=str(e),
            error_code=e.errno if hasattr(e, 'errno') else None
        )
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error(
            "Unexpected database error",
            error=str(e),
            error_type=type(e).__name__
        )
        if conn:
            conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()
            logger.debug("Database connection closed")


def test_database_connection() -> bool:
    """
    Test database connectivity
    Returns True if connection successful, False otherwise
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False


# Función de compatibilidad para imports existentes
def get_db_connection():
    """Compatibility function for existing imports"""
    return get_database_connection()


def initialize_database_tables():
    """
    Initialize required database tables if they don't exist
    """
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Create donation requests table (MySQL syntax)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS solicitudes_donaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    solicitud_id VARCHAR(100) UNIQUE NOT NULL,
                    donaciones JSON NOT NULL,
                    estado ENUM('ACTIVA', 'DADA_DE_BAJA', 'COMPLETADA') DEFAULT 'ACTIVA',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    usuario_creacion INTEGER,
                    usuario_actualizacion INTEGER,
                    notas TEXT
                )
            """)
            
            # Create indexes (MySQL syntax)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_estado 
                ON solicitudes_donaciones(estado)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_fecha 
                ON solicitudes_donaciones(fecha_creacion)
            """)
            
            # Note: MySQL doesn't have GIN indexes like PostgreSQL
            # JSON indexing in MySQL is different, but basic queries will still work
            
            conn.commit()
            cursor.close()
            logger.info("Database tables initialized successfully")
            
    except Exception as e:
        logger.error("Error initializing database tables", error=str(e))
        raise