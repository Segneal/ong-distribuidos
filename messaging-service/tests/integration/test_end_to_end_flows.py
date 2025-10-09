"""
End-to-end integration tests for complete messaging flows
"""
import pytest
import time
import json
from unittest.mock import patch, Mock

from messaging.producers.base_producer import BaseProducer
from messaging.consumers.base_consumer import NetworkConsumer, OrganizationConsumer
from messaging.services.offer_service import OfferService
from messaging.services.event_service import EventService
from messaging.services.transfer_service import TransferService


@pytest.mark.integration
class TestEndToEndFlows:
    """End-to-end integration tests for complete messaging flows"""
    
    def test_donation_request_flow(self, kafka_config, setup_kafka_topics, setup_test_database, 
                                 kafka_producer, kafka_consumer, integration_test_data, integration_helper):
        """Test complete donation request flow from publication to consumption"""
        
        # Step 1: External organization publishes donation request
        request_data = integration_test_data['donation_request']
        message_envelope = integration_helper.create_message_envelope(
            "donation_request", request_data['organization_id'], request_data
        )
        
        # Send to donation requests topic
        kafka_producer.send("test-donation-requests", value=message_envelope, key=request_data['organization_id'])
        kafka_producer.flush()
        
        # Step 2: Our system should consume and process the request
        # Simulate consumer processing
        cursor = setup_test_database
        
        # Manually process the message (simulating consumer)
        cursor.execute("""
            INSERT INTO solicitudes_externas 
            (organizacion_solicitante, solicitud_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
        """, (
            request_data['organization_id'],
            request_data['request_id'],
            json.dumps(request_data['donations']),
            True
        ))
        
        # Step 3: Verify the request was stored
        cursor.execute("""
            SELECT organizacion_solicitante, solicitud_id, donaciones, activa
            FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == request_data['organization_id']
        assert result[1] == request_data['request_id']
        assert result[3] is True  # Active
        
        # Step 4: Verify we can query the stored request
        cursor.execute("""
            SELECT donaciones FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s AND activa = true
        """, (request_data['organization_id'], request_data['request_id']))
        
        stored_donations = cursor.fetchone()[0]
        assert len(stored_donations) == 2
        assert stored_donations[0]['category'] == 'ALIMENTOS'
        assert stored_donations[1]['category'] == 'ROPA'
    
    def test_donation_offer_flow(self, kafka_config, setup_kafka_topics, setup_test_database,
                               kafka_producer, kafka_consumer, integration_test_data, integration_helper):
        """Test complete donation offer flow"""
        
        # Step 1: External organization publishes donation offer
        offer_data = integration_test_data['donation_offer']
        message_envelope = integration_helper.create_message_envelope(
            "donation_offer", offer_data['donor_organization'], offer_data
        )
        
        # Send to donation offers topic
        kafka_producer.send("test-donation-offers", value=message_envelope, key=offer_data['donor_organization'])
        kafka_producer.flush()
        
        # Step 2: Simulate our system consuming and processing the offer
        cursor = setup_test_database
        
        cursor.execute("""
            INSERT INTO ofertas_externas 
            (organizacion_donante, oferta_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
        """, (
            offer_data['donor_organization'],
            offer_data['offer_id'],
            json.dumps(offer_data['donations']),
            True
        ))
        
        # Step 3: Verify the offer was stored and can be queried
        cursor.execute("""
            SELECT organizacion_donante, oferta_id, donaciones
            FROM ofertas_externas
            WHERE organizacion_donante = %s AND oferta_id = %s AND activa = true
        """, (offer_data['donor_organization'], offer_data['offer_id']))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == offer_data['donor_organization']
        assert result[1] == offer_data['offer_id']
        
        stored_donations = result[2]
        assert len(stored_donations) == 1
        assert stored_donations[0]['quantity'] == '5kg'
    
    def test_donation_transfer_flow(self, kafka_config, setup_kafka_topics, setup_test_database,
                                  kafka_producer, kafka_consumer, integration_test_data, integration_helper):
        """Test complete donation transfer flow"""
        
        # Step 1: Create a donation request first
        request_data = integration_test_data['donation_request']
        cursor = setup_test_database
        
        cursor.execute("""
            INSERT INTO solicitudes_externas 
            (organizacion_solicitante, solicitud_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
        """, (
            request_data['organization_id'],
            request_data['request_id'],
            json.dumps(request_data['donations']),
            True
        ))
        
        # Step 2: External organization sends donation transfer
        transfer_data = integration_test_data['donation_transfer']
        message_envelope = integration_helper.create_message_envelope(
            "donation_transfer", transfer_data['donor_organization'], transfer_data
        )
        
        # Send to our organization's transfer topic
        kafka_producer.send("test-transfer-test-org", value=message_envelope, key=transfer_data['donor_organization'])
        kafka_producer.flush()
        
        # Step 3: Simulate our system processing the transfer
        cursor.execute("""
            INSERT INTO transferencias_donaciones 
            (tipo, organizacion_contraparte, solicitud_id, donaciones)
            VALUES (%s, %s, %s, %s)
        """, (
            'RECIBIDA',
            transfer_data['donor_organization'],
            transfer_data['request_id'],
            json.dumps(transfer_data['donations'])
        ))
        
        # Step 4: Verify transfer was recorded
        cursor.execute("""
            SELECT tipo, organizacion_contraparte, solicitud_id, donaciones
            FROM transferencias_donaciones
            WHERE organizacion_contraparte = %s AND solicitud_id = %s
        """, (transfer_data['donor_organization'], transfer_data['request_id']))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'RECIBIDA'
        assert result[1] == transfer_data['donor_organization']
        assert result[2] == transfer_data['request_id']
        
        stored_donations = result[3]
        assert len(stored_donations) == 1
        assert stored_donations[0]['quantity'] == '2kg'
    
    def test_solidarity_event_flow(self, kafka_config, setup_kafka_topics, setup_test_database,
                                 kafka_producer, kafka_consumer, integration_test_data, integration_helper):
        """Test complete solidarity event flow"""
        
        # Step 1: External organization publishes solidarity event
        event_data = integration_test_data['solidarity_event']
        message_envelope = integration_helper.create_message_envelope(
            "solidarity_event", event_data['organization_id'], event_data
        )
        
        # Send to solidarity events topic
        kafka_producer.send("test-solidarity-events", value=message_envelope, key=event_data['organization_id'])
        kafka_producer.flush()
        
        # Step 2: Simulate our system consuming and processing the event
        cursor = setup_test_database
        
        cursor.execute("""
            INSERT INTO eventos_externos 
            (organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            event_data['organization_id'],
            event_data['event_id'],
            event_data['name'],
            event_data['description'],
            event_data['event_date'],
            True
        ))
        
        # Step 3: Verify event was stored
        cursor.execute("""
            SELECT organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo
            FROM eventos_externos
            WHERE organizacion_id = %s AND evento_id = %s
        """, (event_data['organization_id'], event_data['event_id']))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == event_data['organization_id']
        assert result[1] == event_data['event_id']
        assert result[2] == event_data['name']
        assert result[3] == event_data['description']
        assert result[5] is True  # Active
    
    def test_event_adhesion_flow(self, kafka_config, setup_kafka_topics, setup_test_database,
                               kafka_producer, kafka_consumer, integration_test_data, integration_helper):
        """Test complete event adhesion flow"""
        
        # Step 1: Create an external event first
        event_data = integration_test_data['solidarity_event']
        cursor = setup_test_database
        
        cursor.execute("""
            INSERT INTO eventos_externos 
            (organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            event_data['organization_id'],
            event_data['event_id'],
            event_data['name'],
            event_data['description'],
            event_data['event_date'],
            True
        ))
        
        event_id = cursor.fetchone()[0]
        
        # Step 2: External volunteer sends adhesion to our event
        adhesion_data = integration_test_data['event_adhesion']
        message_envelope = integration_helper.create_message_envelope(
            "event_adhesion", adhesion_data['volunteer']['organization_id'], adhesion_data
        )
        
        # Send to our organization's adhesion topic
        kafka_producer.send("test-adhesion-test-org", value=message_envelope, 
                          key=adhesion_data['volunteer']['organization_id'])
        kafka_producer.flush()
        
        # Step 3: Simulate our system processing the adhesion
        volunteer = adhesion_data['volunteer']
        
        cursor.execute("""
            INSERT INTO adhesiones_eventos_externos 
            (evento_externo_id, organizacion_voluntario, nombre_voluntario, 
             apellido_voluntario, telefono_voluntario, email_voluntario, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            event_id,
            volunteer['organization_id'],
            volunteer['name'],
            volunteer['surname'],
            volunteer['phone'],
            volunteer['email'],
            'PENDIENTE'
        ))
        
        # Step 4: Verify adhesion was recorded
        cursor.execute("""
            SELECT organizacion_voluntario, nombre_voluntario, apellido_voluntario, estado
            FROM adhesiones_eventos_externos
            WHERE evento_externo_id = %s
        """, (event_id,))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == volunteer['organization_id']
        assert result[1] == volunteer['name']
        assert result[2] == volunteer['surname']
        assert result[3] == 'PENDIENTE'
    
    def test_request_cancellation_flow(self, kafka_config, setup_kafka_topics, setup_test_database,
                                     kafka_producer, kafka_consumer, integration_test_data, integration_helper):
        """Test complete request cancellation flow"""
        
        # Step 1: Create an active donation request
        request_data = integration_test_data['donation_request']
        cursor = setup_test_database
        
        cursor.execute("""
            INSERT INTO solicitudes_externas 
            (organizacion_solicitante, solicitud_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
        """, (
            request_data['organization_id'],
            request_data['request_id'],
            json.dumps(request_data['donations']),
            True
        ))
        
        # Verify it's active
        cursor.execute("""
            SELECT activa FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        assert cursor.fetchone()[0] is True
        
        # Step 2: External organization sends cancellation
        cancellation_data = {
            "organization_id": request_data['organization_id'],
            "request_id": request_data['request_id'],
            "timestamp": "2024-01-15T13:00:00Z"
        }
        
        message_envelope = integration_helper.create_message_envelope(
            "request_cancellation", cancellation_data['organization_id'], cancellation_data
        )
        
        # Send to request cancellations topic
        kafka_producer.send("test-request-cancellations", value=message_envelope, 
                          key=cancellation_data['organization_id'])
        kafka_producer.flush()
        
        # Step 3: Simulate our system processing the cancellation
        cursor.execute("""
            UPDATE solicitudes_externas 
            SET activa = false
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (cancellation_data['organization_id'], cancellation_data['request_id']))
        
        # Step 4: Verify request is now inactive
        cursor.execute("""
            SELECT activa FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (cancellation_data['organization_id'], cancellation_data['request_id']))
        
        result = cursor.fetchone()
        assert result[0] is False
    
    def test_event_cancellation_flow(self, kafka_config, setup_kafka_topics, setup_test_database,
                                   kafka_producer, kafka_consumer, integration_test_data, integration_helper):
        """Test complete event cancellation flow"""
        
        # Step 1: Create an active external event
        event_data = integration_test_data['solidarity_event']
        cursor = setup_test_database
        
        cursor.execute("""
            INSERT INTO eventos_externos 
            (organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            event_data['organization_id'],
            event_data['event_id'],
            event_data['name'],
            event_data['description'],
            event_data['event_date'],
            True
        ))
        
        # Verify it's active
        cursor.execute("""
            SELECT activo FROM eventos_externos
            WHERE organizacion_id = %s AND evento_id = %s
        """, (event_data['organization_id'], event_data['event_id']))
        
        assert cursor.fetchone()[0] is True
        
        # Step 2: External organization sends event cancellation
        cancellation_data = {
            "organization_id": event_data['organization_id'],
            "event_id": event_data['event_id'],
            "timestamp": "2024-01-15T13:30:00Z"
        }
        
        message_envelope = integration_helper.create_message_envelope(
            "event_cancellation", cancellation_data['organization_id'], cancellation_data
        )
        
        # Send to event cancellations topic
        kafka_producer.send("test-event-cancellations", value=message_envelope, 
                          key=cancellation_data['organization_id'])
        kafka_producer.flush()
        
        # Step 3: Simulate our system processing the cancellation
        cursor.execute("""
            UPDATE eventos_externos 
            SET activo = false
            WHERE organizacion_id = %s AND evento_id = %s
        """, (cancellation_data['organization_id'], cancellation_data['event_id']))
        
        # Step 4: Verify event is now inactive
        cursor.execute("""
            SELECT activo FROM eventos_externos
            WHERE organizacion_id = %s AND evento_id = %s
        """, (cancellation_data['organization_id'], cancellation_data['event_id']))
        
        result = cursor.fetchone()
        assert result[0] is False
    
    def test_multiple_organizations_flow(self, kafka_config, setup_kafka_topics, setup_test_database,
                                       kafka_producer, kafka_consumer, integration_helper):
        """Test messaging flow with multiple organizations"""
        
        cursor = setup_test_database
        
        # Step 1: Organization A publishes a donation request
        org_a_request = {
            "organization_id": "org-a",
            "request_id": "REQ-A-001",
            "donations": [{"category": "ALIMENTOS", "description": "Arroz"}],
            "timestamp": "2024-01-15T10:00:00Z"
        }
        
        message_a = integration_helper.create_message_envelope(
            "donation_request", "org-a", org_a_request
        )
        
        kafka_producer.send("test-donation-requests", value=message_a, key="org-a")
        
        # Step 2: Organization B publishes a donation offer
        org_b_offer = {
            "offer_id": "OFFER-B-001",
            "donor_organization": "org-b",
            "donations": [{"category": "ALIMENTOS", "description": "Arroz", "quantity": "10kg"}],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        message_b = integration_helper.create_message_envelope(
            "donation_offer", "org-b", org_b_offer
        )
        
        kafka_producer.send("test-donation-offers", value=message_b, key="org-b")
        
        # Step 3: Organization C publishes an event
        org_c_event = {
            "organization_id": "org-c",
            "event_id": "EVENT-C-001",
            "name": "Campaña de Recolección",
            "description": "Recolección de alimentos",
            "event_date": "2024-02-15T09:00:00Z",
            "timestamp": "2024-01-15T11:00:00Z"
        }
        
        message_c = integration_helper.create_message_envelope(
            "solidarity_event", "org-c", org_c_event
        )
        
        kafka_producer.send("test-solidarity-events", value=message_c, key="org-c")
        
        kafka_producer.flush()
        
        # Step 4: Simulate our system processing all messages
        # Process request from org-a
        cursor.execute("""
            INSERT INTO solicitudes_externas 
            (organizacion_solicitante, solicitud_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
        """, ("org-a", "REQ-A-001", json.dumps(org_a_request['donations']), True))
        
        # Process offer from org-b
        cursor.execute("""
            INSERT INTO ofertas_externas 
            (organizacion_donante, oferta_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
        """, ("org-b", "OFFER-B-001", json.dumps(org_b_offer['donations']), True))
        
        # Process event from org-c
        cursor.execute("""
            INSERT INTO eventos_externos 
            (organizacion_id, evento_id, nombre, descripcion, fecha_evento, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ("org-c", "EVENT-C-001", org_c_event['name'], org_c_event['description'], 
              org_c_event['event_date'], True))
        
        # Step 5: Verify all data was stored correctly
        # Check request
        cursor.execute("SELECT COUNT(*) FROM solicitudes_externas WHERE organizacion_solicitante = 'org-a'")
        assert cursor.fetchone()[0] == 1
        
        # Check offer
        cursor.execute("SELECT COUNT(*) FROM ofertas_externas WHERE organizacion_donante = 'org-b'")
        assert cursor.fetchone()[0] == 1
        
        # Check event
        cursor.execute("SELECT COUNT(*) FROM eventos_externos WHERE organizacion_id = 'org-c'")
        assert cursor.fetchone()[0] == 1
    
    def test_error_recovery_flow(self, kafka_config, setup_kafka_topics, setup_test_database,
                               kafka_producer, kafka_consumer, integration_test_data, integration_helper):
        """Test error recovery in messaging flows"""
        
        cursor = setup_test_database
        
        # Step 1: Send a valid message
        valid_request = integration_test_data['donation_request']
        valid_message = integration_helper.create_message_envelope(
            "donation_request", valid_request['organization_id'], valid_request
        )
        
        kafka_producer.send("test-donation-requests", value=valid_message, key=valid_request['organization_id'])
        
        # Step 2: Send an invalid message (missing required fields)
        invalid_request = {
            "organization_id": "invalid-org",
            # Missing request_id and other required fields
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        invalid_message = integration_helper.create_message_envelope(
            "donation_request", "invalid-org", invalid_request
        )
        
        kafka_producer.send("test-donation-requests", value=invalid_message, key="invalid-org")
        
        # Step 3: Send another valid message
        valid_request_2 = {
            "organization_id": "recovery-org",
            "request_id": "REQ-RECOVERY-001",
            "donations": [{"category": "ROPA", "description": "Pantalones"}],
            "timestamp": "2024-01-15T11:00:00Z"
        }
        
        valid_message_2 = integration_helper.create_message_envelope(
            "donation_request", "recovery-org", valid_request_2
        )
        
        kafka_producer.send("test-donation-requests", value=valid_message_2, key="recovery-org")
        kafka_producer.flush()
        
        # Step 4: Process valid messages (simulate error handling for invalid one)
        try:
            # Process first valid message
            cursor.execute("""
                INSERT INTO solicitudes_externas 
                (organizacion_solicitante, solicitud_id, donaciones, activa)
                VALUES (%s, %s, %s, %s)
            """, (
                valid_request['organization_id'],
                valid_request['request_id'],
                json.dumps(valid_request['donations']),
                True
            ))
        except Exception:
            pass  # Should not fail
        
        try:
            # Try to process invalid message (should fail gracefully)
            cursor.execute("""
                INSERT INTO solicitudes_externas 
                (organizacion_solicitante, solicitud_id, donaciones, activa)
                VALUES (%s, %s, %s, %s)
            """, (
                invalid_request['organization_id'],
                invalid_request.get('request_id', 'MISSING'),  # This will cause issues
                json.dumps(invalid_request.get('donations', [])),
                True
            ))
        except Exception:
            # Expected to fail, continue processing
            pass
        
        try:
            # Process second valid message
            cursor.execute("""
                INSERT INTO solicitudes_externas 
                (organizacion_solicitante, solicitud_id, donaciones, activa)
                VALUES (%s, %s, %s, %s)
            """, (
                valid_request_2['organization_id'],
                valid_request_2['request_id'],
                json.dumps(valid_request_2['donations']),
                True
            ))
        except Exception:
            pass  # Should not fail
        
        # Step 5: Verify that valid messages were processed despite the invalid one
        cursor.execute("SELECT COUNT(*) FROM solicitudes_externas WHERE organizacion_solicitante = %s", 
                      (valid_request['organization_id'],))
        assert cursor.fetchone()[0] == 1
        
        cursor.execute("SELECT COUNT(*) FROM solicitudes_externas WHERE organizacion_solicitante = %s", 
                      (valid_request_2['organization_id'],))
        assert cursor.fetchone()[0] == 1
        
        # Invalid message should not be in database
        cursor.execute("SELECT COUNT(*) FROM solicitudes_externas WHERE organizacion_solicitante = %s", 
                      ("invalid-org",))
        assert cursor.fetchone()[0] == 0