"""
Database connection utilities for messaging service
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import structlog

from .config import settings

logger = structlog.get_logger(__name__)


@contextmanager
def get_database_connection():
    """
    Context manager for database connections
    Automatically handles connection cleanup
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.db_host,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            port=settings.db_port,
            cursor_factory=RealDictCursor
        )
        
        logger.debug("Database connection established")
        yield conn
        
    except psycopg2.Error as e:
        logger.error(
            "Database connection error",
            error=str(e),
            error_code=e.pgcode if hasattr(e, 'pgcode') else None
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
        if conn:
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


def initialize_database_tables():
    """
    Initialize required database tables if they don't exist
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # Create donation requests table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS solicitudes_donaciones (
                        id SERIAL PRIMARY KEY,
                        solicitud_id VARCHAR(100) UNIQUE NOT NULL,
                        donaciones JSONB NOT NULL,
                        estado VARCHAR(20) DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'DADA_DE_BAJA', 'COMPLETADA')),
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        usuario_creacion INTEGER,
                        usuario_actualizacion INTEGER,
                        notas TEXT
                    )
                """)
                
                # Create indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_estado 
                    ON solicitudes_donaciones(estado)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_fecha 
                    ON solicitudes_donaciones(fecha_creacion)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_gin 
                    ON solicitudes_donaciones USING gin(donaciones)
                """)
                
                conn.commit()
                logger.info("Database tables initialized successfully")
                
    except Exception as e:
        logger.error("Error initializing database tables", error=str(e))
        raise