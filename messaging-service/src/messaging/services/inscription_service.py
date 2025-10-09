"""
Servicio para gestión de solicitudes de inscripción
"""
import logging
import uuid
from datetime import datetime
from ..database.connection import get_db_connection
from ..producers.inscription_request_producer import inscription_request_producer

logger = logging.getLogger(__name__)

class InscriptionService:
    def __init__(self):
        self.db = get_db_connection()
    
    def create_inscription_request(self, solicitud_data):
        """
        Crear nueva solicitud de inscripción
        
        Args:
            solicitud_data (dict): Datos de la solicitud
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            conn = self.db.connect()
            cursor = conn.cursor(dictionary=True)
            
            # Generar ID único para la solicitud
            solicitud_id = f"INS-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Verificar que el email no esté ya registrado
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (solicitud_data['email'],))
            if cursor.fetchone():
                return {
                    'success': False,
                    'message': 'El email ya está registrado en el sistema'
                }
            
            # Verificar que no haya solicitud pendiente con el mismo email
            cursor.execute("""
                SELECT id FROM solicitudes_inscripcion 
                WHERE email = %s AND estado = 'PENDIENTE'
            """, (solicitud_data['email'],))
            
            if cursor.fetchone():
                return {
                    'success': False,
                    'message': 'Ya existe una solicitud pendiente para este email'
                }
            
            # Insertar solicitud en base de datos
            cursor.execute("""
                INSERT INTO solicitudes_inscripcion 
                (solicitud_id, nombre, apellido, email, telefono, organizacion_destino, 
                 rol_solicitado, mensaje, datos_adicionales)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                solicitud_id,
                solicitud_data['nombre'],
                solicitud_data['apellido'],
                solicitud_data['email'],
                solicitud_data.get('telefono'),
                solicitud_data['organizacion_destino'],
                solicitud_data['rol_solicitado'],
                solicitud_data.get('mensaje'),
                solicitud_data.get('datos_adicionales', '{}')
            ))
            
            conn.commit()
            
            # Enviar mensaje a Kafka
            kafka_data = {
                'solicitud_id': solicitud_id,
                'organizacion_destino': solicitud_data['organizacion_destino'],
                'nombre': solicitud_data['nombre'],
                'apellido': solicitud_data['apellido'],
                'email': solicitud_data['email'],
                'telefono': solicitud_data.get('telefono'),
                'rol_solicitado': solicitud_data['rol_solicitado'],
                'mensaje': solicitud_data.get('mensaje'),
                'datos_adicionales': solicitud_data.get('datos_adicionales', {})
            }
            
            kafka_success = inscription_request_producer.send_inscription_request(kafka_data)
            
            cursor.close()
            conn.close()
            
            if kafka_success:
                logger.info(f"Solicitud de inscripción creada: {solicitud_id}")
                return {
                    'success': True,
                    'message': 'Solicitud de inscripción enviada exitosamente',
                    'solicitud_id': solicitud_id
                }
            else:
                logger.warning(f"Solicitud creada pero no se pudo enviar a Kafka: {solicitud_id}")
                return {
                    'success': True,
                    'message': 'Solicitud creada, pero puede haber demora en la notificación',
                    'solicitud_id': solicitud_id
                }
            
        except Exception as e:
            logger.error(f"Error creando solicitud de inscripción: {e}")
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            return {
                'success': False,
                'message': f'Error interno: {str(e)}'
            }
    
    def get_pending_requests(self, organizacion, usuario_id):
        """
        Obtener solicitudes pendientes para una organización
        
        Args:
            organizacion (str): Nombre de la organización
            usuario_id (int): ID del usuario que consulta
            
        Returns:
            dict: Lista de solicitudes pendientes
        """
        try:
            conn = self.db.connect()
            cursor = conn.cursor(dictionary=True)
            
            # Verificar que el usuario tenga permisos (PRESIDENTE o VOCAL)
            cursor.execute("""
                SELECT rol FROM usuarios 
                WHERE id = %s AND organizacion = %s AND rol IN ('PRESIDENTE', 'VOCAL')
            """, (usuario_id, organizacion))
            
            if not cursor.fetchone():
                return {
                    'success': False,
                    'message': 'No tiene permisos para ver solicitudes de inscripción'
                }
            
            # Obtener solicitudes pendientes
            cursor.execute("""
                SELECT si.*, 
                       ns.leida,
                       ns.fecha_creacion as fecha_notificacion
                FROM solicitudes_inscripcion si
                LEFT JOIN notificaciones_solicitudes ns ON si.solicitud_id = ns.solicitud_id 
                    AND ns.usuario_destinatario = %s
                WHERE si.organizacion_destino = %s 
                AND si.estado = 'PENDIENTE'
                ORDER BY si.fecha_solicitud DESC
            """, (usuario_id, organizacion))
            
            solicitudes = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'solicitudes': solicitudes
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo solicitudes pendientes: {e}")
            if 'conn' in locals():
                cursor.close()
                conn.close()
            return {
                'success': False,
                'message': f'Error interno: {str(e)}'
            }
    
    def process_inscription_request(self, solicitud_id, accion, usuario_revisor, comentarios=None):
        """
        Procesar solicitud de inscripción (aprobar/denegar)
        
        Args:
            solicitud_id (str): ID de la solicitud
            accion (str): 'APROBAR' o 'DENEGAR'
            usuario_revisor (dict): Información del usuario revisor
            comentarios (str): Comentarios del revisor
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            conn = self.db.connect()
            cursor = conn.cursor(dictionary=True)
            
            # Obtener datos de la solicitud
            cursor.execute("""
                SELECT * FROM solicitudes_inscripcion 
                WHERE solicitud_id = %s AND estado = 'PENDIENTE'
            """, (solicitud_id,))
            
            solicitud = cursor.fetchone()
            if not solicitud:
                return {
                    'success': False,
                    'message': 'Solicitud no encontrada o ya procesada'
                }
            
            # Verificar permisos del revisor
            cursor.execute("""
                SELECT * FROM usuarios 
                WHERE id = %s AND organizacion = %s AND rol IN ('PRESIDENTE', 'VOCAL')
            """, (usuario_revisor['id'], solicitud['organizacion_destino']))
            
            if not cursor.fetchone():
                return {
                    'success': False,
                    'message': 'No tiene permisos para procesar esta solicitud'
                }
            
            # Determinar estado final
            estado_final = 'APROBADA' if accion == 'APROBAR' else 'DENEGADA'
            
            # Actualizar solicitud
            cursor.execute("""
                UPDATE solicitudes_inscripcion 
                SET estado = %s, 
                    fecha_respuesta = %s,
                    usuario_revisor = %s,
                    comentarios_revisor = %s
                WHERE solicitud_id = %s
            """, (
                estado_final,
                datetime.now(),
                usuario_revisor['id'],
                comentarios
            ))
            
            # Marcar notificaciones como leídas
            cursor.execute("""
                UPDATE notificaciones_solicitudes 
                SET leida = TRUE 
                WHERE solicitud_id = %s
            """, (solicitud_id,))
            
            conn.commit()
            
            # Enviar respuesta a Kafka
            kafka_success = inscription_request_producer.send_inscription_response(
                solicitud_id,
                solicitud['organizacion_destino'],
                estado_final,
                usuario_revisor,
                comentarios
            )
            
            cursor.close()
            conn.close()
            
            if kafka_success:
                logger.info(f"Solicitud procesada: {solicitud_id} - {estado_final}")
                return {
                    'success': True,
                    'message': f'Solicitud {estado_final.lower()} exitosamente',
                    'estado': estado_final
                }
            else:
                logger.warning(f"Solicitud procesada pero no se pudo enviar a Kafka: {solicitud_id}")
                return {
                    'success': True,
                    'message': f'Solicitud {estado_final.lower()}, pero puede haber demora en la notificación',
                    'estado': estado_final
                }
            
        except Exception as e:
            logger.error(f"Error procesando solicitud {solicitud_id}: {e}")
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            return {
                'success': False,
                'message': f'Error interno: {str(e)}'
            }
    
    def get_user_notifications(self, usuario_id):
        """
        Obtener notificaciones de solicitudes para un usuario
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            dict: Lista de notificaciones
        """
        try:
            conn = self.db.connect()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT ns.*, si.nombre, si.apellido, si.email, si.rol_solicitado
                FROM notificaciones_solicitudes ns
                JOIN solicitudes_inscripcion si ON ns.solicitud_id = si.solicitud_id
                WHERE ns.usuario_destinatario = %s
                ORDER BY ns.fecha_creacion DESC
                LIMIT 50
            """, (usuario_id,))
            
            notificaciones = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'notificaciones': notificaciones
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo notificaciones: {e}")
            if 'conn' in locals():
                cursor.close()
                conn.close()
            return {
                'success': False,
                'message': f'Error interno: {str(e)}'
            }

# Instancia global del servicio
inscription_service = InscriptionService()