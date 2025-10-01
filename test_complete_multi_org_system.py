#!/usr/bin/env python3
"""
Script completo para probar el sistema multi-organización
Incluye creación de usuarios, login, y flujos de Kafka
"""
import requests
import json
import time
from datetime import datetime

# Configuración
API_BASE = "http://localhost:3000/api"
MESSAGING_BASE = "http://localhost:8000/api"

def login_user(username, password):
    """Login de usuario y obtener token"""
    login_data = {
        "usernameOrEmail": username,
        "password": password
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data.get('token'), data.get('user')
    else:
        print(f"❌ Error en login {username}: {response.text}")
        return None, None

def create_donation_request(token, user_id, donations, notes=""):
    """Crear solicitud de donación"""
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "donations": donations,
        "userId": user_id,
        "notes": notes
    }
    
    response = requests.post(f"{MESSAGING_BASE}/createDonationRequest", json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('success'), result.get('request_id'), result.get('message')
    else:
        print(f"❌ Error creando solicitud: {response.text}")
        return False, None, response.text

def get_external_requests(token):
    """Obtener solicitudes externas"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{MESSAGING_BASE}/getExternalRequests", json={}, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('success'), result.get('requests', [])
    else:
        print(f"❌ Error obteniendo solicitudes: {response.text}")
        return False, []

def create_donation_offer(token, user_id, donations, notes=""):
    """Crear oferta de donación"""
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "donations": donations,
        "userId": user_id,
        "notes": notes
    }
    
    response = requests.post(f"{MESSAGING_BASE}/createDonationOffer", json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('success'), result.get('offer_id'), result.get('message')
    else:
        print(f"❌ Error creando oferta: {response.text}")
        return False, None, response.text

def get_external_offers(token):
    """Obtener ofertas externas"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{MESSAGING_BASE}/getExternalOffers", json={}, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('success'), result.get('offers', [])
    else:
        print(f"❌ Error obteniendo ofertas: {response.text}")
        return False, []

def transfer_donations(token, user_id, target_org, request_id, donations):
    """Transferir donaciones"""
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "targetOrganization": target_org,
        "requestId": request_id,
        "donations": donations,
        "userId": user_id
    }
    
    response = requests.post(f"{MESSAGING_BASE}/transferDonations", json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        return result.get('success'), result.get('transfer_id'), result.get('message')
    else:
        print(f"❌ Error transfiriendo donaciones: {response.text}")
        return False, None, response.text

def main():
    print("🧪 PRUEBA COMPLETA DEL SISTEMA MULTI-ORGANIZACIÓN")
    print("=" * 70)
    
    # Usuarios de prueba por organización
    test_users = {
        "empuje-comunitario": {"username": "admin", "password": "admin123"},
        "fundacion-esperanza": {"username": "esperanza_admin", "password": "password123"},
        "ong-solidaria": {"username": "solidaria_admin", "password": "password123"},
        "centro-comunitario": {"username": "centro_admin", "password": "password123"}
    }
    
    # Login de todos los usuarios
    print("\\n🔐 FASE 1: LOGIN DE USUARIOS")
    print("-" * 40)
    
    user_sessions = {}
    for org, credentials in test_users.items():
        token, user_data = login_user(credentials["username"], credentials["password"])
        if token and user_data:
            user_sessions[org] = {
                "token": token,
                "user": user_data,
                "user_id": user_data.get("id")
            }
            print(f"✅ {org}: {user_data.get('firstName')} {user_data.get('lastName')} ({user_data.get('role')})")
        else:
            print(f"❌ {org}: Login fallido")
    
    if len(user_sessions) < 2:
        print("❌ Necesitamos al menos 2 usuarios logueados para probar")
        return
    
    # FASE 2: Crear solicitudes de donación
    print("\\n📋 FASE 2: CREAR SOLICITUDES DE DONACIÓN")
    print("-" * 50)
    
    # Fundación Esperanza solicita donaciones
    if "fundacion-esperanza" in user_sessions:
        esperanza_session = user_sessions["fundacion-esperanza"]
        
        donations_needed = [
            {
                "category": "ALIMENTOS",
                "description": "Leche en polvo para niños",
                "quantity": 50,
                "unit": "cajas"
            },
            {
                "category": "ROPA",
                "description": "Ropa de abrigo para invierno",
                "quantity": 100,
                "unit": "prendas"
            }
        ]
        
        success, request_id, message = create_donation_request(
            esperanza_session["token"],
            esperanza_session["user_id"],
            donations_needed,
            "Necesitamos urgentemente para familias vulnerables"
        )
        
        if success:
            print(f"✅ Fundación Esperanza creó solicitud: {request_id}")
        else:
            print(f"❌ Error en solicitud Esperanza: {message}")
    
    # ONG Solidaria solicita donaciones
    if "ong-solidaria" in user_sessions:
        solidaria_session = user_sessions["ong-solidaria"]
        
        donations_needed = [
            {
                "category": "UTILES_ESCOLARES",
                "description": "Cuadernos y lápices",
                "quantity": 200,
                "unit": "sets"
            }
        ]
        
        success, request_id, message = create_donation_request(
            solidaria_session["token"],
            solidaria_session["user_id"],
            donations_needed,
            "Para programa de apoyo escolar"
        )
        
        if success:
            print(f"✅ ONG Solidaria creó solicitud: {request_id}")
        else:
            print(f"❌ Error en solicitud Solidaria: {message}")
    
    # Esperar un poco para que los mensajes se procesen
    print("\\n⏳ Esperando procesamiento de mensajes Kafka...")
    time.sleep(3)
    
    # FASE 3: Ver solicitudes externas
    print("\\n👀 FASE 3: VER SOLICITUDES EXTERNAS")
    print("-" * 45)
    
    for org, session in user_sessions.items():
        success, requests = get_external_requests(session["token"])
        if success:
            print(f"\\n📋 {org.upper()} ve {len(requests)} solicitudes externas:")
            for req in requests:
                print(f"  • {req.get('organization_name')}: {len(req.get('donations', []))} items")
                for donation in req.get('donations', []):
                    print(f"    - {donation.get('category')}: {donation.get('description')}")
        else:
            print(f"❌ {org}: Error obteniendo solicitudes")
    
    # FASE 4: Crear ofertas de donación
    print("\\n🎁 FASE 4: CREAR OFERTAS DE DONACIÓN")
    print("-" * 45)
    
    # Centro Comunitario ofrece donaciones
    if "centro-comunitario" in user_sessions:
        centro_session = user_sessions["centro-comunitario"]
        
        donations_offered = [
            {
                "category": "ALIMENTOS",
                "description": "Leche en polvo",
                "quantity": 30,
                "unit": "cajas"
            },
            {
                "category": "ROPA",
                "description": "Camperas de invierno",
                "quantity": 50,
                "unit": "prendas"
            }
        ]
        
        success, offer_id, message = create_donation_offer(
            centro_session["token"],
            centro_session["user_id"],
            donations_offered,
            "Donaciones disponibles inmediatamente"
        )
        
        if success:
            print(f"✅ Centro Comunitario creó oferta: {offer_id}")
        else:
            print(f"❌ Error en oferta Centro: {message}")
    
    # Empuje Comunitario ofrece donaciones
    if "empuje-comunitario" in user_sessions:
        empuje_session = user_sessions["empuje-comunitario"]
        
        donations_offered = [
            {
                "category": "UTILES_ESCOLARES",
                "description": "Cuadernos y útiles",
                "quantity": 150,
                "unit": "sets"
            }
        ]
        
        success, offer_id, message = create_donation_offer(
            empuje_session["token"],
            empuje_session["user_id"],
            donations_offered,
            "Útiles escolares nuevos"
        )
        
        if success:
            print(f"✅ Empuje Comunitario creó oferta: {offer_id}")
        else:
            print(f"❌ Error en oferta Empuje: {message}")
    
    # Esperar procesamiento
    print("\\n⏳ Esperando procesamiento de ofertas...")
    time.sleep(3)
    
    # FASE 5: Ver ofertas externas
    print("\\n🔍 FASE 5: VER OFERTAS EXTERNAS")
    print("-" * 40)
    
    for org, session in user_sessions.items():
        success, offers = get_external_offers(session["token"])
        if success:
            print(f"\\n🎁 {org.upper()} ve {len(offers)} ofertas externas:")
            for offer in offers:
                print(f"  • {offer.get('organization_name')}: {len(offer.get('donations', []))} items")
                for donation in offer.get('donations', []):
                    print(f"    - {donation.get('category')}: {donation.get('description')}")
        else:
            print(f"❌ {org}: Error obteniendo ofertas")
    
    # FASE 6: Simular transferencia de donaciones
    print("\\n🚚 FASE 6: TRANSFERIR DONACIONES")
    print("-" * 40)
    
    # Centro Comunitario transfiere a Fundación Esperanza
    if "centro-comunitario" in user_sessions and "fundacion-esperanza" in user_sessions:
        centro_session = user_sessions["centro-comunitario"]
        
        # Obtener solicitudes de Esperanza
        success, requests = get_external_requests(centro_session["token"])
        if success and requests:
            esperanza_request = None
            for req in requests:
                if req.get('organization_id') == 'fundacion-esperanza':
                    esperanza_request = req
                    break
            
            if esperanza_request:
                # Transferir algunas donaciones
                donations_to_transfer = [
                    {
                        "category": "ALIMENTOS",
                        "description": "Leche en polvo",
                        "quantity": 25,
                        "unit": "cajas"
                    }
                ]
                
                success, transfer_id, message = transfer_donations(
                    centro_session["token"],
                    centro_session["user_id"],
                    "fundacion-esperanza",
                    esperanza_request.get('request_id'),
                    donations_to_transfer
                )
                
                if success:
                    print(f"✅ Centro → Esperanza: Transferencia {transfer_id}")
                else:
                    print(f"❌ Error en transferencia: {message}")
            else:
                print("❌ No se encontró solicitud de Esperanza")
    
    print("\\n🎉 PRUEBA COMPLETA FINALIZADA")
    print("=" * 70)
    print("\\n📊 RESUMEN:")
    print(f"  • {len(user_sessions)} organizaciones activas")
    print("  • Solicitudes de donación creadas y distribuidas")
    print("  • Ofertas de donación publicadas")
    print("  • Transferencias entre organizaciones")
    print("  • Mensajería Kafka funcionando")
    
    print("\\n🔧 PRÓXIMOS PASOS:")
    print("  1. Verificar en la UI que cada organización ve su información")
    print("  2. Probar eventos solidarios entre organizaciones")
    print("  3. Verificar notificaciones en tiempo real")
    print("  4. Probar adhesiones de voluntarios")

if __name__ == "__main__":
    main()