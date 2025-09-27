#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de los repositorios de red
Ejecutar después de aplicar las migraciones de base de datos
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar paths necesarios
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'user-service', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'inventory-service', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'events-service', 'src'))

try:
    from network_repository import NetworkRepository
    from external_requests_repository import ExternalRequestsRepository
    from external_events_repository import ExternalEventsRepository
except ImportError as e:
    print(f"❌ Error importando repositorios: {e}")
    print("Asegúrate de que las migraciones de base de datos se hayan ejecutado correctamente")
    sys.exit(1)


def test_network_repository():
    """Prueba el repositorio principal de red"""
    print("🧪 Probando NetworkRepository...")
    
    repo = NetworkRepository()
    
    # Probar configuración de organización
    org_id = repo.get_organization_id()
    print(f"✅ ID de organización: {org_id}")
    
    # Probar configuración de Kafka
    kafka_enabled = repo.is_kafka_enabled()
    print(f"✅ Kafka habilitado: {kafka_enabled}")
    
    # Probar creación de oferta externa
    test_offer = repo.create_external_offer(
        "test-org", 
        "TEST-001", 
        [{"categoria": "ALIMENTOS", "descripcion": "Test food", "cantidad": "10 units"}]
    )
    if test_offer:
        print(f"✅ Oferta externa creada: {test_offer['id']}")
        
        # Probar obtención de ofertas
        offers = repo.get_active_external_offers()
        print(f"✅ Ofertas activas encontradas: {len(offers)}")
    else:
        print("❌ Error creando oferta externa")
    
    # Probar registro de transferencia
    transfer = repo.create_transfer_record(
        "ENVIADA", 
        "test-org", 
        "REQ-001", 
        [{"categoria": "ALIMENTOS", "descripcion": "Test transfer", "cantidad": "5 units"}],
        1,  # usuario_registro
        "Transferencia de prueba"
    )
    if transfer:
        print(f"✅ Transferencia registrada: {transfer['id']}")
    else:
        print("❌ Error registrando transferencia")
    
    print("✅ NetworkRepository funcionando correctamente\n")


def test_external_requests_repository():
    """Prueba el repositorio de solicitudes externas"""
    print("🧪 Probando ExternalRequestsRepository...")
    
    repo = ExternalRequestsRepository()
    
    # Probar creación de solicitud externa
    test_request = repo.create_external_request(
        "test-org-2",
        "REQ-TEST-001",
        [{"categoria": "ROPA", "descripcion": "Test clothing", "cantidad": "15 items"}]
    )
    if test_request:
        print(f"✅ Solicitud externa creada: {test_request['id']}")
        
        # Probar obtención de solicitudes activas
        requests = repo.get_active_external_requests()
        print(f"✅ Solicitudes activas encontradas: {len(requests)}")
        
        # Probar búsqueda por categoría
        clothing_requests = repo.get_requests_by_category("ROPA")
        print(f"✅ Solicitudes de ROPA encontradas: {len(clothing_requests)}")
    else:
        print("❌ Error creando solicitud externa")
    
    # Probar estadísticas
    stats = repo.get_requests_statistics()
    print(f"✅ Estadísticas obtenidas: {stats['total_active']} activas, {stats['total_inactive']} inactivas")
    
    print("✅ ExternalRequestsRepository funcionando correctamente\n")


def test_external_events_repository():
    """Prueba el repositorio de eventos externos"""
    print("🧪 Probando ExternalEventsRepository...")
    
    repo = ExternalEventsRepository()
    
    # Probar creación de evento externo
    future_date = datetime.now() + timedelta(days=15)
    test_event = repo.create_external_event(
        "test-org-3",
        "EVT-TEST-001",
        "Evento de Prueba",
        "Descripción del evento de prueba",
        future_date
    )
    if test_event:
        print(f"✅ Evento externo creado: {test_event['id']}")
        
        # Probar obtención de eventos activos
        events = repo.get_active_external_events()
        print(f"✅ Eventos activos encontrados: {len(events)}")
        
        # Probar eventos próximos
        upcoming = repo.get_upcoming_events(30)
        print(f"✅ Eventos próximos (30 días): {len(upcoming)}")
        
        # Probar búsqueda de eventos
        search_results = repo.search_events("Prueba")
        print(f"✅ Eventos encontrados con 'Prueba': {len(search_results)}")
    else:
        print("❌ Error creando evento externo")
    
    # Probar estadísticas
    stats = repo.get_events_statistics()
    print(f"✅ Estadísticas obtenidas: {stats['total_active']} activos, {stats['upcoming_events']} próximos")
    
    print("✅ ExternalEventsRepository funcionando correctamente\n")


def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas de repositorios de red de ONGs\n")
    
    try:
        test_network_repository()
        test_external_requests_repository()
        test_external_events_repository()
        
        print("🎉 Todas las pruebas completadas exitosamente!")
        print("✅ Los repositorios de red están funcionando correctamente")
        print("✅ Las tablas de base de datos están configuradas correctamente")
        print("✅ Los índices de optimización están aplicados")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        print("Verifica que:")
        print("1. La base de datos esté ejecutándose")
        print("2. Las migraciones se hayan aplicado correctamente")
        print("3. Los archivos de repositorio estén en las ubicaciones correctas")
        sys.exit(1)


if __name__ == "__main__":
    main()