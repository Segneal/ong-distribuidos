"""
User model for ONG Management System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from .database import execute_query, execute_transaction

class UserRole(Enum):
    PRESIDENTE = "PRESIDENTE"
    VOCAL = "VOCAL"
    COORDINADOR = "COORDINADOR"
    VOLUNTARIO = "VOLUNTARIO"

class User:
    """User model class"""
    
    def __init__(self, id: Optional[int] = None, nombre_usuario: str = "", 
                 nombre: str = "", apellido: str = "", telefono: Optional[str] = None,
                 email: str = "", password_hash: str = "", rol: UserRole = UserRole.VOLUNTARIO,
                 activo: bool = True, fecha_creacion: Optional[datetime] = None,
                 fecha_actualizacion: Optional[datetime] = None):
        self.id = id
        self.nombre_usuario = nombre_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email
        self.password_hash = password_hash
        self.rol = rol if isinstance(rol, UserRole) else UserRole(rol)
        self.activo = activo
        self.fecha_creacion = fecha_creacion
        self.fecha_actualizacion = fecha_actualizacion
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary"""
        return cls(
            id=data.get('id'),
            nombre_usuario=data.get('nombre_usuario', ''),
            nombre=data.get('nombre', ''),
            apellido=data.get('apellido', ''),
            telefono=data.get('telefono'),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            rol=data.get('rol', UserRole.VOLUNTARIO),
            activo=data.get('activo', True),
            fecha_creacion=data.get('fecha_creacion'),
            fecha_actualizacion=data.get('fecha_actualizacion')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User instance to dictionary"""
        return {
            'id': self.id,
            'nombre_usuario': self.nombre_usuario,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'email': self.email,
            'password_hash': self.password_hash,
            'rol': self.rol.value if isinstance(self.rol, UserRole) else self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }
    
    def save(self) -> 'User':
        """Save user to database"""
        if self.id is None:
            return self._create()
        else:
            return self._update()
    
    def _create(self) -> 'User':
        """Create new user in database"""
        query = """
            INSERT INTO usuarios (nombre_usuario, nombre, apellido, telefono, email, password_hash, rol, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, fecha_creacion, fecha_actualizacion
        """
        params = (
            self.nombre_usuario, self.nombre, self.apellido, self.telefono,
            self.email, self.password_hash, self.rol.value, self.activo
        )
        
        result = execute_query(query, params)
        if result:
            self.id = result[0]['id']
            self.fecha_creacion = result[0]['fecha_creacion']
            self.fecha_actualizacion = result[0]['fecha_actualizacion']
        
        return self
    
    def _update(self) -> 'User':
        """Update existing user in database"""
        query = """
            UPDATE usuarios 
            SET nombre_usuario = %s, nombre = %s, apellido = %s, telefono = %s,
                email = %s, rol = %s, activo = %s
            WHERE id = %s
            RETURNING fecha_actualizacion
        """
        params = (
            self.nombre_usuario, self.nombre, self.apellido, self.telefono,
            self.email, self.rol.value, self.activo, self.id
        )
        
        result = execute_query(query, params)
        if result:
            self.fecha_actualizacion = result[0]['fecha_actualizacion']
        
        return self
    
    def delete(self) -> bool:
        """Soft delete user (set activo = False)"""
        if self.id is None:
            return False
        
        self.activo = False
        self._update()
        
        # Remove user from future events
        query = """
            DELETE FROM participantes_evento 
            WHERE usuario_id = %s AND evento_id IN (
                SELECT id FROM eventos WHERE fecha_evento > CURRENT_TIMESTAMP
            )
        """
        execute_query(query, (self.id,), fetch=False)
        
        return True
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """Get user by ID"""
        query = "SELECT * FROM usuarios WHERE id = %s"
        result = execute_query(query, (user_id,))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """Get user by username"""
        query = "SELECT * FROM usuarios WHERE nombre_usuario = %s"
        result = execute_query(query, (username,))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Get user by email"""
        query = "SELECT * FROM usuarios WHERE email = %s"
        result = execute_query(query, (email,))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_by_username_or_email(cls, identifier: str) -> Optional['User']:
        """Get user by username or email"""
        query = "SELECT * FROM usuarios WHERE nombre_usuario = %s OR email = %s"
        result = execute_query(query, (identifier, identifier))
        
        if result:
            return cls.from_dict(dict(result[0]))
        return None
    
    @classmethod
    def get_all(cls, active_only: bool = True) -> List['User']:
        """Get all users"""
        query = "SELECT * FROM usuarios"
        params = None
        
        if active_only:
            query += " WHERE activo = %s"
            params = (True,)
        
        query += " ORDER BY nombre, apellido"
        
        result = execute_query(query, params)
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    @classmethod
    def get_by_role(cls, role: UserRole, active_only: bool = True) -> List['User']:
        """Get users by role"""
        query = "SELECT * FROM usuarios WHERE rol = %s"
        params = [role.value]
        
        if active_only:
            query += " AND activo = %s"
            params.append(True)
        
        query += " ORDER BY nombre, apellido"
        
        result = execute_query(query, tuple(params))
        return [cls.from_dict(dict(row)) for row in result] if result else []
    
    def __str__(self):
        return f"User(id={self.id}, username={self.nombre_usuario}, name={self.nombre} {self.apellido}, role={self.rol.value})"
    
    def __repr__(self):
        return self.__str__()