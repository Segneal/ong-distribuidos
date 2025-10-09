"""
Producer para enviar mensajes de baja de eventos al topic /baja-evento-solidario
"""
import json
import logging
from datetime import datetime
from kafka import KafkaProducer
from messaging.kafka.connection import get_kafka_connection

logger = logging.getLogger(__name__)

class EventCancellationProducer:
    def __init__(self):
        self.producer = None
        self.topic = "baja-evento-solidario"
        
    def _get_producer(self):
        """Obtiene o crea el producer de Kafka"""
        if not self.producer:
            kafka_config = get_kafka_connection()
            self.producer = KafkaProducer(
                bootstrap_servers=kafka_config['bootstrap_servers'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None
            )
        return self.producer
        
    def publish_event_cancellation(self, event_id, cancellation_reason="Evento cancelado"):
        """
        Publica un mensaje de baja de evento en el topic
        
        Args:
            event_id (int): ID del evento cancelado
            cancellation_reason (str): Motivo de la cancelación
        """
        try:
            message = {
                "organization_id": "empuje-comunitario",
                "event_id": event_id,
                "cancellation_reason": cancellation_reason,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            producer = self._get_producer()
            
            # Usar event_id como key para particionado
            key = f"empuje-comunitario-{event_id}"
            
            future = producer.send(
                self.topic,
                key=key,
                value=message
            )
            
            # Esperar confirmación
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Mensaje de baja de evento enviado exitosamente:")
            logger.info(f"  Topic: {record_metadata.topic}")
            logger.info(f"  Partition: {record_metadata.partition}")
            logger.info(f"  Offset: {record_metadata.offset}")
            logger.info(f"  Event ID: {event_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando mensaje de baja de evento: {e}")
            return False
            
    def close(self):
        """Cierra el producer"""
        if self.producer:
            self.producer.close()
            logger.info("Producer de baja de eventos cerrado")