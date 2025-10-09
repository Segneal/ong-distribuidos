#!/usr/bin/env python3
"""
Script para probar el sistema completo de solicitudes de inscripción
"""
import requests
import json
import time

def test_inscription_system():
    """Probar el sistema completo de solicitudes de inscripción"""
    
    API_BASE = "http://localhost:3001/api"
    
    print("🧪 TESTING SISTEMA DE SOLICITUDES DE INSCRIPCIÓN")
    print("=" * 60)
    
    # 1. Crear solicitud de inscripción (sin autenticación)
    print("📝 PASO 1: CREAR SOLICITUD DE INSCRIPCIÓN")
    
    solicitud_data = {
        "nombre": "Juan Carlos",
        "apellido": "Pérez",
        "email": "juan.perez@test.com",
        "telefono": "+54911555666",
        "organizacion_destino": "empuje-comunitario",
        "rol_solicitado": "VOLUNTARIO",
        "mensaje": "Me interesa colaborar con la organización en actividades comunitarias. Tengo experiencia en trabajo social."
    }
    
    try:
        response = requests.post(f"{API_BASE}/messaging/inscription-request", json=solicitud_data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Solicitud creada exitosamente")
            print(f"  📋 ID: {result.get('solicitud_id')}")
            print(f"  📧 Email: {solicitud_data['email']}")
            print(f"  🏢 Organización: {solicitud_data['organizacion_destino']}")
            solicitud_id = result.get('solicitud_id')
        else:
            print(f"❌ Error creando solicitud: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error conectando al API: {e}")
        return
    
    # Esperar un poco para que se procese el mensaje de Kafka
    print(f"\n⏳ Esperando procesamiento de Kafka...")
    time.sleep(3)
    
    # 2. Login como PRESIDENTE para ver solicitudes
    print(f"\n👤 PASO 2: LOGIN COMO PRESIDENTE")
    
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('token')
            user_info = login_result.get('user', {})
            
            print(f"✅ Login exitoso como PRESIDENTE")
            print(f"  👤 Usuario: {user_info.get('username')}")
            print(f"  🏢 Organización: {user_info.get('organization')}")
            print(f"  🎭 Rol: {user_info.get('role')}")
            
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return
    
    # 3. Obtener solicitudes pendientes
    print(f"\n📋 PASO 3: OBTENER SOLICITUDES PENDIENTES")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        pending_response = requests.get(f"{API_BASE}/messaging/pending-inscriptions", headers=headers)
        
        if pending_response.status_code == 200:
            pending_result = pending_response.json()
            solicitudes = pending_result.get('solicitudes', [])
            
            print(f"✅ Solicitudes obtenidas exitosamente")
            print(f"  📊 Total solicitudes pendientes: {len(solicitudes)}")
            
            if len(solicitudes) > 0:
                print(f"\n📋 SOLICITUDES PENDIENTES:")
                for solicitud in solicitudes:
                    print(f"  📝 ID: {solicitud.get('solicitud_id')}")
                    print(f"      👤 Solicitante: {solicitud.get('nombre')} {solicitud.get('apellido')}")
                    print(f"      📧 Email: {solicitud.get('email')}")
                    print(f"      🎭 Rol: {solicitud.get('rol_solicitado')}")
                    print(f"      📅 Fecha: {solicitud.get('fecha_solicitud')}")
                    if solicitud.get('mensaje'):
                        print(f"      💬 Mensaje: {solicitud.get('mensaje')[:100]}...")
                    print()
            else:
                print(f"⚠️  No se encontraron solicitudes pendientes")
                
        else:
            print(f"❌ Error obteniendo solicitudes: {pending_response.status_code}")
            print(f"   Respuesta: {pending_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error obteniendo solicitudes: {e}")
        return
    
    # 4. Aprobar la solicitud si existe
    if len(solicitudes) > 0 and solicitud_id:
        print(f"\n✅ PASO 4: APROBAR SOLICITUD")
        
        approval_data = {
            "solicitud_id": solicitud_id,
            "accion": "APROBAR",
            "comentarios": "Solicitud aprobada. Bienvenido al equipo!"
        }
        
        try:
            approval_response = requests.post(f"{API_BASE}/messaging/process-inscription", 
                                            json=approval_data, headers=headers)
            
            if approval_response.status_code == 200:
                approval_result = approval_response.json()
                print(f"✅ Solicitud aprobada exitosamente")
                print(f"  📋 ID: {solicitud_id}")
                print(f"  📊 Estado: {approval_result.get('estado')}")
                print(f"  💬 Mensaje: {approval_result.get('message')}")
                
            else:
                print(f"❌ Error aprobando solicitud: {approval_response.status_code}")
                print(f"   Respuesta: {approval_response.text}")
                
        except Exception as e:
            print(f"❌ Error aprobando solicitud: {e}")
    
    # 5. Verificar notificaciones
    print(f"\n🔔 PASO 5: VERIFICAR NOTIFICACIONES")
    
    try:
        notifications_response = requests.get(f"{API_BASE}/messaging/inscription-notifications", headers=headers)
        
        if notifications_response.status_code == 200:
            notifications_result = notifications_response.json()
            notificaciones = notifications_result.get('notificaciones', [])
            
            print(f"✅ Notificaciones obtenidas exitosamente")
            print(f"  📊 Total notificaciones: {len(notificaciones)}")
            
            if len(notificaciones) > 0:
                print(f"\n🔔 NOTIFICACIONES:")
                for notif in notificaciones[:5]:  # Mostrar solo las primeras 5
                    print(f"  📝 Solicitud: {notif.get('solicitud_id')}")
                    print(f"      👤 Solicitante: {notif.get('nombre')} {notif.get('apellido')}")
                    print(f"      📧 Email: {notif.get('email')}")
                    print(f"      🔔 Tipo: {notif.get('tipo_notificacion')}")
                    print(f"      👁️ Leída: {'Sí' if notif.get('leida') else 'No'}")
                    print()
            
        else:
            print(f"❌ Error obteniendo notificaciones: {notifications_response.status_code}")
            print(f"   Respuesta: {notifications_response.text}")
            
    except Exception as e:
        print(f"❌ Error obteniendo notificaciones: {e}")
    
    print(f"\n🎉 TESTING COMPLETADO")
    print(f"✅ Sistema de solicitudes de inscripción funcionando correctamente")

if __name__ == "__main__":
    test_inscription_system()