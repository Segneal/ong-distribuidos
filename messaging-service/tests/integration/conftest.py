"""
Integration test configuration and fixtures
"""
import pytest
import os
import time
import threading
import tempfile
import shutil
from unittest.mock import Mock, patch
import psycopg2
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError


@pytest.fixture(scope="session")
def kafka_config():
    """Kafka configuration for integration tests"""
    return {
        'bootstrap_servers': os.getenv('KAFKA_TEST_BROKERS', 'localhost:9093'),
        'group_id': 'test-messaging-group',
        'auto_offset_reset': 'earliest'
    }


@pytest.fixture(scope="session")
def test_topics():
    """Test topic names"""
    return [
        'test-donation-requests',
        'test-donation-offers',
        'test-request-cancellations',
        'test-solidarity-events',
        'test-event-cancellations',
        'test-transfer-test-org',
        'test-adhesion-test-org'
    ]


@pytest.fixture(scope="session")
def kafka_admin_client(kafka_config):
    """Kafka admin client for test setup"""
    try:
        admin = KafkaAdminClient(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            request_timeout_ms=10000
        )
        yield admin
        admin.close()
    except Exception as e:
        pytest.skip(f"Kafka not available for integration tests: {e}")


@pytest.fixture(scope="session")
def setup_kafka_topics(kafka_admin_client, test_topics):
    """Setup test topics in Kafka"""
    try:
        # Create topics
        topic_list = [
            NewTopic(name=topic, num_partitions=1, replication_factor=1)
            for topic in test_topics
        ]
        
        try:
            kafka_admin_client.create_topics(topic_list, validate_only=False)
        except TopicAlreadyExistsError:
            pass  # Topics already exist, that's fine
        
        # Wait for topics to be created
        time.sleep(2)
        
        yield test_topics
        
        # Cleanup topics after tests
        try:
            kafka_admin_client.delete_topics(test_topics)
        except Exception:
            pass  # Cleanup failed, but that's okay for tests
            
    except Exception as e:
        pytest.skip(f"Failed to setup Kafka topics: {e}")


@pytest.fixture
def kafka_producer(kafka_config):
    """Kafka producer for integration tests"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            request_timeout_ms=10000
        )
        yield producer
        producer.close()
    except Exception as e:
        pytest.skip(f"Failed to create Kafka producer: {e}")


@pytest.fixture
def kafka_consumer(kafka_config):
    """Kafka consumer for integration tests"""
    def _create_consumer(topics):
        try:
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=kafka_config['bootstrap_servers'],
                group_id=f"{kafka_config['group_id']}-{int(time.time())}",
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='earliest',
                consumer_timeout_ms=5000
            )
            return consumer
        except Exception as e:
            pytest.skip(f"Failed to create Kafka consumer: {e}")
    
    return _create_consumer


@pytest.fixture
def test_database_config():
    """Test database configuration"""
    return {
        'host': os.getenv('TEST_DB_HOST', 'localhost'),
        'port': os.getenv('TEST_DB_PORT', '5432'),
        'database': os.getenv('TEST_DB_NAME', 'test_ong_management'),
        'user': os.getenv('TEST_DB_USER', 'test_user'),
        'password': os.getenv('TEST_DB_PASSWORD', 'test_pass')
    }


@pytest.fixture
def test_database_connection(test_database_config):
    """Test database connection"""
    try:
        conn = psycopg2.connect(**test_database_config)
        conn.autocommit = True
        yield conn
        conn.close()
    except Exception as e:
        pytest.skip(f"Test database not available: {e}")


@pytest.fixture
def setup_test_database(test_database_connection):
    """Setup test database schema"""
    cursor = test_database_connection.cursor()
    
    try:
        # Create test tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitudes_externas (
                id SERIAL PRIMARY KEY,
                organizacion_solicitante VARCHAR(100) NOT NULL,
                solicitud_id VARCHAR(100) NOT NULL,
                donaciones JSONB NOT NULL,
                activa BOOLEAN DEFAULT true,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organizacion_solicitante, solicitud_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ofertas_externas (
                id SERIAL PRIMARY KEY,
                organizacion_donante VARCHAR(100) NOT NULL,
                oferta_id VARCHAR(100) NOT NULL,
                donaciones JSONB NOT NULL,
                activa BOOLEAN DEFAULT true,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organizacion_donante, oferta_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventos_externos (
                id SERIAL PRIMARY KEY,
                organizacion_id VARCHAR(100) NOT NULL,
                evento_id VARCHAR(100) NOT NULL,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                fecha_evento TIMESTAMP NOT NULL,
                activo BOOLEAN DEFAULT true,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(organizacion_id, evento_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transferencias_donaciones (
                id SERIAL PRIMARY KEY,
                tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('ENVIADA', 'RECIBIDA')),
                organizacion_contraparte VARCHAR(100) NOT NULL,
                solicitud_id VARCHAR(100),
                donaciones JSONB NOT NULL,
                fecha_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adhesiones_eventos_externos (
                id SERIAL PRIMARY KEY,
                evento_externo_id INTEGER REFERENCES eventos_externos(id),
                voluntario_id INTEGER,
                organizacion_voluntario VARCHAR(100),
                nombre_voluntario VARCHAR(100),
                apellido_voluntario VARCHAR(100),
                telefono_voluntario VARCHAR(20),
                email_voluntario VARCHAR(100),
                fecha_adhesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado VARCHAR(20) DEFAULT 'PENDIENTE'
            )
        """)
        
        yield cursor
        
        # Cleanup test data
        cursor.execute("DELETE FROM adhesiones_eventos_externos")
        cursor.execute("DELETE FROM transferencias_donaciones")
        cursor.execute("DELETE FROM eventos_externos")
        cursor.execute("DELETE FROM ofertas_externas")
        cursor.execute("DELETE FROM solicitudes_externas")
        
    except Exception as e:
        pytest.skip(f"Failed to setup test database: {e}")


