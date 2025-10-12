#!/usr/bin/env python3
"""
Verificar si el messaging service se inicia correctamente
"""

import subprocess
import time
import requests
import sys

def check_messaging_startup():
    print("🔍 CHECKING MESSAGING SERVICE STARTUP")
    print("=" * 50)
    
    print("⚠️  NOTA: Este test intentará iniciar el messaging service")
    print("   Si ya está corriendo, puede fallar")
    print("   Presiona Ctrl+C para cancelar si es necesario")
    
    try:
        # Intentar iniciar el messaging service
        print("\n🚀 Intentando iniciar messaging service...")
        
        # Cambiar al directorio del messaging service y ejecutar
        process = subprocess.Popen(
            ["python", "src/main.py"],
            cwd="messaging-service",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Esperando 10 segundos para que se inicie...")
        time.sleep(10)
        
        # Verificar si el proceso sigue corriendo
        if process.poll() is None:
            print("✅ Proceso iniciado correctamente")
            
            # Probar conexión
            try:
                response = requests.get("http://localhost:50054/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Messaging service responde correctamente")
                    data = response.json()
                    print(f"   Status: {data.get('status')}")
                    print(f"   Organization: {data.get('organization_id')}")
                    
                    # Verificar consumers
                    status_response = requests.get("http://localhost:50054/status", timeout=5)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        consumers = status_data.get('consumers', {})
                        
                        print("\n📡 Estado de consumers:")
                        for consumer_name, consumer_info in consumers.items():
                            running = consumer_info.get('running', False)
                            topics = consumer_info.get('topics', [])
                            print(f"   {consumer_name}: {'✅ Running' if running else '❌ Stopped'}")
                            print(f"      Topics: {len(topics)}")
                            
                        print("\n🎉 ¡MESSAGING SERVICE FUNCIONANDO CORRECTAMENTE!")
                        print("   Ahora puedes probar las transferencias")
                        
                else:
                    print(f"❌ Health check failed: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print("❌ No se puede conectar al messaging service")
            except Exception as e:
                print(f"❌ Error probando conexión: {str(e)}")
                
        else:
            print("❌ El proceso terminó inesperadamente")
            stdout, stderr = process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            
        # Terminar el proceso
        if process.poll() is None:
            print("\n🛑 Terminando proceso de prueba...")
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
                
    except KeyboardInterrupt:
        print("\n⚠️  Cancelado por el usuario")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📋 RESULTADO")
    print("=" * 50)
    print("Si el messaging service se inició correctamente:")
    print("1. 🚀 Inicia el messaging service manualmente:")
    print("   cd messaging-service")
    print("   python src/main.py")
    print("2. 🧪 Ejecuta el test de transferencias:")
    print("   python test_consumer_fix.py")

if __name__ == "__main__":
    check_messaging_startup()