"""
Final Inventory Repository with correct Spanish field names and organization support
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
    
    def create_donation(self, category: DonationCategory, description: str, quantity: int, created_by: int, organization: str = 'empuje-comunitario') -> Optional[Donation]:
        """Create a new donation"""
        try:
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            conn = self._get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            
            # Convert enum to string for database
            category_str = category.value if isinstance(category, DonationCategory) else str(category)
            
            # Check if organizacion column exists
            cursor.execute("DESCRIBE donaciones")
            columns = [col[0] for col in cursor.fetchall()]
            
            if 'organizacion' in columns:
                query = """
                    INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta)
                    VALUES (%s, %s, %s, %s, %s)
                """
                params = (category_str, description, quantity, organization, created_by)
            else:
                query = """
                    INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta)
                    VALUES (%s, %s, %s, %s)
                """
                params = (category_str, description, quantity, created_by)
            
            cursor.execute(query, params)
            donation_id = cursor.lastrowid
            conn.commit()
            
            # Get the created donation
            cursor.execute("SELECT * FROM donaciones WHERE id = %s", (donation_id,))
            result = cursor.fetchone()
            
            if result:
                donation = Donation(
                    id=result['id'],
                    categoria=DonationCategory(result['categoria']),
                    descripcion=result['descripcion'],
                    cantidad=result['cantidad'],
                    organizacion=result.get('organizacion', organization),
                    eliminado=result['eliminado'],
                    fecha_alta=result['fecha_alta'],
                    usuario_alta=result['usuario_alta']
                )
                
                cursor.close()
                conn.close()
                return donation
            
            cursor.close()
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error creating donation: {e}")
            if conn:
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
            
            # Check if organizacion column exists
            cursor.execute("DESCRIBE donaciones")
            columns = [col[0] for col in cursor.fetchall()]
            has_organization = 'organizacion' in columns
            
            conditions = []
            params = []
            
            if not include_deleted:
                conditions.append("eliminado = FALSE")
            
            if organization and has_organization:
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
                    organizacion=row.get('organizacion', 'empuje-comunitario') if has_organization else 'empuje-comunitario',
                    eliminado=row['eliminado'],
                    fecha_alta=row['fecha_alta'],
                    usuario_alta=row['usuario_alta']
                )
                donations.append(donation)
            
            cursor.close()
            conn.close()
            return donations
            
        except Exception as e:
            print(f"Error getting donations: {e}")
            return []
    
    def list_donations(self, category=None, include_deleted=False, organization=None):
        """List donations with filters - alias for get_all_donations"""
        return self.get_all_donations(include_deleted=include_deleted, organization=organization)
    
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
                    organizacion=result.get('organizacion', 'empuje-comunitario'),
                    eliminado=result['eliminado'],
                    fecha_alta=result['fecha_alta'],
                    usuario_alta=result['usuario_alta'],
                    fecha_modificacion=result.get('fecha_modificacion'),
                    usuario_modificacion=result.get('usuario_modificacion')
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
    
    def update_donation(self, donation_id: int, description: str = None, quantity: int = None, updated_by: int = None) -> Optional[Donation]:
        """Update donation"""
        try:
            conn = self._get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            
            # Build update query dynamically
            updates = []
            params = []
            
            if description is not None:
                updates.append("descripcion = %s")
                params.append(description)
            
            if quantity is not None:
                updates.append("cantidad = %s")
                params.append(quantity)
            
            if updated_by is not None:
                updates.append("usuario_modificacion = %s")
                params.append(updated_by)
            
            updates.append("fecha_modificacion = CURRENT_TIMESTAMP")
            params.append(donation_id)
            
            query = f"UPDATE donaciones SET {', '.join(updates)} WHERE id = %s"
            
            cursor.execute(query, params)
            conn.commit()
            
            # Return updated donation
            updated_donation = self.get_donation_by_id(donation_id)
            
            cursor.close()
            conn.close()
            return updated_donation
            
        except Exception as e:
            print(f"Error updating donation: {e}")
            if conn:
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
            
            query = """
                UPDATE donaciones 
                SET eliminado = TRUE, fecha_modificacion = CURRENT_TIMESTAMP, usuario_modificacion = %s
                WHERE id = %s
            """
            
            cursor.execute(query, (deleted_by, donation_id))
            conn.commit()
            
            success = cursor.rowcount > 0
            
            cursor.close()
            conn.close()
            return success
            
        except Exception as e:
            print(f"Error deleting donation: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False