#!/usr/bin/env python3
"""
Script para probar la configuración local del messaging service
"""
import sys
import os
from pathlib import Path

def test_messaging_config_local():
    """Probar la configuración local del messaging service"""
    
    print("🧪 TESTING CONFIGURACIÓN LOCAL DEL MESSAGING SERVICE")
    print("=" * 55)
    
    # Configurar variables de entorno desde .env.local
    env_file = Path(__file__).parent / 'messaging-service' / '.env.local'
    
    if env_file.exists():
        print(f"📄 Cargando configuración desde: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"  🔧 {key.strip()}={value.strip()}")
    else:
        print(f"❌ Archivo de configuración no encontrado: {env_file}")
        return
    
    # Agregar paths necesarios
    sys.path.append(os.path.join(os.path.dirname(__file__), 'messaging-service', 'src'))
    
    try:
        # Importar configuración
        from messaging.config import settings
        print(f"\n✅ Configuración cargada correctamente:")
        print(f"   DB Host: {settings.db_host}")
        print(f"   DB Port: {settings.db_port}")
        print(f"   DB Name: {settings.db_name}")
        print(f"   DB User: {settings.db_user}")
        print(f"   Organization: {settings.organization_id}")
        print(f"   Service Port: {settings.service_port}")
        
        # Probar conexión a base de datos
        from messaging.database.connection import get_database_connection
        print(f"\n🔍 Probando conexión a base de datos...")
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print("✅ Conexión a base de datos OK")
            
            # Probar consulta a tabla de usuarios
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            user_count = cursor.fetchone()
            print(f"✅ Tabla usuarios accesible: {user_count[0]} usuarios")
        
        print(f"\n🎉 CONFIGURACIÓN LOCAL LISTA")
        print(f"💡 Para iniciar el messaging service:")
        print(f"   python start_messaging_local.py")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_messaging_config_local()