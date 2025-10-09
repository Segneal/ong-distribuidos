from database_mysql import get_db_connection
from datetime import datetime

class UserRepository:
    def __init__(self):
        self.db = get_db_connection()
    
    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """Método helper para ejecutar queries con manejo de errores"""
        conn = None
        cursor = None
        try:
            conn = self.db.connect()
            if not conn:
                print("❌ No se pudo establecer conexión a la base de datos")
                return None
                
            cursor = self.db.get_cursor()
            if not cursor:
                print("❌ No se pudo obtener cursor de la base de datos")
                return None
            
            cursor.execute(query, params or ())
            
            result = None
            if fetch_one:
                result = cursor.fetchone()
                result = dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                result = [dict(row) for row in results]
            else:
                result = cursor.rowcount
            
            if commit:
                conn.commit()
            
            return result
            
        except Exception as e:
            print(f"❌ Error ejecutando query: {e}")
            if conn and commit:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.db.close()
    
    def create_user(self, username, first_name, last_name, email, phone, role, password_hash):
        """Crea un nuevo usuario en la base de datos"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            # Insert user (MySQL no soporta RETURNING)
            query = """
                INSERT INTO usuarios (nombre_usuario, nombre, apellido, email, telefono, password_hash, rol)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (username, first_name, last_name, email, phone, password_hash, role))
            user_id = cursor.lastrowid
            conn.commit()
            
            # Fetch the created user
            select_query = """
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, activo, fecha_creacion, fecha_actualizacion
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
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, activo, fecha_creacion, fecha_actualizacion
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
        query = """
            SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, activo, fecha_creacion, fecha_actualizacion, password_hash
            FROM usuarios WHERE (nombre_usuario = %s OR email = %s) AND activo = true
        """
        return self._execute_query(query, (username_or_email, username_or_email), fetch_one=True)
    
    def update_user(self, user_id, username, first_name, last_name, email, phone, role):
        """Actualiza un usuario existente"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            # Update user (MySQL no soporta RETURNING)
            query = """
                UPDATE usuarios 
                SET nombre_usuario = %s, nombre = %s, apellido = %s, email = %s, telefono = %s, rol = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(query, (username, first_name, last_name, email, phone, role, user_id))
            conn.commit()
            
            # Fetch the updated user
            select_query = """
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, activo, fecha_creacion, fecha_actualizacion
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
    
    def list_users(self, include_inactive=False):
        """Lista todos los usuarios"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            if include_inactive:
                query = """
                    SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, activo, fecha_creacion, fecha_actualizacion
                    FROM usuarios ORDER BY nombre, apellido
                """
                cursor.execute(query)
            else:
                query = """
                    SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, activo, fecha_creacion, fecha_actualizacion
                    FROM usuarios WHERE activo = true ORDER BY nombre, apellido
                """
                cursor.execute(query)
            
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