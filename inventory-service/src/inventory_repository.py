"""
Inventory Repository for ONG Management System
Handles database operations for donations
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from typing import Optional, List
from datetime import datetime
from models.donation import Donation, DonationCategory
import psycopg2
from psycopg2.extras import RealDictCursor

class InventoryRepository:
    """Repository class for inventory/donations operations"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'ong_management')
        self.user = os.getenv('DB_USER', 'ong_user')
        self.password = os.getenv('DB_PASSWORD', 'ong_pass')
        self.port = os.getenv('DB_PORT', '5432')
    
    def _get_connection(self):
        """Get database connection"""
        try:
            connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                options='-c client_encoding=UTF8'
            )
            connection.autocommit = False
            return connection
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
            
            # Validate quantity is not negative
            print(f"REPOSITORY: 2. Validating quantity...")
            if quantity < 0:
                print(f"REPOSITORY: 3. Quantity validation failed")
                raise ValueError("Quantity cannot be negative")
            
            print(f"REPOSITORY: 4. Getting database connection...")
            conn = self._get_connection()
            if not conn:
                print(f"REPOSITORY: 5. Failed to get database connection")
                return None
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            print(f"REPOSITORY: 6. Building SQL query...")
            query = """
                INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta)
                VALUES (%s, %s, %s, %s)
                RETURNING id, fecha_alta
            """
            params = (category.value, description, quantity, created_by)
            print(f"REPOSITORY: 7. Query: {query}")
            print(f"REPOSITORY: 8. Params: {params}")
            
            print(f"REPOSITORY: 9. Executing query...")
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            
            print(f"REPOSITORY: 10. Database result: {result}")
            print(f"REPOSITORY: 11. Result type: {type(result)}")
            
            if result:
                print(f"REPOSITORY: 12. Creating Donation object...")
                donation = Donation(
                    id=result['id'],
                    categoria=category,
                    descripcion=description,
                    cantidad=quantity,
                    eliminado=False,
                    fecha_alta=result['fecha_alta'],
                    usuario_alta=created_by
                )
                print(f"REPOSITORY: 13. Created donation: {donation}")
                return donation
            else:
                print(f"REPOSITORY: 14. No result")
                return None
            
        except Exception as e:
            print(f"REPOSITORY: 15. EXCEPTION in create_donation: {e}")
            print(f"REPOSITORY: 16. Exception type: {type(e)}")
            import traceback
            print(f"REPOSITORY: 17. Exception traceback: {traceback.format_exc()}")
            if conn:
                conn.rollback()
            return None
        finally:
            try:
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if 'conn' in locals() and conn:
                    conn.close()
            except:
                pass
            print("=== REPOSITORY: create_donation ENDED ===")
    
    def get_donation_by_id(self, donation_id: int, include_deleted: bool = False) -> Optional[Donation]:
        """Get donation by ID"""
        try:
            conn = self._get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT * FROM donaciones WHERE id = %s"
            params = [donation_id]
            
            if not include_deleted:
                query += " AND eliminado = FALSE"
            
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            
            if result:
                return Donation(
                    id=result['id'],
                    categoria=DonationCategory(result['categoria']),
                    descripcion=result['descripcion'],
                    cantidad=result['cantidad'],
                    eliminado=result['eliminado'],
                    fecha_alta=result['fecha_alta'],
                    usuario_alta=result['usuario_alta'],
                    fecha_modificacion=result.get('fecha_modificacion'),
                    usuario_modificacion=result.get('usuario_modificacion')
                )
            return None
            
        except Exception as e:
            print(f"Error getting donation by ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def update_donation(self, donation_id: int, description: str, quantity: int, updated_by: int, category: Optional[DonationCategory] = None) -> Optional[Donation]:
        """Update existing donation"""
        try:
            # Validate quantity is not negative
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            conn = self._get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Build query dynamically based on whether category is provided
            if category is not None:
                query = """
                    UPDATE donaciones 
                    SET categoria = %s, descripcion = %s, cantidad = %s, fecha_modificacion = CURRENT_TIMESTAMP,
                        usuario_modificacion = %s
                    WHERE id = %s AND eliminado = FALSE
                    RETURNING *
                """
                params = (category.value, description, quantity, updated_by, donation_id)
            else:
                query = """
                    UPDATE donaciones 
                    SET descripcion = %s, cantidad = %s, fecha_modificacion = CURRENT_TIMESTAMP,
                        usuario_modificacion = %s
                    WHERE id = %s AND eliminado = FALSE
                    RETURNING *
                """
                params = (description, quantity, updated_by, donation_id)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                return Donation(
                    id=result['id'],
                    categoria=DonationCategory(result['categoria']),
                    descripcion=result['descripcion'],
                    cantidad=result['cantidad'],
                    eliminado=result['eliminado'],
                    fecha_alta=result['fecha_alta'],
                    usuario_alta=result['usuario_alta'],
                    fecha_modificacion=result['fecha_modificacion'],
                    usuario_modificacion=result['usuario_modificacion']
                )
            return None
            
        except Exception as e:
            print(f"Error updating donation: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def delete_donation(self, donation_id: int, deleted_by: int) -> bool:
        """Soft delete donation (logical delete)"""
        try:
            conn = self._get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            query = """
                UPDATE donaciones 
                SET eliminado = TRUE, fecha_modificacion = CURRENT_TIMESTAMP,
                    usuario_modificacion = %s
                WHERE id = %s AND eliminado = FALSE
            """
            params = (deleted_by, donation_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error deleting donation: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def list_donations(self, category: Optional[DonationCategory] = None, include_deleted: bool = False) -> List[Donation]:
        """List donations with optional filters"""
        try:
            conn = self._get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT * FROM donaciones WHERE 1=1"
            params = []
            
            if category:
                query += " AND categoria = %s"
                params.append(category.value)
            
            if not include_deleted:
                query += " AND eliminado = FALSE"
            
            query += " ORDER BY categoria, descripcion"
            
            cursor.execute(query, tuple(params) if params else None)
            result = cursor.fetchall()
            
            donations = []
            if result:
                for row in result:
                    donation = Donation(
                        id=row['id'],
                        categoria=DonationCategory(row['categoria']),
                        descripcion=row['descripcion'],
                        cantidad=row['cantidad'],
                        eliminado=row['eliminado'],
                        fecha_alta=row['fecha_alta'],
                        usuario_alta=row['usuario_alta'],
                        fecha_modificacion=row.get('fecha_modificacion'),
                        usuario_modificacion=row.get('usuario_modificacion')
                    )
                    donations.append(donation)
            
            return donations
            
        except Exception as e:
            print(f"Error listing donations: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def transfer_donations(self, transfers: List[dict], target_organization: str, transferred_by: int) -> List[str]:
        """Transfer donations to another organization"""
        try:
            conn = self._get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            transfer_ids = []
            
            for transfer in transfers:
                donation_id = transfer['donation_id']
                quantity = transfer['quantity']
                
                # First, check if donation exists and has enough quantity
                donation = self.get_donation_by_id(donation_id)
                if not donation or donation.cantidad < quantity:
                    continue
                
                # Reduce quantity from current donation
                new_quantity = donation.cantidad - quantity
                update_query = """
                    UPDATE donaciones 
                    SET cantidad = %s, fecha_modificacion = CURRENT_TIMESTAMP,
                        usuario_modificacion = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (new_quantity, transferred_by, donation_id))
                
                # Generate transfer ID
                transfer_id = f"TRANS_{donation_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                transfer_ids.append(transfer_id)
            
            conn.commit()
            return transfer_ids
            
        except Exception as e:
            print(f"Error transferring donations: {e}")
            if conn:
                conn.rollback()
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()