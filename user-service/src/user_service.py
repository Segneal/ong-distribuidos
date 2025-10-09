import grpc
from concurrent import futures
import users_pb2
import users_pb2_grpc
from user_repository_mysql import UserRepository
from password_generator import generate_random_password
from crypto import hash_password, verify_password
from email_sender import send_password_email
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class UserService(users_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.repository = UserRepository()
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')
    
    def _convert_role_to_string(self, role_enum):
        """Convierte el enum de rol a string"""
        role_map = {
            users_pb2.PRESIDENTE: 'PRESIDENTE',
            users_pb2.VOCAL: 'VOCAL',
            users_pb2.COORDINADOR: 'COORDINADOR',
            users_pb2.VOLUNTARIO: 'VOLUNTARIO'
        }
        return role_map.get(role_enum, 'VOLUNTARIO')
    
    def _convert_string_to_role(self, role_string):
        """Convierte string de rol a enum"""
        role_map = {
            'PRESIDENTE': users_pb2.PRESIDENTE,
            'VOCAL': users_pb2.VOCAL,
            'COORDINADOR': users_pb2.COORDINADOR,
            'VOLUNTARIO': users_pb2.VOLUNTARIO
        }
        return role_map.get(role_string, users_pb2.VOLUNTARIO)
    
    def _create_user_message(self, user_data):
        """Crea un mensaje User desde los datos de la base de datos"""
        return users_pb2.User(
            id=user_data['id'],
            username=user_data['nombre_usuario'],
            first_name=user_data['nombre'],
            last_name=user_data['apellido'],
            email=user_data['email'],
            phone=user_data.get('telefono', ''),
            role=self._convert_string_to_role(user_data['rol']),
            is_active=user_data['activo'],
            created_at=str(user_data['fecha_creacion']),
            updated_at=str(user_data['fecha_actualizacion']),
            organization=user_data.get('organizacion', 'empuje-comunitario')
        )
    
    def CreateUser(self, request, context):
        """Crea un nuevo usuario"""
        try:
            print(f"=== CreateUser DEBUG ===")
            print(f"Request type: {type(request)}")
            print(f"Request fields: {[field.name for field in request.DESCRIPTOR.fields]}")
            print(f"Username: {request.username}")
            print(f"First name: {request.first_name}")
            print(f"Last name: {request.last_name}")
            print(f"Email: {request.email}")
            print(f"Phone: {request.phone}")
            print(f"Role: {request.role}")
            
            # Verificar si tiene campo organization
            has_org = hasattr(request, 'organization')
            print(f"Has organization field: {has_org}")
            if has_org:
                print(f"Organization value: '{request.organization}'")
            
            org_value = getattr(request, 'organization', 'empuje-comunitario')
            print(f"Organization to use: '{org_value}'")
            
            # Validar que el username no exista
            if self.repository.username_exists(request.username):
                return users_pb2.UserResponse(
                    success=False,
                    message="El nombre de usuario ya existe"
                )
            
            # Validar que el email no exista
            if self.repository.email_exists(request.email):
                return users_pb2.UserResponse(
                    success=False,
                    message="El email ya existe"
                )
            
            # Generar contraseña aleatoria
            password = generate_random_password()
            password_hash = hash_password(password)
            
            # Convertir rol a string
            role_string = self._convert_role_to_string(request.role)
            
            # Crear usuario en la base de datos
            # Crear usuario en la base de datos
            org_param = getattr(request, 'organization', 'empuje-comunitario')
            print(f"=== Calling repository.create_user ===")
            print(f"Args count: 8")
            print(f"1. username: {request.username}")
            print(f"2. first_name: {request.first_name}")
            print(f"3. last_name: {request.last_name}")
            print(f"4. email: {request.email}")
            print(f"5. phone: {request.phone}")
            print(f"6. role: {role_string}")
            print(f"7. password_hash: {password_hash[:10]}...")
            print(f"8. organization: {org_param}")
            
            user_data = self.repository.create_user(
                request.username,
                request.first_name,
                request.last_name,
                request.email,
                request.phone,
                role_string,
                password_hash,
                org_param
            )
            
            if user_data:
                # Enviar contraseña por email
                send_password_email(request.email, request.username, password, request.first_name, request.last_name)
                
                user_message = self._create_user_message(user_data)
                return users_pb2.UserResponse(
                    success=True,
                    message="Usuario creado exitosamente",
                    user=user_message
                )
            else:
                return users_pb2.UserResponse(
                    success=False,
                    message="Error creando el usuario"
                )
                
        except Exception as e:
            print(f"Error en CreateUser: {e}")
            return users_pb2.UserResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def GetUser(self, request, context):
        """Obtiene un usuario por ID"""
        try:
            user_data = self.repository.get_user_by_id(request.id)
            
            if user_data:
                user_message = self._create_user_message(user_data)
                return users_pb2.UserResponse(
                    success=True,
                    message="Usuario encontrado",
                    user=user_message
                )
            else:
                return users_pb2.UserResponse(
                    success=False,
                    message="Usuario no encontrado"
                )
                
        except Exception as e:
            print(f"Error en GetUser: {e}")
            return users_pb2.UserResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def UpdateUser(self, request, context):
        """Actualiza un usuario existente"""
        try:
            # Validar que el usuario existe
            existing_user = self.repository.get_user_by_id(request.id)
            if not existing_user:
                return users_pb2.UserResponse(
                    success=False,
                    message="Usuario no encontrado"
                )
            
            # Validar que el username no exista (excluyendo el usuario actual)
            if self.repository.username_exists(request.username, request.id):
                return users_pb2.UserResponse(
                    success=False,
                    message="El nombre de usuario ya existe"
                )
            
            # Validar que el email no exista (excluyendo el usuario actual)
            if self.repository.email_exists(request.email, request.id):
                return users_pb2.UserResponse(
                    success=False,
                    message="El email ya existe"
                )
            
            # Convertir rol a string
            role_string = self._convert_role_to_string(request.role)
            
            # Actualizar usuario
            user_data = self.repository.update_user(
                request.id,
                request.username,
                request.first_name,
                request.last_name,
                request.email,
                request.phone,
                role_string,
                getattr(request, 'organization', 'empuje-comunitario')
            )
            
            if user_data:
                user_message = self._create_user_message(user_data)
                return users_pb2.UserResponse(
                    success=True,
                    message="Usuario actualizado exitosamente",
                    user=user_message
                )
            else:
                return users_pb2.UserResponse(
                    success=False,
                    message="Error actualizando el usuario"
                )
                
        except Exception as e:
            print(f"Error en UpdateUser: {e}")
            return users_pb2.UserResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def DeleteUser(self, request, context):
        """Elimina un usuario (baja lógica)"""
        try:
            success = self.repository.delete_user(request.id)
            
            if success:
                return users_pb2.DeleteUserResponse(
                    success=True,
                    message="Usuario eliminado exitosamente"
                )
            else:
                return users_pb2.DeleteUserResponse(
                    success=False,
                    message="Usuario no encontrado o error eliminando"
                )
                
        except Exception as e:
            print(f"Error en DeleteUser: {e}")
            return users_pb2.DeleteUserResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def ListUsers(self, request, context):
        """Lista todos los usuarios"""
        try:
            print(f"=== ListUsers DEBUG ===")
            users_data = self.repository.list_users(request.include_inactive)
            print(f"Users from repository: {len(users_data)}")
            
            users_messages = []
            for user_data in users_data:
                print(f"User: {user_data.get('nombre_usuario')} - Org: {user_data.get('organizacion')}")
                user_message = self._create_user_message(user_data)
                print(f"Message org: {user_message.organization}")
                users_messages.append(user_message)
            
            return users_pb2.ListUsersResponse(
                success=True,
                message=f"Se encontraron {len(users_messages)} usuarios",
                users=users_messages
            )
            
        except Exception as e:
            print(f"Error en ListUsers: {e}")
            return users_pb2.ListUsersResponse(
                success=False,
                message="Error interno del servidor",
                users=[]
            )
    
    def AuthenticateUser(self, request, context):
        """Autentica un usuario"""
        try:
            # Buscar usuario por username o email
            user_data = self.repository.get_user_by_username_or_email(request.username_or_email)
            
            if not user_data:
                return users_pb2.AuthResponse(
                    success=False,
                    message="Usuario/email inexistente"
                )
            
            if not user_data['activo']:
                return users_pb2.AuthResponse(
                    success=False,
                    message="Usuario inactivo"
                )
            
            # Verificar contraseña
            if not verify_password(request.password, user_data['password_hash']):
                return users_pb2.AuthResponse(
                    success=False,
                    message="Credenciales incorrectas"
                )
            
            # Generar JWT token
            payload = {
                'user_id': user_data['id'],
                'username': user_data['nombre_usuario'],
                'role': user_data['rol'],
                'organization': user_data.get('organizacion', 'empuje-comunitario'),
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            
            # Crear mensaje de usuario (sin password_hash)
            user_data_clean = {k: v for k, v in user_data.items() if k != 'password_hash'}
            user_message = self._create_user_message(user_data_clean)
            
            return users_pb2.AuthResponse(
                success=True,
                message="Autenticación exitosa",
                user=user_message,
                token=token
            )
            
        except Exception as e:
            print(f"Error en AuthenticateUser: {e}")
            import traceback
            traceback.print_exc()
            return users_pb2.AuthResponse(
                success=False,
                message="Error interno del servidor"
            )

def serve():
    """Inicia el servidor gRPC"""
    port = os.getenv('GRPC_PORT', '50051')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    print(f"🚀 User Service iniciado en puerto {port}")
    print(f"📊 Escuchando en {listen_addr}")
    
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo User Service...")
        server.stop(0)

if __name__ == '__main__':
    serve()