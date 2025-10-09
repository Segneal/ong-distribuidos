"""
Consumer para procesar mensajes de baja de eventos solidarios
Topic: /baja-evento-solidario
"""
import json
import logging
from kafka import KafkaConsumer
from messaging.database.connection import get_database_connection
from messaging.kafka.connection import get_kafka_connection

logger = logging.getLogger(__name__)

class EventCancellationConsumer:
    def __init__(self):
        self.consumer = None
        self.topic = "baja-evento-solidario"
        
    def start_consuming(self):
        """Inicia el consumo de mensajes de baja de eventos"""
        try:
            kafka_config = get_kafka_connection()
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=kafka_config['bootstrap_servers'],
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id='ong-management-event-cancellation',
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
            
            logger.info(f"Iniciando consumer para topic: {self.topic}")
            
            for message in self.consumer:
                try:
                    self.process_event_cancellation(message.value)
                except Exception as e:
                    logger.error(f"Error procesando mensaje de baja de evento: {e}")
                    
        except Exception as e:
            logger.error(f"Error en consumer de baja de eventos: {e}")
            
    def process_event_cancellation(self, message_data):
        """
        Procesa un mensaje de baja de evento
        
        Formato esperado del mensaje:
        {
            "organization_id": "fundacion-esperanza",
            "event_id": 101,
            "cancellation_reason": "Cancelado por mal tiempo",
            "timestamp": "2025-09-30T22:30:00Z"
        }
        """
        try:
            logger.info(f"Procesando baja de evento: {message_data}")
            
            organization_id = message_data.get('organization_id')
            event_id = message_data.get('event_id')
            cancellation_reason = message_data.get('cancellation_reason', 'Evento cancelado por la organización')
            
            if not organization_id or not event_id:
                logger.error("Mensaje inválido: falta organization_id o event_id")
                return
                
            # Actualizar evento en eventos_red
            self._deactivate_network_event(organization_id, event_id, cancellation_reason)
            
            # Notificar a usuarios inscritos
            self._notify_registered_users(organization_id, event_id, cancellation_reason)
            
            # Registrar en historial
            self._log_cancellation(organization_id, event_id, cancellation_reason)
            
            logger.info(f"Evento {event_id} de {organization_id} dado de baja exitosamente")
            
        except Exception as e:
            logger.error(f"Error procesando baja de evento: {e}")
            
    def _deactivate_network_event(self, organization_id, event_id, reason):
        """Desactiva el evento en la tabla eventos_red"""
        try:
            connection = get_database_connection()
            cursor = connection.cursor()
            
            # Marcar evento como inactivo
            query = """
                UPDATE eventos_red 
                SET activo = false, 
                    descripcion = CONCAT(descripcion, ' - CANCELADO: ', %s)
                WHERE evento_id = %s AND organizacion_origen = %s
            """
            
            cursor.execute(query, (reason, event_id, organization_id))
            connection.commit()
            
            logger.info(f"Evento {event_id} de {organization_id} desactivado en eventos_red")
            
        except Exception as e:
            logger.error(f"Error desactivando evento en red: {e}")
        finally:
            if connection:
                connection.close()
                
    def _notify_registered_users(self, organization_id, event_id, reason):
        """Notifica a usuarios que tenían adhesiones al evento cancelado"""
        try:
            connection = get_database_connection()
            cursor = connection.cursor()
            
            # Obtener usuarios inscritos al evento
            query = """
                SELECT aee.voluntario_id, u.name, u.lastName, u.email, er.nombre as event_name
                FROM adhesiones_eventos_externos aee
                JOIN usuarios u ON aee.voluntario_id = u.id
                JOIN eventos_red er ON aee.evento_externo_id = er.evento_id 
                    AND er.organizacion_origen = %s
                WHERE aee.evento_externo_id = %s 
                AND aee.estado = 'CONFIRMADA'
            """
            
            cursor.execute(query, (organization_id, event_id))
            registered_users = cursor.fetchall()
            
            # Actualizar estado de adhesiones
            update_query = """
                UPDATE adhesiones_eventos_externos 
                SET estado = 'CANCELADA'
                WHERE evento_externo_id = %s
            """
            cursor.execute(update_query, (event_id,))
            connection.commit()
            
            # Crear notificaciones para los usuarios
            for user in registered_users:
                self._create_user_notification(
                    user[0],  # user_id
                    f"Evento Cancelado: {user[4]}",  # event_name
                    f"El evento '{user[4]}' de {organization_id} ha sido cancelado. Motivo: {reason}",
                    'EVENT_CANCELLED'
                )
            
            logger.info(f"Notificados {len(registered_users)} usuarios sobre cancelación del evento {event_id}")
            
        except Exception as e:
            logger.error(f"Error notificando usuarios: {e}")
        finally:
            if connection:
                connection.close()
                
    def _create_user_notification(self, user_id, title, message, notification_type):
        """Crea una notificación para un usuario"""
        try:
            connection = get_database_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO notificaciones_usuarios 
                (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
                VALUES (%s, %s, %s, %s, NOW(), false)
            """
            
            cursor.execute(query, (user_id, title, message, notification_type))
            connection.commit()
            
        except Exception as e:
            logger.error(f"Error creando notificación para usuario {user_id}: {e}")
        finally:
            if connection:
                connection.close()
                
    def _log_cancellation(self, organization_id, event_id, reason):
        """Registra la cancelación en el historial de mensajes"""
        try:
            connection = get_database_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO historial_mensajes 
                (topic, tipo_mensaje, organizacion_origen, contenido, estado, fecha_procesamiento)
                VALUES (%s, %s, %s, %s, 'PROCESADO', NOW())
            """
            
            content = json.dumps({
                'event_id': event_id,
                'organization_id': organization_id,
                'cancellation_reason': reason,
                'action': 'event_cancelled'
            })
            
            cursor.execute(query, (self.topic, 'EVENT_CANCELLATION', organization_id, content))
            connection.commit()
            
        except Exception as e:
            logger.error(f"Error registrando cancelación en historial: {e}")
        finally:
            if connection:
                connection.close()
                
    def stop_consuming(self):
        """Detiene el consumer"""
        if self.consumer:
            self.consumer.close()
            logger.info("Consumer de baja de eventos detenido")