"""
ONG Network Messaging Service

Kafka-based messaging service for enabling collaboration between ONGs
through donation requests, transfers, offers, events, and adhesions.
"""

__version__ = "1.0.0"
__author__ = "ONG Management System"

from .messaging.config import settings, Topics
from .messaging.kafka.connection import kafka_manager
from .messaging.producers.base_producer import BaseProducer
from .messaging.consumers.base_consumer import BaseConsumer, NetworkConsumer, OrganizationConsumer

__all__ = [
    "settings",
    "Topics", 
    "kafka_manager",
    "BaseProducer",
    "BaseConsumer",
    "NetworkConsumer",
    "OrganizationConsumer"
]