#!/usr/bin/env python3
"""
Script para probar el messaging service de forma simple
"""
import sys
import os

# Agregar paths necesarios
sys.path.append(os.path.join(os.path.dirname(__file__), 'messaging-service', 'src'))

def test_messaging_service():
    """Probar el messaging service"""
    
    print("🧪 TESTING MESSAGING SERVICE")
    print("=" * 40)
    
    try:
        # Importar FastAPI
        from fastapi import FastAPI
        print("✅ FastAPI importado correctamente")
        
        # Importar configuración
        from messaging.config import settings
        print("✅ Configuración importada correctamente")
        print(f"   Organization ID: {settings.organization_id}")
        
        # Importar servicios
        from messaging.services.request_service import RequestService
        print("✅ RequestService importado correctamente")
        
        # Probar crear una instancia del servicio
        request_service = RequestService()
        print("✅ RequestService instanciado correctamente")
        
        # Probar conexión a base de datos
        from messaging.database.connection import get_database_connection
        print("✅ Database connection importada correctamente")
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Conexión a base de datos OK")
        
        print(f"\n🎉 MESSAGING SERVICE ESTÁ LISTO PARA EJECUTAR")
        print(f"💡 Para iniciarlo manualmente:")
        print(f"   cd messaging-service/src")
        print(f"   python main.py")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print(f"   Instala las dependencias: pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_messaging_service()