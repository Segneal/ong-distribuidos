"""
Inventory Repository for ONG Management System
Handles database operations for donations - MySQL version
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from typing import Optional, List
from datetime import datetime
from donation_model_fixed import Donation, DonationCategory
from database_mysql import get_db_connection

class InventoryRepository:
    """Repository class for inventory/donations operations"""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def _get_connection(self):
        """Get database connection"""
        try:
            return self.db.connect()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def create_donation(self, category: DonationCategory, description: str, quantity: int, created_by: int, organization: str = 'empuje-comunitario') -> Optional[Donation]:
        """Create a new donation"""
        print("=== REPOSITORY: create_donation STARTED ===")
        try:
            print(f"REPOSITORY: 1. Input parameters:")
            print(f"REPOSITORY:    - category: {category} (type: {type(category)})")
            print(f"REPOSITORY:    - description: '{description}' (type: {type(description)})")
            print(f"REPOSITORY:    - quantity: {quantity} (type: {type(quantity)})")
            print(f"REPOSITORY:    - created_by: {created_by} (type: {type(created_by)})")

            # Validate inputs
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            print(f"REPOSITORY: 4. Getting database connection...")
            conn = self._get_connection()
            if not conn:
                print(f"REPOSITORY: 5. Failed to get database connection")
                return None
            
            cursor = conn.cursor(dictionary=True)
            
            # Convert enum to string for database
            category_str = category.value if hasattr(category, 'value') else str(category)
            print(f"REPOSITORY: 6. Category converted to: '{category_str}'")
            
            # Insert donation
            query = """
                INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta, organizacion, fecha_alta) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            values = (category_str, description, quantity, created_by, organization)
            
            print(f"REPOSITORY: 7. Executing query: {query}")
            print(f"REPOSITORY: 8. With values: {values}")
            
            cursor.execute(query, values)
            donation_id = cursor.lastrowid
            
            conn.commit()
            
            print(f"REPOSITORY: 10. Database result: donation_id = {donation_id}")
            
            # Fetch the created donation
            cursor.execute("""
                SELECT id, categoria, descripcion, cantidad, eliminado, fecha_alta, usuario_alta 
                FROM donaciones WHERE id = %s
            """, (donation_id,))
            
            result = cursor.fetchone()
            print(f"REPOSITORY: 11. Fetched result: {result}")
            
            if result:
                donation = Donation(
                    id=result['id'],
                    categoria=DonationCategory(result['categoria']),
                    descripcion=result['descripcion'],
                    cantidad=result['cantidad'],
                    eliminado=result['eliminado'],
                    fecha_alta=result['fecha_alta'],
                    usuario_alta=result['usuario_alta'],
                    organizacion=result.get('organizacion', 'empuje-comunitario')
                )
                print(f"REPOSITORY: 12. Created donation object: {donation}")
                cursor.close()
                conn.close()
                return donation
            else:
                print(f"REPOSITORY: 13. No result found after insert")
                cursor.close()
                conn.close()
                return None
                
        except Exception as e:
            print(f"REPOSITORY: ERROR in create_donation: {e}")
            print(f"REPOSITORY: ERROR type: {type(e)}")
            import traceback
            print(f"REPOSITORY: ERROR traceback: {traceback.format_exc()}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return None
    
    def get_all_donations(self, include_deleted: bool = False, organization: str = None) -> List[Donation]:
        """Get all donations, optionally filtered by organization"""
        try:
            conn = self._get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor(dictionary=True)
            
            conditions = []
            params = []
            
            if not include_deleted:
                conditions.append("eliminado = FALSE")
            
            if organization:
                conditions.append("organizacion = %s")
                params.append(organization)
            
            if conditions:
                query = f"SELECT * FROM donaciones WHERE {' AND '.join(conditions)} ORDER BY fecha_alta DESC"
            else:
                query = "SELECT * FROM donaciones ORDER BY fecha_alta DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            donations = []
            for row in results:
                donation = Donation(
                    id=row['id'],
                    categoria=DonationCategory(row['categoria']),
                    descripcion=row['descripcion'],
                    cantidad=row['cantidad'],
                    eliminado=row['eliminado'],
                    fecha_alta=row['fecha_alta'],
                    usuario_alta=row['usuario_alta'],
                    organizacion=row.get('organizacion', 'empuje-comunitario')
                )
                donations.append(donation)
            
            cursor.close()
            conn.close()
            return donations
            
        except Exception as e:
            print(f"Error getting donations: {e}")
            return []
    
    def get_donation_by_id(self, donation_id: int) -> Optional[Donation]:
        """Get donation by ID"""
        try:
            conn = self._get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM donaciones WHERE id = %s", (donation_id,))
            result = cursor.fetchone()
            
            if result:
                donation = Donation(
                    id=result['id'],
                    categoria=DonationCategory(result['categoria']),
                    descripcion=result['descripcion'],
                    cantidad=result['cantidad'],
                    eliminado=result['eliminado'],
                    fecha_alta=result['fecha_alta'],
                    usuario_alta=result['usuario_alta'],
                    organizacion=result.get('organizacion', 'empuje-comunitario')
                )
                cursor.close()
                conn.close()
                return donation
            
            cursor.close()
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error getting donation by ID: {e}")
            return None
    
    def update_donation(self, donation_id: int, category: DonationCategory = None, 
                       description: str = None, quantity: int = None, 
                       updated_by: int = None) -> Optional[Donation]:
        """Update donation"""
        try:
            conn = self._get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            
            # Build dynamic update query
            updates = []
            values = []
            
            if category is not None:
                updates.append("categoria = %s")
                values.append(category.value if hasattr(category, 'value') else str(category))
            
            if description is not None:
                updates.append("descripcion = %s")
                values.append(description)
            
            if quantity is not None:
                if quantity < 0:
                    raise ValueError("Quantity cannot be negative")
                updates.append("cantidad = %s")
                values.append(quantity)
            
            if updated_by is not None:
                updates.append("usuario_modificacion = %s")
                values.append(updated_by)
            
            updates.append("fecha_modificacion = NOW()")
            values.append(donation_id)
            
            if not updates:
                cursor.close()
                conn.close()
                return self.get_donation_by_id(donation_id)
            
            query = f"UPDATE donaciones SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, values)
            conn.commit()
            
            cursor.close()
            conn.close()
            return self.get_donation_by_id(donation_id)
            
        except Exception as e:
            print(f"Error updating donation: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return None
    
    def delete_donation(self, donation_id: int, deleted_by: int) -> bool:
        """Soft delete donation"""
        try:
            conn = self._get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE donaciones 
                SET eliminado = TRUE, usuario_modificacion = %s, fecha_modificacion = NOW()
                WHERE id = %s
            """, (deleted_by, donation_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()
            return success
            
        except Exception as e:
            print(f"Error deleting donation: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    

    
    def transfer_donations(self, transfers, target_organization, transferred_by):
        """Transfer donations to another organization"""
        try:
            conn = self._get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            transfer_ids = []
            
            for transfer in transfers:
                # Here you would implement the transfer logic
                # For now, just return empty list
                pass
            
            cursor.close()
            conn.close()
            return transfer_ids
            
        except Exception as e:
            print(f"Error transferring donations: {e}")
            return []    

    def list_donations(self, category=None, include_deleted=False, organization=None):
        """List donations with filters - alias for get_all_donations"""
        return self.get_all_donations(include_deleted=include_deleted, organization=organization)