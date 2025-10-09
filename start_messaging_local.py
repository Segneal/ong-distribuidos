#!/usr/bin/env python3
"""
Script para iniciar el messaging service con configuración local
"""
import sys
import os
import subprocess
from pathlib import Path

def start_messaging_local():
    """Iniciar el messaging service con configuración local"""
    
    print("🚀 INICIANDO MESSAGING SERVICE (LOCAL)")
    print("=" * 45)
    
    # Directorio del messaging service
    messaging_dir = Path(__file__).parent / 'messaging-service'
    env_file = messaging_dir / '.env.local'
    main_file = messaging_dir / 'src' / 'main.py'
    
    if not main_file.exists():
        print(f"❌ Archivo no encontrado: {main_file}")
        return
    
    if not env_file.exists():
        print(f"❌ Archivo de configuración no encontrado: {env_file}")
        return
    
    print(f"📁 Directorio: {messaging_dir}")
    print(f"⚙️  Configuración: {env_file}")
    print(f"🌐 Puerto: 50054")
    print(f"🗄️  Base de datos: localhost:3306")
    print(f"🔄 Iniciando servidor...")
    print("-" * 45)
    
    try:
        # Configurar variables de entorno desde el archivo .env.local
        env_vars = os.environ.copy()
        
        # Leer archivo .env.local
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    print(f"  🔧 {key.strip()}={value.strip()}")
        
        print("-" * 45)
        
        # Cambiar al directorio del messaging service
        os.chdir(messaging_dir / 'src')
        
        # Ejecutar el servidor con las variables de entorno
        subprocess.run([sys.executable, "main.py"], env=env_vars, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando servidor: {e}")
    except FileNotFoundError as e:
        print(f"❌ Archivo no encontrado: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_messaging_local()