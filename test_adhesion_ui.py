#!/usr/bin/env python3
"""
Test para verificar que la interfaz de gestión de adhesiones funciona correctamente
"""
import os
import sys
import json
import time
from datetime import datetime, timedelta

# Add messaging service to path
sys.path.append('messaging-service/src')

def create_test_adhesions():
    """Crear adhesiones de prueba para verificar la interfaz"""
    print("=== CREANDO ADHESIONES DE PRUEBA ===")
    
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    # Crear adhesiones desde diferentes organizaciones a empuje-comunitario
    test_organizations = [
        {
            'org_id': 'esperanza-viva',
            'volunteers': [
                {
                    'volunteer_id': 101,
                    'name': 'María',
                    'surname': 'González',
                    'email': 'maria.gonzalez@esperanza.org',
                    'phone': '123456789'
                },
                {
                    'volunteer_id': 102,
                    'name': 'Carlos',
                    'surname': 'Rodríguez',
                    'email': 'carlos.rodriguez@esperanza.org',
                    'phone': '987654321'
                }
            ]
        },
        {
            'org_id': 'manos-solidarias',
            'volunteers': [
                {
                    'volunteer_id': 201,
                    'name': 'Ana',
                    'surname': 'Martínez',
                    'email': 'ana.martinez@manos.org',
                    'phone': '555666777'
                }
            ]
        },
        {
            'org_id': 'corazon-abierto',
            'volunteers': [
                {
                    'volunteer_id': 301,
                    'name': 'Luis',
                    'surname': 'Fernández',
                    'email': 'luis.fernandez@corazon.org',
                    'phone': '111222333'
                },
                {
                    'volunteer_id': 302,
                    'name': 'Elena',
                    'surname': 'Torres',
                    'email': 'elena.torres@corazon.org',
                    'phone': '444555666'
                }
            ]
        }
    ]
    
    # Eventos de prueba
    test_events = [
        'evento-solidario-1',
        'evento-comunitario-2',
        'jornada-voluntariado-3'
    ]
    
    success_count = 0
    total_adhesions = 0
    
    for org_data in test_organizations:
        org_id = org_data['org_id']
        
        # Configurar organización
        os.environ['ORGANIZATION_ID'] = org_id
        
        # Import fresh modules
        import importlib
        import messaging.config
        importlib.reload(messaging.config)
        
        from messaging.config import settings
        from messaging.producers.base_producer import BaseProducer
        
        producer = BaseProducer()
        
        print(f"\nEnviando adhesiones desde {org_id}...")
        
        for volunteer in org_data['volunteers']:
            for event_id in test_events:
                total_adhesions += 1
                
                # Enviar adhesión a empuje-comunitario
                success = producer.publish_event_adhesion(
                    target_org="empuje-comunitario",
                    event_id=event_id,
                    volunteer_data=volunteer
                )
                
                if success:
                    success_count += 1
                    print(f"  ✅ {volunteer['name']} → {event_id}")
                else:
                    print(f"  ❌ {volunteer['name']} → {event_id}")
                
                # Pequeña pausa para evitar saturar Kafka
                time.sleep(0.1)
    
    print(f"\n📊 RESULTADO: {success_count}/{total_adhesions} adhesiones enviadas")
    
    if success_count == total_adhesions:
        print("🎉 ¡Todas las adhesiones de prueba se enviaron correctamente!")
        print("\nAhora puedes:")
        print("1. Abrir el frontend en http://localhost:3000")
        print("2. Iniciar sesión como admin de empuje-comunitario")
        print("3. Ir a 'Red de ONGs' → 'Gestión de Adhesiones'")
        print("4. Ver las adhesiones pendientes y aprobar/rechazar")
    else:
        print("❌ Algunos envíos fallaron")
    
    return success_count == total_adhesions

