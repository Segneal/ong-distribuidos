"""
Event model for the reports service.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Association table for many-to-many relationship between events and users
participantes_evento = Table(
    'participantes_evento',
    Base.metadata,
    Column('evento_id', Integer, ForeignKey('eventos.id'), primary_key=True),
    Column('usuario_id', Integer, ForeignKey('usuarios.id'), primary_key=True),
    Column('fecha_adhesion', DateTime)
)

class Event(Base):
    __tablename__ = 'eventos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    fecha_evento = Column(DateTime, nullable=False)
    fecha_creacion = Column(DateTime)
    fecha_actualizacion = Column(DateTime)
    
    # Relationships
    participantes = relationship("User", secondary=participantes_evento, backref="eventos_participados")
    donaciones_repartidas = relationship("DonacionRepartida", back_populates="evento")
    
    def __repr__(self):
        return f"<Event(id={self.id}, nombre='{self.nombre}', fecha_evento='{self.fecha_evento}')>"
    
    @property
    def tiene_donaciones_repartidas(self):
        """Check if event has distributed donations"""
        return len(self.donaciones_repartidas) > 0

class DonacionRepartida(Base):
    __tablename__ = 'donaciones_repartidas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey('eventos.id'))
    donacion_id = Column(Integer, ForeignKey('donaciones.id'))
    cantidad_repartida = Column(Integer, nullable=False)
    usuario_registro = Column(Integer, ForeignKey('usuarios.id'))
    fecha_registro = Column(DateTime)
    
    # Relationships
    evento = relationship("Event", back_populates="donaciones_repartidas")
    donacion = relationship("Donation")
    usuario_registrador = relationship("User")
    
    def __repr__(self):
        return f"<DonacionRepartida(id={self.id}, evento_id={self.evento_id}, donacion_id={self.donacion_id}, cantidad={self.cantidad_repartida})>"