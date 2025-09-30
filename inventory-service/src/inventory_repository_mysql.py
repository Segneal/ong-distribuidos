"""
Inventory Repository for ONG Management System
Handles database operations for donations - MySQL version
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from typing import Optional, List
from datetime import datetime
from models.donation import Donation, DonationCategory
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
    
    def create_donation(self, category: DonationCategory, description: str, quantity: int, created_by: int) -> Optional[Donation]:
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
                INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta, fecha_alta) 
                VALUES (%s, %s, %s, %s, NOW())
            """
            values = (category_str, description, quantity, created_by)
            
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
                    category=DonationCategory(result['categoria']),
                    description=result['descripcion'],
                    quantity=result['cantidad'],
                    deleted=result['eliminado'],
                    created_at=result['fecha_alta'],
                    created_by=result['usuario_alta']
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
    
    def get_all_donations(self, include_deleted: bool = False) -> List[Donation]:
        """Get all donations"""
        try:
            conn = self._get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor(dictionary=True)
            
            if include_deleted:
                query = "SELECT * FROM donaciones ORDER BY fecha_alta DESC"
            else:
                query = "SELECT * FROM donaciones WHERE eliminado = FALSE ORDER BY fecha_alta DESC"
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            donations = []
            for row in results:
                donation = Donation(
                    id=row['id'],
                    category=DonationCategory(row['categoria']),
                    description=row['descripcion'],
                    quantity=row['cantidad'],
                    deleted=row['eliminado'],
                    created_at=row['fecha_alta'],
                    created_by=row['usuario_alta']
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
                    category=DonationCategory(result['categoria']),
                    description=result['descripcion'],
                    quantity=result['cantidad'],
                    deleted=result['eliminado'],
                    created_at=result['fecha_alta'],
                    created_by=result['usuario_alta']
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
    
    def list_donations(self, category=None, include_deleted=False):
        """List donations with optional filters"""
        try:
            conn = self._get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor(dictionary=True)
            
            # Build query based on filters
            query = "SELECT * FROM donaciones"
            conditions = []
            values = []
            
            if not include_deleted:
                conditions.append("eliminado = FALSE")
            
            if category is not None:
                conditions.append("categoria = %s")
                values.append(category.value if hasattr(category, 'value') else str(category))
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY fecha_alta DESC"
            
            cursor.execute(query, values)
            results = cursor.fetchall()
            
            donations = []
            for row in results:
                donation = Donation(
                    id=row['id'],
                    category=DonationCategory(row['categoria']),
                    description=row['descripcion'],
                    quantity=row['cantidad'],
                    deleted=row['eliminado'],
                    created_at=row['fecha_alta'],
                    created_by=row['usuario_alta']
                )
                donations.append(donation)
            
            cursor.close()
            conn.close()
            return donations
            
        except Exception as e:
            print(f"Error listing donations: {e}")
            return []
    
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