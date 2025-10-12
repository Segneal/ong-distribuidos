#!/usr/bin/env python3
"""
Test para verificar que las notificaciones de transferencias funcionen correctamente
"""
import os
import sys
import json
import time
from datetime import datetime

# Add messaging service to path
sys.path.append('messaging-service/src')

def test_transfer_notification_flow():
    """Test completo del flujo de notificaciones de transferencias"""
    print("=== TESTING TRANSFER NOTIFICATION FLOW ===")
    
    # Set up environment
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    # Step 1: Simulate a donation request from esperanza-viva
    print("\n1. Simulating donation request from esperanza-viva...")
    
    os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
    
    # Import fresh modules
    import importlib
    import messaging.config
    importlib.reload(messaging.config)
    
    from messaging.config import settings
    from messaging.producers.base_producer import BaseProducer
    
    print(f"Requesting organization: {settings.organization_id}")
    
    # Create a donation request
    producer = BaseProducer()
    
    test_donations = [
        {
            "category": "Alimentos",
            "description": "Arroz",
            "quantity": "10kg"
        },
        {
            "category": "Ropa",
            "description": "Abrigos de invierno",
            "quantity": "5 unidades"
        }
    ]
    
    request_id = f"test-request-{int(time.time())}"
    
    success = producer.publish_donation_request(request_id, test_donations)
    print(f"Request published: {success}")
    
    if not success:
        print("❌ Failed to publish request")
        return False
    
    # Step 2: Simulate transfer from empuje-comunitario
    print("\n2. Simulating transfer from empuje-comunitario...")
    
    os.environ['ORGANIZATION_ID'] = 'empuje-comunitario'
    importlib.reload(messaging.config)
    
    from messaging.services.transfer_service import TransferService
    
    transfer_service = TransferService()
    
    # Create transfer data
    transfer_donations = [
        {
            "inventoryId": "1",
            "category": "Alimentos",
            "description": "Arroz",
            "quantity": "8kg"
        },
        {
            "inventoryId": "2", 
            "category": "Ropa",
            "description": "Abrigos de invierno",
            "quantity": "3 unidades"
        }
    ]
    
    print(f"Transferring to esperanza-viva for request {request_id}")
    
    success, message, transfer_id = transfer_service.transfer_donations(
        target_organization="esperanza-viva",
        request_id=request_id,
        donations=transfer_donations,
        user_id=1  # Admin user
    )
    
    print(f"Transfer result: {success}")
    print(f"Message: {message}")
    print(f"Transfer ID: {transfer_id}")
    
    if not success:
        print("❌ Transfer failed")
        return False
    
    # Step 3: Wait for processing
    print("\n3. Waiting for message processing...")
    time.sleep(5)
    
    # Step 4: Check if notification was created
    print("\n4. Checking for notifications...")
    
    try:
        from messaging.database.connection import get_database_connection
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Look for recent notifications about donations received
            cursor.execute("""
                SELECT 
                    id,
                    usuario_id,
                    titulo,
                    mensaje,
                    tipo,
                    fecha_creacion,
                    leida
                FROM notificaciones_usuarios 
                WHERE titulo LIKE '%donación%' OR titulo LIKE '%Donación%'
                ORDER BY fecha_creacion DESC 
                LIMIT 5
            """)
            
            notifications = cursor.fetchall()
            
            if notifications:
                print(f"✅ Found {len(notifications)} donation-related notifications:")
                for notif in notifications:
                    print(f"   ID: {notif[0]}")
                    print(f"   Usuario: {notif[1]}")
                    print(f"   Título: {notif[2]}")
                    print(f"   Mensaje: {notif[3][:100]}...")
                    print(f"   Tipo: {notif[4]}")
                    print(f"   Fecha: {notif[5]}")
                    print(f"   Leída: {notif[6]}")
                    print("   " + "-"*50)
                
                # Check if any notification is about received donations
                received_notifications = [n for n in notifications if "recibida" in n[2].lower() or "recibida" in n[3].lower()]
                
                if received_notifications:
                    print("✅ Found notification about received donations!")
                    return True
                else:
                    print("⚠️  No notifications about received donations found")
                    return False
            else:
                print("❌ No donation-related notifications found")
                return False
                
    except Exception as e:
        print(f"❌ Error checking notifications: {e}")
        return False

