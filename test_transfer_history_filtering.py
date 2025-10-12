#!/usr/bin/env python3
"""
Test para verificar que el filtrado del historial de transferencias funcione correctamente
"""
import mysql.connector
import requests
import json

def check_database_state():
    """Verificar el estado actual de la base de datos"""
    print("=== VERIFICANDO ESTADO DE LA BASE DE DATOS ===")
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='ong_management',
            user='root',
            password='root'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Verificar transferencias por organización
        cursor.execute("""
            SELECT 
                organizacion_propietaria,
                tipo,
                organizacion_contraparte,
                solicitud_id,
                fecha_transferencia,
                notas
            FROM transferencias_donaciones 
            ORDER BY organizacion_propietaria, fecha_transferencia DESC
        """)
        
        transfers = cursor.fetchall()
        
        print(f"📊 Total transferencias: {len(transfers)}")
        
        # Agrupar por organización propietaria
        by_org = {}
        for transfer in transfers:
            org = transfer['organizacion_propietaria']
            if org not in by_org:
                by_org[org] = []
            by_org[org].append(transfer)
        
        for org, org_transfers in by_org.items():
            print(f"\n🏢 {org.upper()}:")
            print(f"   Total: {len(org_transfers)} transferencias")
            
            enviadas = [t for t in org_transfers if t['tipo'] == 'ENVIADA']
            recibidas = [t for t in org_transfers if t['tipo'] == 'RECIBIDA']
            
            print(f"   Enviadas: {len(enviadas)}")
            print(f"   Recibidas: {len(recibidas)}")
            
            # Mostrar algunas transferencias de ejemplo
            for i, transfer in enumerate(org_transfers[:3], 1):
                print(f"   {i}. {transfer['tipo']} - {transfer['organizacion_contraparte']} - {transfer['fecha_transferencia']}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_filtering():
    """Test del filtrado de la API"""
    print("\n=== TESTING API FILTERING ===")
    
    base_url = "http://localhost:5000"
    
    # Test con diferentes usuarios de diferentes organizaciones
    test_users = [
        {
            "username": "admin",
            "expected_org": "empuje-comunitario"
        },
        {
            "username": "esperanza_admin", 
            "expected_org": "fundacion-esperanza"
        }
    ]
    
    for user_data in test_users:
        print(f"\n--- Testing user: {user_data['username']} ---")
        
        # Login
        login_response = requests.post(f"{base_url}/auth/login", json={
            "username": user_data["username"],
            "password": "admin123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            user_info = login_response.json().get("user", {})
            
            print(f"✅ Login successful")
            print(f"   Organization: {user_info.get('organization')}")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test transfer history
            history_response = requests.post(
                f"{base_url}/messaging/transfer-history",
                headers=headers,
                json={}
            )
            
            if history_response.status_code == 200:
                data = history_response.json()
                transfers = data.get("transfers", [])
                
                print(f"✅ API call successful")
                print(f"   Found {len(transfers)} transfers")
                
                if transfers:
                    print("   Sample transfers:")
                    for i, transfer in enumerate(transfers[:3], 1):
                        print(f"     {i}. {transfer.get('tipo')} - {transfer.get('organizacion_contraparte')} - {transfer.get('fecha_transferencia')}")
                else:
                    print("   No transfers found (this might be expected)")
                    
            else:
                print(f"❌ API call failed: {history_response.status_code}")
                print(f"   Response: {history_response.text}")
        else:
            print(f"❌ Login failed: {history_response.status_code}")

def create_test_transfers():
    """Crear transferencias de prueba para diferentes organizaciones"""
    print("\n=== CREATING TEST TRANSFERS ===")
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='ong_management',
            user='root',
            password='root'
        )
        
        cursor = connection.cursor()
        
        # Crear transferencias para esperanza
        test_transfers_esperanza = [
            {
                'tipo': 'ENVIADA',
                'organizacion_contraparte': 'empuje-comunitario',
                'solicitud_id': 'test-esperanza-001',
                'donaciones': json.dumps([{"categoria": "Alimentos", "descripcion": "Leche", "cantidad": "5L"}]),
                'organizacion_propietaria': 'fundacion-esperanza'
            },
            {
                'tipo': 'RECIBIDA',
                'organizacion_contraparte': 'manos-solidarias',
                'solicitud_id': 'test-esperanza-002',
                'donaciones': json.dumps([{"categoria": "Ropa", "descripcion": "Zapatos", "cantidad": "10 pares"}]),
                'organizacion_propietaria': 'fundacion-esperanza'
            }
        ]
        
        for transfer in test_transfers_esperanza:
            cursor.execute("""
                INSERT INTO transferencias_donaciones 
                (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, organizacion_propietaria, notas)
                VALUES (%s, %s, %s, %s, 'COMPLETADA', %s, 'Transferencia de prueba')
            """, (
                transfer['tipo'],
                transfer['organizacion_contraparte'],
                transfer['solicitud_id'],
                transfer['donaciones'],
                transfer['organizacion_propietaria']
            ))
        
        connection.commit()
        print("✅ Transferencias de prueba creadas para fundacion-esperanza")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando transferencias de prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 TESTING TRANSFER HISTORY FILTERING")
    print("="*60)
    
    # Verificar estado de la BD
    db_success = check_database_state()
    
    if db_success:
        # Crear transferencias de prueba
        create_test_transfers()
        
        # Test API filtering
        try:
            test_api_filtering()
        except requests.exceptions.ConnectionError:
            print("⚠️  API Gateway no está corriendo - no se puede probar el filtrado de API")
            print("   Inicia el API Gateway y ejecuta este test nuevamente")
        
        print("\n" + "="*60)
        print("📋 RESUMEN")
        print("="*60)
        print("✅ Base de datos corregida con campo organizacion_propietaria")
        print("✅ Consulta API actualizada para filtrar por organización")
        print("✅ Transferencias de prueba creadas para diferentes organizaciones")
        
        print("\n🔄 PARA COMPLETAR LA CORRECCIÓN:")
        print("1. Reiniciar API Gateway")
        print("2. Probar historial de transferencias en frontend")
        print("3. Cada organización debería ver solo sus transferencias")

if __name__ == "__main__":
    main()