@pytest.fixture
def mock_integration_settings():
    """Mock settings for integration tests"""
    settings = Mock()
    settings.organization_id = "test-org"
    settings.kafka_brokers = "localhost:9093"
    settings.kafka_group_id = "test-messaging-group"
    settings.database_url = "postgresql://test_user:test_pass@localhost:5432/test_ong_management"
    return settings


@pytest.fixture
def integration_test_data():
    """Common test data for integration tests"""
    return {
        'donation_request': {
            "organization_id": "external-org",
            "request_id": "REQ-INT-001",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates"
                },
                {
                    "category": "ROPA",
                    "description": "Camisetas talla M"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        },
        'donation_offer': {
            "offer_id": "OFFER-INT-001",
            "donor_organization": "external-org",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates",
                    "quantity": "5kg"
                }
            ],
            "timestamp": "2024-01-15T11:00:00Z"
        },
        'donation_transfer': {
            "request_id": "REQ-INT-001",
            "donor_organization": "external-org",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates",
                    "quantity": "2kg"
                }
            ],
            "timestamp": "2024-01-15T11:30:00Z"
        },
        'solidarity_event': {
            "organization_id": "external-org",
            "event_id": "EVENT-INT-001",
            "name": "Campaña de Donación",
            "description": "Recolección de alimentos para familias necesitadas",
            "event_date": "2024-02-15T09:00:00Z",
            "timestamp": "2024-01-15T12:00:00Z"
        },
        'event_adhesion': {
            "event_id": "EVENT-INT-001",
            "volunteer": {
                "organization_id": "external-org",
                "volunteer_id": "VOL-INT-001",
                "name": "Juan",
                "surname": "Pérez",
                "phone": "+1234567890",
                "email": "juan.perez@example.com"
            },
            "timestamp": "2024-01-15T12:30:00Z"
        }
    }


import json


class IntegrationTestHelper:
    """Helper class for integration tests"""
    
    @staticmethod
    def create_message_envelope(message_type, organization_id, data):
        """Create a message envelope for testing"""
        return {
            "message_id": f"test-msg-{int(time.time())}",
            "message_type": message_type,
            "organization_id": organization_id,
            "timestamp": "2024-01-15T10:30:00Z",
            "data": data
        }
    
    @staticmethod
    def wait_for_message_processing(timeout=10):
        """Wait for message processing to complete"""
        time.sleep(min(timeout, 2))  # Wait up to 2 seconds for processing
    
    @staticmethod
    def verify_database_record(cursor, table, conditions):
        """Verify a record exists in the database"""
        where_clause = " AND ".join([f"{k} = %s" for k in conditions.keys()])
        query = f"SELECT COUNT(*) FROM {table} WHERE {where_clause}"
        cursor.execute(query, list(conditions.values()))
        return cursor.fetchone()[0] > 0


@pytest.fixture
def integration_helper():
    """Integration test helper"""
    return IntegrationTestHelper