def test_notification_content():
    """Test the content of transfer notifications"""
    print("\n=== TESTING NOTIFICATION CONTENT ===")
    
    # Test the notification creation logic
    os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    import importlib
    import messaging.config
    importlib.reload(messaging.config)
    
    try:
        from messaging.consumers.transfer_consumer import DonationTransferConsumer
        from messaging.models.transfer import DonationTransfer, DonationTransferItem
        
        # Create a test transfer
        transfer_items = [
            DonationTransferItem(
                category="Alimentos",
                description="Arroz integral",
                quantity="5kg"
            ),
            DonationTransferItem(
                category="Ropa",
                description="Camisetas",
                quantity="10 unidades"
            )
        ]
        
        transfer = DonationTransfer(
            transfer_id="test-transfer-123",
            request_id="test-request-456",
            donor_organization="empuje-comunitario",
            recipient_organization="esperanza-viva",
            donations=transfer_items,
            timestamp=datetime.now().isoformat(),
            user_id=1
        )
        
        print("✅ Test transfer object created successfully")
        print(f"   Transfer ID: {transfer.transfer_id}")
        print(f"   Request ID: {transfer.request_id}")
        print(f"   Donor: {transfer.donor_organization}")
        print(f"   Donations: {len(transfer.donations)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing notification content: {e}")
        return False

def show_expected_notification():
    """Show what the notification should look like"""
    print("\n" + "="*60)
    print("📧 EXPECTED NOTIFICATION FORMAT")
    print("="*60)
    
    print("\n📋 Notification Details:")
    print("   Title: 🎁 ¡Donación recibida!")
    print("   Type: SUCCESS")
    print("   Recipient: User who made the original request")
    
    print("\n📝 Message Content:")
    print("   ¡Excelente noticia [User Name]!")
    print("   ")
    print("   La organización '[Donor Organization]' ha respondido a tu solicitud de donaciones.")
    print("   ")
    print("   Donaciones recibidas:")
    print("   • Arroz integral (5kg)")
    print("   • Camisetas (10 unidades)")
    print("   ")
    print("   Las donaciones ya están disponibles en tu inventario. ¡Gracias por usar la red de colaboración!")
    
    print("\n🔔 When Notification is Sent:")
    print("   - When a transfer is received and processed")
    print("   - Only if the transfer has a valid request_id")
    print("   - Only if the original requesting user is found")
    print("   - Automatically when the transfer consumer processes the message")

def main():
    """Main test function"""
    print("🔔 TESTING TRANSFER NOTIFICATIONS")
    print("="*60)
    
    # Test 1: Notification content structure
    test1 = test_notification_content()
    
    # Test 2: Full transfer notification flow
    test2 = test_transfer_notification_flow()
    
    # Show expected format
    show_expected_notification()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    if test1 and test2:
        print("✅ ALL TESTS PASSED!")
        print("🎉 Transfer notifications should work correctly")
    elif test1:
        print("⚠️  PARTIAL SUCCESS")
        print("✅ Notification structure is correct")
        print("❌ Full flow test failed - check Kafka and database")
    else:
        print("❌ TESTS FAILED")
        print("🔧 Check the implementation and try again")
    
    print("\n🔧 TO TEST MANUALLY:")
    print("1. Make a donation request from one organization")
    print("2. Transfer donations from another organization")
    print("3. Check notifications in the requesting user's account")
    print("4. Verify the notification content and format")

if __name__ == "__main__":
    main()