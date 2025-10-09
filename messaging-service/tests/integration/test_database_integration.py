"""
Integration tests for database synchronization
"""
import pytest
import json
import time
from unittest.mock import patch, Mock

# Database connection will be handled through fixtures
from messaging.services.offer_service import OfferService
from messaging.services.event_service import EventService
from messaging.services.transfer_service import TransferService


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_database_connection(self, test_database_connection):
        """Test basic database connection"""
        cursor = test_database_connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
    
    def test_external_request_storage(self, setup_test_database, integration_test_data, integration_helper):
        """Test storing external donation requests in database"""
        cursor = setup_test_database
        
        # Simulate processing an external donation request
        request_data = integration_test_data['donation_request']
        
        # Insert external request
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
        
        # Verify insertion
        cursor.execute("""
            SELECT organizacion_solicitante, solicitud_id, donaciones, activa
            FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == request_data['organization_id']
        assert result[1] == request_data['request_id']
        assert result[3] is True  # activa
        
        # Verify donations data
        stored_donations = result[2]
        assert len(stored_donations) == len(request_data['donations'])
        assert stored_donations[0]['category'] == 'ALIMENTOS'
    
    def test_external_offer_storage(self, setup_test_database, integration_test_data):
        """Test storing external donation offers in database"""
        cursor = setup_test_database
        
        # Simulate processing an external donation offer
        offer_data = integration_test_data['donation_offer']
        
        # Insert external offer
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
        
        # Verify insertion
        cursor.execute("""
            SELECT organizacion_donante, oferta_id, donaciones, activa
            FROM ofertas_externas
            WHERE organizacion_donante = %s AND oferta_id = %s
        """, (offer_data['donor_organization'], offer_data['offer_id']))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == offer_data['donor_organization']
        assert result[1] == offer_data['offer_id']
        assert result[3] is True  # activa
        
        # Verify donations data
        stored_donations = result[2]
        assert len(stored_donations) == len(offer_data['donations'])
        assert stored_donations[0]['quantity'] == '5kg'
    
    def test_external_event_storage(self, setup_test_database, integration_test_data):
        """Test storing external solidarity events in database"""
        cursor = setup_test_database
        
        # Simulate processing an external solidarity event
        event_data = integration_test_data['solidarity_event']
        
        # Insert external event
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
        
        # Verify insertion
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
        assert result[5] is True  # activo
    
    def test_transfer_history_storage(self, setup_test_database, integration_test_data):
        """Test storing donation transfer history in database"""
        cursor = setup_test_database
        
        # Simulate processing a donation transfer
        transfer_data = integration_test_data['donation_transfer']
        
        # Insert transfer record
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
        
        # Verify insertion
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
        
        # Verify donations data
        stored_donations = result[3]
        assert len(stored_donations) == len(transfer_data['donations'])
        assert stored_donations[0]['quantity'] == '2kg'
    
    def test_event_adhesion_storage(self, setup_test_database, integration_test_data):
        """Test storing event adhesions in database"""
        cursor = setup_test_database
        
        # First create an external event
        event_data = integration_test_data['solidarity_event']
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
        
        # Now create an adhesion
        adhesion_data = integration_test_data['event_adhesion']
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
        
        # Verify insertion
        cursor.execute("""
            SELECT organizacion_voluntario, nombre_voluntario, apellido_voluntario, 
                   telefono_voluntario, email_voluntario, estado
            FROM adhesiones_eventos_externos
            WHERE evento_externo_id = %s
        """, (event_id,))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == volunteer['organization_id']
        assert result[1] == volunteer['name']
        assert result[2] == volunteer['surname']
        assert result[3] == volunteer['phone']
        assert result[4] == volunteer['email']
        assert result[5] == 'PENDIENTE'
    
    def test_request_cancellation_update(self, setup_test_database, integration_test_data):
        """Test updating request status on cancellation"""
        cursor = setup_test_database
        
        # First create an external request
        request_data = integration_test_data['donation_request']
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
        
        result = cursor.fetchone()
        assert result[0] is True
        
        # Now simulate cancellation
        cursor.execute("""
            UPDATE solicitudes_externas 
            SET activa = false
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        # Verify it's now inactive
        cursor.execute("""
            SELECT activa FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        result = cursor.fetchone()
        assert result[0] is False
    
    def test_event_cancellation_update(self, setup_test_database, integration_test_data):
        """Test updating event status on cancellation"""
        cursor = setup_test_database
        
        # First create an external event
        event_data = integration_test_data['solidarity_event']
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
        
        result = cursor.fetchone()
        assert result[0] is True
        
        # Now simulate cancellation
        cursor.execute("""
            UPDATE eventos_externos 
            SET activo = false
            WHERE organizacion_id = %s AND evento_id = %s
        """, (event_data['organization_id'], event_data['event_id']))
        
        # Verify it's now inactive
        cursor.execute("""
            SELECT activo FROM eventos_externos
            WHERE organizacion_id = %s AND evento_id = %s
        """, (event_data['organization_id'], event_data['event_id']))
        
        result = cursor.fetchone()
        assert result[0] is False
    
    def test_database_transaction_rollback(self, setup_test_database, integration_test_data):
        """Test database transaction rollback on error"""
        cursor = setup_test_database
        connection = cursor.connection
        
        request_data = integration_test_data['donation_request']
        
        try:
            # Start transaction
            connection.autocommit = False
            
            # Insert valid record
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
            
            # Try to insert duplicate (should fail due to unique constraint)
            cursor.execute("""
                INSERT INTO solicitudes_externas 
                (organizacion_solicitante, solicitud_id, donaciones, activa)
                VALUES (%s, %s, %s, %s)
            """, (
                request_data['organization_id'],
                request_data['request_id'],  # Same ID, should fail
                json.dumps(request_data['donations']),
                True
            ))
            
            # This should not be reached
            connection.commit()
            pytest.fail("Expected duplicate key error")
            
        except Exception:
            # Rollback transaction
            connection.rollback()
        
        finally:
            connection.autocommit = True
        
        # Verify no records were inserted due to rollback
        cursor.execute("""
            SELECT COUNT(*) FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        count = cursor.fetchone()[0]
        assert count == 0
    
    def test_concurrent_database_access(self, setup_test_database, integration_test_data):
        """Test concurrent database access scenarios"""
        cursor = setup_test_database
        
        # Simulate concurrent insertions
        request_data = integration_test_data['donation_request']
        
        # Insert first record
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
        
        # Try to update the same record
        cursor.execute("""
            UPDATE solicitudes_externas 
            SET activa = false
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        # Verify update was successful
        cursor.execute("""
            SELECT activa FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        result = cursor.fetchone()
        assert result[0] is False
    
    @patch('messaging.database.connection.get_database_connection')
    def test_database_connection_error_handling(self, mock_db_connection):
        """Test database connection error handling"""
        # Mock database connection failure
        mock_db_connection.side_effect = Exception("Connection failed")
        
        # Test that services handle database errors gracefully
        try:
            service = OfferService()
            # This should handle the database error gracefully
            result = service.process_external_offer({
                "offer_id": "TEST-001",
                "donor_organization": "test-org",
                "donations": [],
                "timestamp": "2024-01-15T10:30:00Z"
            })
            # Should return False on database error
            assert result is False
        except Exception:
            # Services should handle database errors, not propagate them
            pytest.fail("Service should handle database errors gracefully")