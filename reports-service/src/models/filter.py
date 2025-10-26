"""
Filter models for saved filters and Excel files.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum
import uuid
from datetime import datetime, timedelta

class FilterType(enum.Enum):
    DONACIONES = "DONACIONES"
    EVENTOS = "EVENTOS"

class SavedFilter(Base):
    __tablename__ = 'filtros_guardados'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    nombre = Column(String(255), nullable=False)
    tipo = Column(Enum(FilterType), nullable=False)
    configuracion = Column(JSON, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usuario = relationship("User")
    
    def __repr__(self):
        return f"<SavedFilter(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo.value}', usuario_id={self.usuario_id})>"

class ExcelFile(Base):
    __tablename__ = 'archivos_excel'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime, nullable=False)
    
    # Relationships
    usuario = relationship("User")
    
    def __repr__(self):
        return f"<ExcelFile(id='{self.id}', nombre_archivo='{self.nombre_archivo}', usuario_id={self.usuario_id})>"
    
    @classmethod
    def create_with_expiration(cls, usuario_id: int, nombre_archivo: str, ruta_archivo: str, hours_to_expire: int = 24):
        """Create an Excel file record with automatic expiration"""
        expiration_date = datetime.utcnow() + timedelta(hours=hours_to_expire)
        return cls(
            usuario_id=usuario_id,
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo,
            fecha_expiracion=expiration_date
        )
    
    def is_expired(self):
        """Check if the file has expired"""
        return datetime.utcnow() > self.fecha_expiracion