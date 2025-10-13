"""
Repository para gestionar inventario de donaciones
Versión simplificada para messaging service
"""

import json
from typing import List, Dict, Optional, Any
from messaging.database.connection import get_database_connection


class InventoryRepository:
    def __init__(self):
        pass
    
    def get_donation_by_id(self, donation_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una donación por ID"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT * FROM donaciones WHERE id = %s"
                cursor.execute(query, (donation_id,))
                donation = cursor.fetchone()
                
                return donation
                
        except Exception as e:
            print(f"Error getting donation by ID: {e}")
            return None
    
    def get_donations_by_category(self, categoria: str) -> List[Dict[str, Any]]:
        """Obtiene donaciones por categoría"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT * FROM donaciones WHERE categoria = %s AND cantidad > 0"
                cursor.execute(query, (categoria,))
                donations = cursor.fetchall()
                
                return donations
                
        except Exception as e:
            print(f"Error getting donations by category: {e}")
            return []
    
    def update_donation_quantity(self, donation_id: int, new_quantity: int) -> bool:
        """Actualiza la cantidad de una donación"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                query = "UPDATE donaciones SET cantidad = %s WHERE id = %s"
                cursor.execute(query, (new_quantity, donation_id))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error updating donation quantity: {e}")
            return False
    
    def validate_donation_availability(self, donations: List[Dict]) -> bool:
        """Valida que las donaciones estén disponibles"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                for donation in donations:
                    if 'id' in donation:
                        query = "SELECT cantidad FROM donaciones WHERE id = %s"
                        cursor.execute(query, (donation['id'],))
                        result = cursor.fetchone()
                        
                        if not result or result['cantidad'] < donation.get('cantidad_solicitada', 1):
                            return False
                
                return True
                
        except Exception as e:
            print(f"Error validating donation availability: {e}")
            return False  
    
    def get_all_donations(self, organization: str = None) -> List[Dict[str, Any]]:
        """Obtiene todas las donaciones, opcionalmente filtradas por organización"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                if organization:
                    query = "SELECT * FROM donaciones WHERE organizacion = %s"
                    cursor.execute(query, (organization,))
                else:
                    query = "SELECT * FROM donaciones"
                    cursor.execute(query)
                
                donations = cursor.fetchall()
                return donations
                
        except Exception as e:
            print(f"Error getting all donations: {e}")
            return []