"""
Donation model for the reports service.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum

class DonationCategory(enum.Enum):
    ALIMENTOS = "ALIMENTOS"
    ROPA = "ROPA"
    MEDICAMENTOS = "MEDICAMENTOS"
    JUGUETES = "JUGUETES"
    LIBROS = "LIBROS"
    ELECTRODOMESTICOS = "ELECTRODOMESTICOS"
    MUEBLES = "MUEBLES"
    OTROS = "OTROS"
    UTILES_ESCOLARES = "UTILES_ESCOLARES"

class Donation(Base):
    __tablename__ = 'donaciones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    categoria = Column(Enum(DonationCategory), nullable=False)
    descripcion = Column(Text)
    cantidad = Column(Integer, nullable=False)
    eliminado = Column(Boolean, default=False)
    fecha_alta = Column(DateTime)
    usuario_alta = Column(Integer, ForeignKey('usuarios.id'))
    fecha_modificacion = Column(DateTime)
    usuario_modificacion = Column(Integer, ForeignKey('usuarios.id'))
    
    # Relationships
    usuario_creador = relationship("User", foreign_keys=[usuario_alta])
    usuario_modificador = relationship("User", foreign_keys=[usuario_modificacion])
    
    def __repr__(self):
        return f"<Donation(id={self.id}, categoria='{self.categoria.value}', cantidad={self.cantidad}, eliminado={self.eliminado})>"
    
    @property
    def categoria_display(self):
        """Return a human-readable category name"""
        category_names = {
            DonationCategory.ALIMENTOS: "Alimentos",
            DonationCategory.ROPA: "Ropa",
            DonationCategory.MEDICAMENTOS: "Medicamentos",
            DonationCategory.JUGUETES: "Juguetes",
            DonationCategory.LIBROS: "Libros",
            DonationCategory.ELECTRODOMESTICOS: "Electrodomésticos",
            DonationCategory.MUEBLES: "Muebles",
            DonationCategory.OTROS: "Otros",
            DonationCategory.UTILES_ESCOLARES: "Útiles Escolares"
        }
        return category_names.get(self.categoria, self.categoria.value)
    
    def is_active(self):
        """Check if donation is not eliminated"""
        return not self.eliminado
    
    def is_eliminated(self):
        """Check if donation is eliminated"""
        return self.eliminado