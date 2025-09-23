"""
Donation model for ONG Management System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from .database import execute_query, execute_transaction

class DonationCategory(Enum):
    ROPA = "ROPA"
    ALIMENTOS = "ALIMENTOS"
    JUGUETES = "JUGUETES"
    UTILES_ESCOLARES = "UTILES_ESCOLARES"

class Donation:
    """Donation model class"""
    
    def __init__(self, id: Optional[int] = None, categoria: DonationCategory = DonationCategory.ALIMENTOS,
                 descripcion: Optional[str] = None, cantidad: int = 0, eliminado: bool = False,
                 fecha_alta: Optional[datetime] = None, usuario_alta: Optional[int] = None,
                 fecha_modificacion: Optional[datetime] = None, usuario_modificacion: Optional[int] = None):
        self.id = id
        self.categoria = categoria if isinstance(categoria, DonationCategory) else DonationCategory(categoria)
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.eliminado = eliminado
        self.fecha_alta = fecha_alta
        self.usuario_alta = usuario_alta
        self.fecha_modificacion = fecha_modificacion
        self.usuario_modificacion = usuario_modificacion
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Donation':
        """Create Donation instance from dictionary"""
        return cls(
            id=data.get('id'),
            categoria=data.get('categoria', DonationCategory.ALIMENTOS),
            descripcion=data.get('descripcion'),
            cantidad=data.get('cantidad', 0),
            eliminado=data.get('eliminado', False),
            fecha_alta=data.get('fecha_alta'),
            usuario_alta=data.get('usuario_alta'),
            fecha_modificacion=data.get('fecha_modificacion'),
            usuario_modificacion=data.get('usuario_modificacion')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Donation instance to dictionary"""
        return {
            'id': self.id,
            'categoria': self.categoria.value if isinstance(self.categoria, DonationCategory) else self.categoria,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'eliminado': self.eliminado,
            'fecha_alta': self.fecha_alta,
            'usuario_alta': self.usuario_alta,
            'fecha_modificacion': self.fecha_modificacion,
            'usuario_modificacion': self.usuario_modificacion
        }
    
    def save(self, user_id: int) -> 'Donation':
        """Save donation to database"""
        if self.id is None:
            return self._create(user_id)
        else:
            return self._update(user_id)
    
    def _create(self, user_id: int) -> 'Donation':
        """Create new donation in database"""
        query = """
            INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta)
            VALUES (%s, %s, %s, %s)
            RETURNING id, fecha_alta
        """
        params = (self.categoria.value, self.descripcion, self.cantidad, user_id)
        
        result = execute_query(query, params)
        if result:
            self.id = result[0]['id']
            self.fecha_alta = result[0]['fecha_alta']
            self.usuario_alta = user_id
        
        return self
    
    def _update(self, user_id: int) -> 'Donation':
        """Update existing donation in database"""
        query = """
            UPDATE donaciones 
            SET descripcion = %s, cantidad = %s, fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s AND eliminado = FALSE
            RETURNING fecha_modificacion
        """
        params = (self.descripcion, self.cantidad, user_id, self.id)
        
        result = execute_query(query, params)
        if result:
            self.fecha_modificacion = result[0]['fecha_modificacion']
            self.usuario_modificacion = user_id
        
        return self
    
    def delete(self, user_id: int) -> bool:
        """Soft delete donation (set eliminado = True)"""
        if self.id is None:
            return False
        
        query = """
            UPDATE donaciones 
            SET eliminado = TRUE, fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
        """
        execute_query(query, (user_id, self.id), fetch=False)
        
        self.eliminado = True
        self.fecha_modificacion = datetime.now()
        self.usuario_modificacion = user_id
        
        return True
    
    def reduce_quantity(self, amount: int, user_id: int) -> bool:
        """Reduce donation quantity (for distributions)"""
        if self.cantidad < amount:
            return False
        
        self.cantidad -= amount
        return self._update(user_id) is not None
    
    @classmethod
    def get_by_id(cls, donation_id: int, include_deleted: bool = False) -> Optional['Donation']:
        """Get donation by ID"""
        query = "SELECT * FROM donaciones WHERE id = %s"
        params = [donation_id]
        
        if not include_deleted:
            query += " AND eliminado = FALSE"
        
        result = execute_query(query, tuple(params))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_all(cls, include_deleted: bool = False) -> List['Donation']:
        """Get all donations"""
        query = "SELECT * FROM donaciones"
        params = None
        
        if not include_deleted:
            query += " WHERE eliminado = FALSE"
        
        query += " ORDER BY categoria, descripcion"
        
        result = execute_query(query, params)
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    @classmethod
    def get_by_category(cls, category: DonationCategory, include_deleted: bool = False) -> List['Donation']:
        """Get donations by category"""
        query = "SELECT * FROM donaciones WHERE categoria = %s"
        params = [category.value]
        
        if not include_deleted:
            query += " AND eliminado = FALSE"
        
        query += " ORDER BY descripcion"
        
        result = execute_query(query, tuple(params))
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    @classmethod
    def get_available_inventory(cls) -> List['Donation']:
        """Get donations with quantity > 0 and not deleted"""
        query = """
            SELECT * FROM donaciones 
            WHERE eliminado = FALSE AND cantidad > 0
            ORDER BY categoria, descripcion
        """
        
        result = execute_query(query)
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    @classmethod
    def get_inventory_summary(cls) -> Dict[str, int]:
        """Get inventory summary by category"""
        query = """
            SELECT categoria, SUM(cantidad) as total
            FROM donaciones 
            WHERE eliminado = FALSE AND cantidad > 0
            GROUP BY categoria
            ORDER BY categoria
        """
        
        result = execute_query(query)
        summary = {}
        
        if result:
            for row in result:
                summary[row['categoria']] = int(row['total'])
        
        return summary
    
    def __str__(self):
        return f"Donation(id={self.id}, category={self.categoria.value}, description={self.descripcion}, quantity={self.cantidad})"
    
    def __repr__(self):
        return self.__str__()