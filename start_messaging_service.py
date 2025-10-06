#!/usr/bin/env python3
"""
Script para iniciar el messaging service
"""
import sys
import os
import subprocess

def start_messaging_service():
    """Iniciar el messaging service"""
    
    print("🚀 INICIANDO MESSAGING SERVICE")
    print("=" * 40)
    
    # Cambiar al directorio del messaging service
    messaging_dir = os.path.join(os.path.dirname(__file__), 'messaging-service', 'src')
    
    if not os.path.exists(messaging_dir):
        print(f"❌ Directorio no encontrado: {messaging_dir}")
        return
    
    print(f"📁 Directorio: {messaging_dir}")
    print(f"🌐 Puerto: 50054")
    print(f"🔄 Iniciando servidor...")
    print("-" * 40)
    
    try:
        # Cambiar al directorio y ejecutar
        os.chdir(messaging_dir)
        
        # Ejecutar el servidor
        subprocess.run([sys.executable, "main.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando servidor: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_messaging_service()