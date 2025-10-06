"""
Producer para solicitudes de inscripción
"""
import json
import logging
from datetime import datetime
from ..kafka.connection import get_kafka_producer

logger = logging.getLogger(__name__)

class InscriptionRequestProducer:
    def __init__(self):
        self.producer = get_kafka_producer()
        self.topic = 'inscription-requests'
    
    def send_inscription_request(self, solicitud_data):
        """
        Enviar solicitud de inscripción a Kafka
        
        Args:
            solicitud_data (dict): Datos de la solicitud de inscripción
        """
        try:
            message = {
                'event_type': 'NUEVA_SOLICITUD_INSCRIPCION',
                'timestamp': datetime.now().isoformat(),
                'solicitud_id': solicitud_data['solicitud_id'],
                'organizacion_destino': solicitud_data['organizacion_destino'],
                'solicitante': {
                    'nombre': solicitud_data['nombre'],
                    'apellido': solicitud_data['apellido'],
                    'email': solicitud_data['email'],
                    'telefono': solicitud_data.get('telefono'),
                    'rol_solicitado': solicitud_data['rol_solicitado'],
                    'mensaje': solicitud_data.get('mensaje')
                },
                'metadata': {
                    'fecha_solicitud': solicitud_data.get('fecha_solicitud', datetime.now().isoformat()),
                    'datos_adicionales': solicitud_data.get('datos_adicionales', {})
                }
            }
            
            # Enviar mensaje a Kafka
            future = self.producer.send(
                self.topic,
                key=solicitud_data['solicitud_id'].encode('utf-8'),
                value=json.dumps(message).encode('utf-8')
            )
            
            # Esperar confirmación
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Solicitud de inscripción enviada: {solicitud_data['solicitud_id']} "
                       f"a topic {record_metadata.topic} partition {record_metadata.partition}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando solicitud de inscripción {solicitud_data.get('solicitud_id')}: {e}")
            return False
    
    def send_inscription_response(self, solicitud_id, organizacion, estado, revisor_info, comentarios=None):
        """
        Enviar respuesta a solicitud de inscripción
        
        Args:
            solicitud_id (str): ID de la solicitud
            organizacion (str): Organización que responde
            estado (str): APROBADA o DENEGADA
            revisor_info (dict): Información del revisor
            comentarios (str): Comentarios del revisor
        """
        try:
            message = {
                'event_type': f'SOLICITUD_{estado.upper()}',
                'timestamp': datetime.now().isoformat(),
                'solicitud_id': solicitud_id,
                'organizacion': organizacion,
                'estado': estado,
                'revisor': {
                    'id': revisor_info['id'],
                    'nombre': revisor_info['nombre'],
                    'rol': revisor_info['rol']
                },
                'comentarios': comentarios,
                'fecha_respuesta': datetime.now().isoformat()
            }
            
            # Enviar mensaje a Kafka
            future = self.producer.send(
                'inscription-responses',
                key=solicitud_id.encode('utf-8'),
                value=json.dumps(message).encode('utf-8')
            )
            
            # Esperar confirmación
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Respuesta de inscripción enviada: {solicitud_id} - {estado} "
                       f"a topic {record_metadata.topic}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando respuesta de inscripción {solicitud_id}: {e}")
            return False
    
    def close(self):
        """Cerrar el producer"""
        if self.producer:
            self.producer.close()

# Instancia global del producer
inscription_request_producer = InscriptionRequestProducer()