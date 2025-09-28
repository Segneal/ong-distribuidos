"""
ONG Network Messaging Service

Kafka-based messaging service for enabling collaboration between ONGs
through donation requests, transfers, offers, events, and adhesions.
"""

__version__ = "1.0.0"
__author__ = "ONG Management System"

from .config import settings, Topics
from .kafka_connection import kafka_manager
from .base_producer import BaseProducer
from .base_consumer import BaseConsumer, NetworkConsumer, OrganizationConsumer

__all__ = [
    "settings",
    "Topics", 
    "kafka_manager",
    "BaseProducer",
    "BaseConsumer",
    "NetworkConsumer",
    "OrganizationConsumer"
]