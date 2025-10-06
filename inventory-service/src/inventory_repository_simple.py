#!/usr/bin/env python3
"""
Repository simplificado que funciona correctamente
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from typing import Optional, List
from datetime import datetime
from models.donation import Donation, DonationCategory
from database_mysql import get_db_connection

class InventoryRepository:
    """Repository simplificado para inventario"""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def create_donation(self, category: DonationCategory, description: str, quantity: int, created_by: int, organization: str = 'empuje-comunitario') -> Optional[Donation]:
        """Create a new donation - versión simplificada"""
        try:
            print(f"REPO: Creando donación - {category.value}, {description}, {quantity}, {organization}")
            
            conn = self.db.connect()
            cursor = conn.cursor(dictionary=True)
            
            # Insert simple
            query = """
                INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (category.value, description, quantity, organization, created_by)
            
            print(f"REPO: Ejecutando query: {query}")
            print(f"REPO: Parámetros: {params}")
            
            cursor.execute(query, params)
            donation_id = cursor.lastrowid
            conn.commit()
            
            print(f"REPO: Donación creada con ID: {donation_id}")
            
            # Crear objeto de respuesta con nombres en español
            donation = Donation(
                id=donation_id,
                categoria=category.value,  # Pasar el string del enum, no el enum
                descripcion=description,
                cantidad=quantity,
                organizacion=organization,
                usuario_alta=created_by,
                fecha_alta=datetime.now()
            )
            
            cursor.close()
            conn.close()
            
            print(f"REPO: Donación creada exitosamente: {donation}")
            return donation
            
        except Exception as e:
            print(f"REPO: Error detallado: {e}")
            print(f"REPO: Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_donations(self, include_deleted=False, organization=None):
        """Get all donations"""
        try:
            print(f"REPO: get_all_donations called with organization: {organization}")
            print(f"REPO: include_deleted: {include_deleted}")
            
            conn = self.db.connect()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM donaciones WHERE eliminado = FALSE"
            params = []
            
            if organization:
                query += " AND organizacion = %s"
                params.append(organization)
                print(f"REPO: Added organization filter: {organization}")
            else:
                print(f"REPO: NO organization filter applied")
            
            query += " ORDER BY fecha_alta DESC"
            
            print(f"REPO: Final query: {query}")
            print(f"REPO: Query params: {params}")
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            donations = []
            for row in results:
                donation = Donation(
                    id=row['id'],
                    categoria=DonationCategory(row['categoria']),  # DB en español -> modelo en español
                    descripcion=row['descripcion'],
                    cantidad=row['cantidad'],
                    organizacion=row.get('organizacion', 'empuje-comunitario'),
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
        """Alias for get_all_donations"""
        print(f"REPO: list_donations called with:")
        print(f"  - category: {category}")
        print(f"  - include_deleted: {include_deleted}")
        print(f"  - organization: {organization}")
        return self.get_all_donations(include_deleted=include_deleted, organization=organization)
    
    def update_donation(self, donation_id: int, description: str = None, quantity: int = None, updated_by: int = None, category = None):
        """Update donation"""
        try:
            print(f"REPO: update_donation called with ID: {donation_id}")
            print(f"  - description: {description}")
            print(f"  - quantity: {quantity}")
            print(f"  - updated_by: {updated_by}")
            print(f"  - category: {category}")
            
            conn = self.db.connect()
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
            
            # Categoría no se puede modificar por seguridad
            if category is not None:
                print(f"REPO: Category update ignored for security: {category}")
                # No agregar categoría a los updates
            
            if updated_by is not None:
                updates.append("usuario_modificacion = %s")
                params.append(updated_by)
            
            updates.append("fecha_modificacion = CURRENT_TIMESTAMP")
            params.append(donation_id)
            
            query = f"UPDATE donaciones SET {', '.join(updates)} WHERE id = %s"
            
            print(f"REPO: Executing update query: {query}")
            print(f"REPO: Update params: {params}")
            
            cursor.execute(query, params)
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"REPO: Updated {cursor.rowcount} donation(s)")
                
                # Get updated donation
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
                    print(f"REPO: Update successful: {donation}")
                    return donation
            
            cursor.close()
            conn.close()
            print(f"REPO: No donation found with ID: {donation_id}")
            return None
            
        except Exception as e:
            print(f"REPO: Error updating donation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_donation_by_id(self, donation_id: int):
        """Get donation by ID"""
        try:
            print(f"REPO: get_donation_by_id called with ID: {donation_id}")
            
            conn = self.db.connect()
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
                print(f"REPO: Found donation: {donation}")
                return donation
            
            cursor.close()
            conn.close()
            print(f"REPO: No donation found with ID: {donation_id}")
            return None
            
        except Exception as e:
            print(f"REPO: Error getting donation by ID: {e}")
            import traceback
            traceback.print_exc()
            return None