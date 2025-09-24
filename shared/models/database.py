"""
Database connection utilities for ONG Management System
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
import logging

class DatabaseConnection:
    """Singleton database connection manager"""
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            # Usar variables de entorno individuales si están disponibles
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'ong_management')
            db_user = os.getenv('DB_USER', 'ong_user')
            db_password = os.getenv('DB_PASSWORD', 'ong_pass')
            
            database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            
            self._connection = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
            self._connection.autocommit = False
            print(f"Database connection established successfully")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        if self._connection is None or self._connection.closed:
            self.connect()
        return self._connection
    
    def close(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

def get_db_connection():
    """Get database connection instance"""
    return DatabaseConnection().get_connection()

def execute_insert_returning(query: str, params: tuple = None):
    """
    Execute an INSERT query with RETURNING clause
    
    Args:
        query: SQL INSERT query string with RETURNING
        params: Query parameters
    
    Returns:
        Query results from RETURNING clause
    """
    print("=== DATABASE: execute_insert_returning STARTED ===")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print(f"DATABASE: 1. Executing INSERT with RETURNING")
        print(f"DATABASE: 2. Query: {query}")
        print(f"DATABASE: 3. Params: {params}")
        print(f"DATABASE: 4. Cursor type: {type(cursor)}")
        
        print(f"DATABASE: 5. Executing query...")
        cursor.execute(query, params)
        
        print(f"DATABASE: 6. Fetching results...")
        result = cursor.fetchall()
        
        print(f"DATABASE: 7. Committing transaction...")
        conn.commit()
        
        print(f"DATABASE: 8. INSERT RETURNING result: {result}")
        print(f"DATABASE: 9. Result type: {type(result)}")
        print(f"DATABASE: 10. Result length: {len(result) if result else 'None'}")
        
        if result and len(result) > 0:
            print(f"DATABASE: 11. First result item: {result[0]}")
            print(f"DATABASE: 12. First result type: {type(result[0])}")
        
        return result
            
    except Exception as e:
        print(f"DATABASE: 13. EXCEPTION in execute_insert_returning: {e}")
        print(f"DATABASE: 14. Exception type: {type(e)}")
        conn.rollback()
        print(f"DATABASE: 15. Transaction rolled back")
        import traceback
        print(f"DATABASE: 16. Exception traceback: {traceback.format_exc()}")
        raise
    finally:
        cursor.close()
        print("=== DATABASE: execute_insert_returning ENDED ===")

def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """
    Execute a database query
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch: Whether to fetch results
    
    Returns:
        Query results if fetch=True, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        
        if fetch:
            if query.strip().upper().startswith('SELECT') or 'RETURNING' in query.upper():
                print(f"About to fetchall for query: {query}")
                result = cursor.fetchall()
                print(f"Query: {query}")
                print(f"Params: {params}")
                print(f"Fetchall result: {result}")
                print(f"Fetchall result type: {type(result)}")
                if 'RETURNING' in query.upper():
                    conn.commit()  # Commit for INSERT/UPDATE with RETURNING
                    print("Committed transaction for RETURNING query")
                return result
            else:
                conn.commit()
                rowcount = cursor.rowcount
                print(f"Non-SELECT query, returning rowcount: {rowcount}")
                return rowcount
        else:
            conn.commit()
            return None
            
    except Exception as e:
        conn.rollback()
        print(f"Database query error: {e}")
        raise
    finally:
        cursor.close()

def execute_transaction(queries: list):
    """
    Execute multiple queries in a transaction
    
    Args:
        queries: List of (query, params) tuples
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for query, params in queries:
            cursor.execute(query, params)
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Transaction error: {e}")
        raise
    finally:
        cursor.close()

def test_connection():
    """
    Test database connection
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False