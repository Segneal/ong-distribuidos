import os
import requests
from datetime import datetime

def send_password_email(email, username, password, first_name="", last_name=""):
    """Envía la contraseña por email usando el servicio de Node.js"""
    try:
        email_service_url = os.getenv('EMAIL_SERVICE_URL', 'http://localhost:3001')
        
        payload = {
            'email': email,
            'username': username,
            'password': password,
            'firstName': first_name,
            'lastName': last_name
        }
        
        response = requests.post(f"{email_service_url}/send-password", json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"Email enviado exitosamente a {email} para usuario {username}")
            return True
        else:
            print(f"Error enviando email: {response.status_code} - {response.text}")
            # Fallback: escribir al archivo de log
            log_password_to_file(username, password)
            return False
            
    except Exception as e:
        print(f"Error conectando al servicio de email: {e}")
        # Fallback: escribir al archivo de log
        log_password_to_file(username, password)
        return False

def log_password_to_file(username, password):
    """Escribe las credenciales al archivo de log para testing"""
    try:
        # Crear directorio si no existe
        os.makedirs('testing/usuarios', exist_ok=True)
        
        # Escribir al archivo de log
        with open('testing/usuarios/passlogs.txt', 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] Usuario: {username}, Contraseña: {password}\n")
        
        return True
    except Exception as e:
        print(f"Error escribiendo al archivo de log: {e}")
        return False