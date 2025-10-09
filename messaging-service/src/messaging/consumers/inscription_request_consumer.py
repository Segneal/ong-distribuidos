"""
Consumer para solicitudes de inscripción
"""
import json
import logging
from datetime import datetime
from ..kafka.connection import get_kafka_consumer
from ..database.connection import get_db_connection

logger = logging.getLogger(__name__)

class InscriptionRequestConsumer:
    def __init__(self):
        self.consumer = get_kafka_consumer(['inscription-requests', 'inscription-responses'])
        self.db = get_db_connection()
    
    def process_messages(self):
        """Procesar mensajes de solicitudes de inscripción"""
        try:
            for message in self.consumer:
                try:
                    # Decodificar mensaje
                    message_data = json.loads(message.value.decode('utf-8'))
                    topic = message.topic
                    
                    logger.info(f"Procesando mensaje de {topic}: {message_data.get('event_type')}")
                    
                    if topic == 'inscription-requests':
                        self._process_inscription_request(message_data)
                    elif topic == 'inscription-responses':
                        self._process_inscription_response(message_data)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error decodificando mensaje JSON: {e}")
                except Exception as e:
                    logger.error(f"Error procesando mensaje: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Consumer detenido por usuario")
        except Exception as e:
            logger.error(f"Error en consumer: {e}")
        finally:
            self.consumer.close()
    
    def _process_inscription_request(self, message_data):
        """
        Procesar nueva solicitud de inscripción
        
        Args:
            message_data (dict): Datos del mensaje
        """
        try:
            conn = self.db.connect()
            cursor = conn.cursor(dictionary=True)
            
            # Obtener usuarios PRESIDENTE y VOCAL de la organización destino
            cursor.execute("""
                SELECT id, nombre, apellido, email, rol, organizacion
                FROM usuarios 
                WHERE organizacion = %s 
                AND rol IN ('PRESIDENTE', 'VOCAL')
                AND activo = TRUE
            """, (message_data['organizacion_destino'],))
            
            destinatarios = cursor.fetchall()
            
            if not destinatarios:
                logger.warning(f"No se encontraron PRESIDENTE/VOCAL para organización: {message_data['organizacion_destino']}")
                cursor.close()
                conn.close()
                return
            
            # Crear notificaciones para cada destinatario
            for destinatario in destinatarios:
                cursor.execute("""
                    INSERT INTO notificaciones_solicitudes 
                    (solicitud_id, usuario_destinatario, tipo_notificacion)
                    VALUES (%s, %s, 'NUEVA_SOLICITUD')
                """, (
                    message_data['solicitud_id'],
                    destinatario['id']
                ))
                
                logger.info(f"Notificación creada para {destinatario['nombre']} ({destinatario['rol']}) "
                           f"sobre solicitud {message_data['solicitud_id']}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Procesada solicitud de inscripción: {message_data['solicitud_id']} "
                       f"- {len(destinatarios)} notificaciones creadas")
            
        except Exception as e:
            logger.error(f"Error procesando solicitud de inscripción: {e}")
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
    
    def _process_inscription_response(self, message_data):
        """
        Procesar respuesta a solicitud de inscripción
        
        Args:
            message_data (dict): Datos del mensaje
        """
        try:
            conn = self.db.connect()
            cursor = conn.cursor(dictionary=True)
            
            # Actualizar estado de la solicitud
            cursor.execute("""
                UPDATE solicitudes_inscripcion 
                SET estado = %s, 
                    fecha_respuesta = %s,
                    usuario_revisor = %s,
                    comentarios_revisor = %s
                WHERE solicitud_id = %s
            """, (
                message_data['estado'],
                message_data['fecha_respuesta'],
                message_data['revisor']['id'],
                message_data.get('comentarios')
            ))
            
            # Si fue aprobada, crear el usuario
            if message_data['estado'] == 'APROBADA':
                self._create_approved_user(cursor, message_data['solicitud_id'])
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Procesada respuesta de inscripción: {message_data['solicitud_id']} - {message_data['estado']}")
            
        except Exception as e:
            logger.error(f"Error procesando respuesta de inscripción: {e}")
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
    
    def _create_approved_user(self, cursor, solicitud_id):
        """
        Crear usuario para solicitud aprobada
        
        Args:
            cursor: Cursor de base de datos
            solicitud_id (str): ID de la solicitud
        """
        try:
            # Obtener datos de la solicitud
            cursor.execute("""
                SELECT * FROM solicitudes_inscripcion 
                WHERE solicitud_id = %s
            """, (solicitud_id,))
            
            solicitud = cursor.fetchone()
            if not solicitud:
                logger.error(f"No se encontró solicitud: {solicitud_id}")
                return
            
            # Generar nombre de usuario único
            base_username = f"{solicitud['nombre'].lower()}.{solicitud['apellido'].lower()}"
            username = base_username
            counter = 1
            
            while True:
                cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            # Crear usuario con contraseña temporal
            import bcrypt
            temp_password = "temporal123"  # En producción, generar contraseña aleatoria
            password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO usuarios 
                (nombre_usuario, nombre, apellido, telefono, email, password_hash, rol, organizacion, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            """, (
                username,
                solicitud['nombre'],
                solicitud['apellido'],
                solicitud['telefono'],
                solicitud['email'],
                password_hash,
                solicitud['rol_solicitado'],
                solicitud['organizacion_destino']
            ))
            
            logger.info(f"Usuario creado: {username} para solicitud aprobada {solicitud_id}")
            
        except Exception as e:
            logger.error(f"Error creando usuario para solicitud {solicitud_id}: {e}")
            raise

def start_inscription_consumer():
    """Iniciar el consumer de solicitudes de inscripción"""
    consumer = InscriptionRequestConsumer()
    logger.info("Iniciando consumer de solicitudes de inscripción...")
    consumer.process_messages()

if __name__ == "__main__":
    start_inscription_consumer()