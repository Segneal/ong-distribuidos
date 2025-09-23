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
            database_url = os.getenv('DATABASE_URL', 'postgresql://ong_user:ong_pass@localhost:5432/ong_management')
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
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
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