"""
User model for the reports service.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserRole(enum.Enum):
    PRESIDENTE = "PRESIDENTE"
    VOCAL = "VOCAL"
    COORDINADOR = "COORDINADOR"
    VOLUNTARIO = "VOLUNTARIO"

class User(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(UserRole), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime)
    fecha_actualizacion = Column(DateTime)
    
    # Organization field - will be populated from JWT token
    @property
    def organization(self):
        """Get organization from context or default"""
        return getattr(self, '_organization', 'empuje-comunitario')
    
    # Relationships will be defined after all models are loaded
    
    def __repr__(self):
        return f"<User(id={self.id}, nombre_usuario='{self.nombre_usuario}', rol='{self.rol.value}')>"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    def is_presidente(self):
        return self.rol == UserRole.PRESIDENTE
    
    def is_vocal(self):
        return self.rol == UserRole.VOCAL
    
    def is_coordinador(self):
        return self.rol == UserRole.COORDINADOR
    
    def is_voluntario(self):
        return self.rol == UserRole.VOLUNTARIO
    
    def can_access_donation_reports(self):
        """Check if user can access donation reports (Presidentes and Vocales)"""
        return self.rol in [UserRole.PRESIDENTE, UserRole.VOCAL]
    
    def can_access_all_event_reports(self):
        """Check if user can access all users' event reports (Presidentes and Coordinadores)"""
        return self.rol in [UserRole.PRESIDENTE, UserRole.COORDINADOR]
    
    def can_access_soap_consultation(self):
        """Check if user can access SOAP consultation (only Presidentes)"""
        return self.rol == UserRole.PRESIDENTE