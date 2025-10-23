"""
Transfer model for donation transfers between organizations.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class TransferType(enum.Enum):
    ENVIADA = "ENVIADA"
    RECIBIDA = "RECIBIDA"

class TransferStatus(enum.Enum):
    PENDIENTE = "PENDIENTE"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"

class DonationTransfer(Base):
    __tablename__ = 'transferencias_donaciones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(Enum(TransferType), nullable=False)
    organizacion_contraparte = Column(String(100), nullable=False)
    organizacion_propietaria = Column(String(100), nullable=False)
    solicitud_id = Column(String(100))
    donaciones = Column(JSON, nullable=False)
    estado = Column(Enum(TransferStatus), default=TransferStatus.COMPLETADA)
    fecha_transferencia = Column(DateTime, default=datetime.utcnow)
    usuario_registro = Column(Integer, ForeignKey('usuarios.id'))
    notas = Column(Text)
    
    # Relationships
    usuario = relationship("User", foreign_keys=[usuario_registro])
    
    def __repr__(self):
        return f"<DonationTransfer(id={self.id}, tipo='{self.tipo.value}', organizacion='{self.organizacion_contraparte}', estado='{self.estado.value}')>"
    
    @property
    def is_sent(self):
        """Check if transfer is sent"""
        return self.tipo == TransferType.ENVIADA
    
    @property
    def is_received(self):
        """Check if transfer is received"""
        return self.tipo == TransferType.RECIBIDA
    
    @property
    def is_completed(self):
        """Check if transfer is completed"""
        return self.estado == TransferStatus.COMPLETADA
    
    def get_donation_items(self):
        """Parse donation items from JSON"""
        if isinstance(self.donaciones, list):
            return self.donaciones
        return []
    
    def get_total_items(self):
        """Get total number of donation items (count of different items)"""
        items = self.get_donation_items()
        return len(items)
    
    def get_total_quantity(self):
        """Get total quantity of all items"""
        items = self.get_donation_items()
        total = 0
        
        for item in items:
            try:
                # Handle both formats: 'cantidad'/'quantity'
                quantity_str = str(item.get('cantidad') or item.get('quantity', '0'))
                
                # Extract numbers from string
                import re
                numbers = re.findall(r'\d+', quantity_str)
                if numbers:
                    total += int(numbers[0])
            except:
                pass
        
        return total
    
    def get_categories_summary(self):
        """Get summary of categories in this transfer"""
        items = self.get_donation_items()
        categories = {}
        
        for item in items:
            categoria = item.get('categoria', 'N/A')
            if categoria not in categories:
                categories[categoria] = 0
            categories[categoria] += 1
        
        return categories