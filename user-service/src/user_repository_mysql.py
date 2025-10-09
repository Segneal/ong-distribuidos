from database_mysql import get_db_connection
from datetime import datetime

class UserRepository:
    def __init__(self):
        self.db = get_db_connection()
    
    def create_user(self, username, first_name, last_name, email, phone, role, password_hash, organization='empuje-comunitario'):
        """Crea un nuevo usuario en la base de datos"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            # Insert user (MySQL no soporta RETURNING)
            query = """
                INSERT INTO usuarios (nombre_usuario, nombre, apellido, email, telefono, password_hash, rol, organizacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (username, first_name, last_name, email, phone, password_hash, role, organization))
            user_id = cursor.lastrowid
            conn.commit()
            
            # Fetch the created user
            select_query = """
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, organizacion, activo, fecha_creacion, fecha_actualizacion
                FROM usuarios WHERE id = %s
            """
            cursor.execute(select_query, (user_id,))
            user = cursor.fetchone()
            
            return dict(user) if user else None
            
        except Exception as e:
            print(f"Error creando usuario: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            cursor.close()
            self.db.close()
    
    def get_user_by_id(self, user_id):
        """Obtiene un usuario por su ID"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            query = """
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, organizacion, activo, fecha_creacion, fecha_actualizacion
                FROM usuarios WHERE id = %s
            """
            
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            
            return dict(user) if user else None
            
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
        finally:
            cursor.close()
            self.db.close()
    
    def get_user_by_username_or_email(self, username_or_email):
        """Obtiene un usuario por nombre de usuario o email"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            query = """
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, organizacion, activo, fecha_creacion, fecha_actualizacion, password_hash
                FROM usuarios WHERE (nombre_usuario = %s OR email = %s) AND activo = true
            """
            
            cursor.execute(query, (username_or_email, username_or_email))
            user = cursor.fetchone()
            
            return dict(user) if user else None
            
        except Exception as e:
            print(f"Error obteniendo usuario por username/email: {e}")
            return None
        finally:
            cursor.close()
            self.db.close()
    
    def update_user(self, user_id, username, first_name, last_name, email, phone, role, organization='empuje-comunitario'):
        """Actualiza un usuario existente"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            # Update user (MySQL no soporta RETURNING)
            query = """
                UPDATE usuarios 
                SET nombre_usuario = %s, nombre = %s, apellido = %s, email = %s, telefono = %s, rol = %s, organizacion = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(query, (username, first_name, last_name, email, phone, role, organization, user_id))
            conn.commit()
            
            # Fetch the updated user
            select_query = """
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, organizacion, activo, fecha_creacion, fecha_actualizacion
                FROM usuarios WHERE id = %s
            """
            cursor.execute(select_query, (user_id,))
            user = cursor.fetchone()
            
            return dict(user) if user else None
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            cursor.close()
            self.db.close()
    
    def delete_user(self, user_id):
        """Aplica baja lógica a un usuario"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            # Primero remover de eventos futuros
            remove_from_events_query = """
                DELETE FROM participantes_evento 
                WHERE usuario_id = %s AND evento_id IN (
                    SELECT id FROM eventos WHERE fecha_evento > CURRENT_TIMESTAMP
                )
            """
            cursor.execute(remove_from_events_query, (user_id,))
            
            # Luego aplicar baja lógica
            query = """
                UPDATE usuarios 
                SET activo = false, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(query, (user_id,))
            success = cursor.rowcount > 0
            conn.commit()
            
            return success
            
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            cursor.close()
            self.db.close()
    
    def list_users(self, include_inactive=False, organization=None):
        """Lista usuarios, opcionalmente filtrados por organización"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            base_query = """
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, organizacion, activo, fecha_creacion, fecha_actualizacion
                FROM usuarios
            """
            
            conditions = []
            params = []
            
            if not include_inactive:
                conditions.append("activo = true")
            
            if organization:
                conditions.append("organizacion = %s")
                params.append(organization)
            
            if conditions:
                query = base_query + " WHERE " + " AND ".join(conditions)
            else:
                query = base_query
            
            query += " ORDER BY nombre, apellido"
            
            cursor.execute(query, params)
            users = cursor.fetchall()
            return [dict(user) for user in users]
            
        except Exception as e:
            print(f"Error listando usuarios: {e}")
            return []
        finally:
            cursor.close()
            self.db.close()
    
    def username_exists(self, username, exclude_id=None):
        """Verifica si un nombre de usuario ya existe"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            if exclude_id:
                query = "SELECT id FROM usuarios WHERE nombre_usuario = %s AND id != %s"
                cursor.execute(query, (username, exclude_id))
            else:
                query = "SELECT id FROM usuarios WHERE nombre_usuario = %s"
                cursor.execute(query, (username,))
            
            result = cursor.fetchone()
            return result is not None
            
        except Exception as e:
            print(f"Error verificando username: {e}")
            return False
        finally:
            cursor.close()
            self.db.close()
    
    def email_exists(self, email, exclude_id=None):
        """Verifica si un email ya existe"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            if exclude_id:
                query = "SELECT id FROM usuarios WHERE email = %s AND id != %s"
                cursor.execute(query, (email, exclude_id))
            else:
                query = "SELECT id FROM usuarios WHERE email = %s"
                cursor.execute(query, (email,))
            
            result = cursor.fetchone()
            return result is not None
            
        except Exception as e:
            print(f"Error verificando email: {e}")
            return False
        finally:
            cursor.close()
            self.db.close()