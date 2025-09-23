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
from database_fixed import get_db_connection

class InventoryRepository:
    """Repository class for inventory/donations operations"""
    
    def create_donation(self, category: DonationCategory, description: str, quantity: int, created_by: int) -> Optional[Donation]:
        """Create a new donation"""
        try:
            # Validate quantity is not negative
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            query = """
                INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta)
                VALUES (%s, %s, %s, %s)
                RETURNING id, fecha_alta
            """
            params = (category.value, description, quantity, created_by)
            
            result = execute_query(query, params)
            if result:
                donation = Donation(
                    id=result[0]['id'],
                    categoria=category,
                    descripcion=description,
                    cantidad=quantity,
                    eliminado=False,
                    fecha_alta=result[0]['fecha_alta'],
                    usuario_alta=created_by
                )
                return donation
            return None
            
        except Exception as e:
            print(f"Error creating donation: {e}")
            return None
    
    def get_donation_by_id(self, donation_id: int, include_deleted: bool = False) -> Optional[Donation]:
        """Get donation by ID"""
        try:
            query = "SELECT * FROM donaciones WHERE id = %s"
            params = [donation_id]
            
            if not include_deleted:
                query += " AND eliminado = FALSE"
            
            result = execute_query(query, tuple(params))
            
            if result:
                row = dict(result[0])
                return Donation(
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
            return None
            
        except Exception as e:
            print(f"Error getting donation by ID: {e}")
            return None
    
    def update_donation(self, donation_id: int, description: str, quantity: int, updated_by: int) -> Optional[Donation]:
        """Update existing donation"""
        try:
            # Validate quantity is not negative
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            query = """
                UPDATE donaciones 
                SET descripcion = %s, cantidad = %s, fecha_modificacion = CURRENT_TIMESTAMP,
                    usuario_modificacion = %s
                WHERE id = %s AND eliminado = FALSE
                RETURNING *
            """
            params = (description, quantity, updated_by, donation_id)
            
            result = execute_query(query, params)
            if result:
                row = dict(result[0])
                return Donation(
                    id=row['id'],
                    categoria=DonationCategory(row['categoria']),
                    descripcion=row['descripcion'],
                    cantidad=row['cantidad'],
                    eliminado=row['eliminado'],
                    fecha_alta=row['fecha_alta'],
                    usuario_alta=row['usuario_alta'],
                    fecha_modificacion=row['fecha_modificacion'],
                    usuario_modificacion=row['usuario_modificacion']
                )
            return None
            
        except Exception as e:
            print(f"Error updating donation: {e}")
            return None
    
    def delete_donation(self, donation_id: int, deleted_by: int) -> bool:
        """Soft delete donation (logical delete)"""
        try:
            query = """
                UPDATE donaciones 
                SET eliminado = TRUE, fecha_modificacion = CURRENT_TIMESTAMP,
                    usuario_modificacion = %s
                WHERE id = %s AND eliminado = FALSE
            """
            params = (deleted_by, donation_id)
            
            result = execute_query(query, params, fetch=False)
            return result is not None
            
        except Exception as e:
            print(f"Error deleting donation: {e}")
            return False
    
    def list_donations(self, category: Optional[DonationCategory] = None, include_deleted: bool = False) -> List[Donation]:
        """List donations with optional filters"""
        try:
            query = "SELECT * FROM donaciones WHERE 1=1"
            params = []
            
            if category:
                query += " AND categoria = %s"
                params.append(category.value)
            
            if not include_deleted:
                query += " AND eliminado = FALSE"
            
            query += " ORDER BY categoria, descripcion"
            
            result = execute_query(query, tuple(params) if params else None)
            
            donations = []
            if result:
                for row in result:
                    row_dict = dict(row)
                    donation = Donation(
                        id=row_dict['id'],
                        categoria=DonationCategory(row_dict['categoria']),
                        descripcion=row_dict['descripcion'],
                        cantidad=row_dict['cantidad'],
                        eliminado=row_dict['eliminado'],
                        fecha_alta=row_dict['fecha_alta'],
                        usuario_alta=row_dict['usuario_alta'],
                        fecha_modificacion=row_dict.get('fecha_modificacion'),
                        usuario_modificacion=row_dict.get('usuario_modificacion')
                    )
                    donations.append(donation)
            
            return donations
            
        except Exception as e:
            print(f"Error listing donations: {e}")
            return []
    
    def transfer_donations(self, transfers: List[dict], target_organization: str, transferred_by: int) -> List[str]:
        """Transfer donations to another organization"""
        try:
            transfer_ids = []
            queries = []
            
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
                queries.append((update_query, (new_quantity, transferred_by, donation_id)))
                
                # Generate transfer ID
                transfer_id = f"TRANS_{donation_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                transfer_ids.append(transfer_id)
            
            # Execute all updates in a transaction
            if queries:
                execute_transaction(queries)
            
            return transfer_ids
            
        except Exception as e:
            print(f"Error transferring donations: {e}")
            return []