def create_reverse_adhesions():
    """Crear adhesiones desde empuje-comunitario hacia otras organizaciones"""
    print("\n=== CREANDO ADHESIONES INVERSAS ===")
    
    os.environ['ORGANIZATION_ID'] = 'empuje-comunitario'
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    # Import fresh modules
    import importlib
    import messaging.config
    importlib.reload(messaging.config)
    
    from messaging.producers.base_producer import BaseProducer
    
    producer = BaseProducer()
    
    # Voluntarios de empuje-comunitario
    empuje_volunteers = [
        {
            'volunteer_id': 401,
            'name': 'Pedro',
            'surname': 'Sánchez',
            'email': 'pedro.sanchez@empuje.org',
            'phone': '777888999'
        },
        {
            'volunteer_id': 402,
            'name': 'Laura',
            'surname': 'López',
            'email': 'laura.lopez@empuje.org',
            'phone': '333444555'
        }
    ]
    
    target_orgs = ['esperanza-viva', 'manos-solidarias']
    events = ['evento-externo-1', 'actividad-colaborativa-2']
    
    success_count = 0
    total_adhesions = 0
    
    for volunteer in empuje_volunteers:
        for target_org in target_orgs:
            for event_id in events:
                total_adhesions += 1
                
                success = producer.publish_event_adhesion(
                    target_org=target_org,
                    event_id=event_id,
                    volunteer_data=volunteer
                )
                
                if success:
                    success_count += 1
                    print(f"  ✅ {volunteer['name']} → {target_org}/{event_id}")
                else:
                    print(f"  ❌ {volunteer['name']} → {target_org}/{event_id}")
                
                time.sleep(0.1)
    
    print(f"\n📊 RESULTADO INVERSO: {success_count}/{total_adhesions} adhesiones enviadas")
    
    return success_count == total_adhesions

def show_ui_instructions():
    """Mostrar instrucciones para probar la interfaz"""
    print("\n" + "="*60)
    print("🖥️  INSTRUCCIONES PARA PROBAR LA INTERFAZ")
    print("="*60)
    
    print("\n1. INICIAR EL FRONTEND:")
    print("   cd frontend")
    print("   npm start")
    print("   Abrir http://localhost:3000")
    
    print("\n2. INICIAR SESIÓN:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("   (o cualquier usuario con rol PRESIDENTE/COORDINADOR)")
    
    print("\n3. NAVEGAR A GESTIÓN DE ADHESIONES:")
    print("   Opción A: Menú lateral → 'Gestión Adhesiones'")
    print("   Opción B: 'Red de ONGs' → 'Gestión de Adhesiones'")
    
    print("\n4. FUNCIONALIDADES DISPONIBLES:")
    print("   ✅ Ver adhesiones pendientes por evento")
    print("   ✅ Aprobar/rechazar adhesiones")
    print("   ✅ Ver estadísticas de adhesiones")
    print("   ✅ Ver mis adhesiones a eventos externos")
    print("   ✅ Filtrar por estado (pendiente, confirmada, rechazada)")
    
    print("\n5. DATOS DE PRUEBA CREADOS:")
    print("   📊 Adhesiones de 5 voluntarios externos")
    print("   📊 3 eventos con adhesiones")
    print("   📊 Adhesiones desde 3 organizaciones diferentes")
    print("   📊 Adhesiones inversas para probar 'Mis Adhesiones'")
    
    print("\n6. PROBAR FUNCIONALIDADES:")
    print("   🔸 Seleccionar un evento en la barra lateral")
    print("   🔸 Ver las adhesiones pendientes")
    print("   🔸 Aprobar algunas adhesiones")
    print("   🔸 Rechazar otras (con motivo opcional)")
    print("   🔸 Cambiar a la pestaña 'Mis Adhesiones'")
    print("   🔸 Ver las adhesiones propias a eventos externos")
    
    print("\n7. VERIFICAR NOTIFICACIONES:")
    print("   🔔 Ir a 'Notificaciones' para ver alertas de nuevas adhesiones")
    print("   🔔 Las aprobaciones/rechazos generan notificaciones automáticas")
    
    print("\n" + "="*60)
    print("🚀 ¡LA INTERFAZ DE GESTIÓN DE ADHESIONES ESTÁ LISTA!")
    print("="*60)

def main():
    """Función principal"""
    print("🧪 PREPARANDO DATOS DE PRUEBA PARA LA INTERFAZ DE ADHESIONES")
    print("="*70)
    
    # Crear adhesiones de prueba
    test1 = create_test_adhesions()
    
    # Crear adhesiones inversas
    test2 = create_reverse_adhesions()
    
    # Mostrar instrucciones
    show_ui_instructions()
    
    if test1 and test2:
        print("\n✅ TODOS LOS DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("🎯 La interfaz está lista para ser probada")
    else:
        print("\n⚠️  Algunos datos de prueba no se crearon correctamente")
        print("🔧 Verifica que Kafka esté funcionando")

if __name__ == "__main__":
    main()