#!/usr/bin/env python3
"""
Script para corregir las credenciales del messaging service directamente
"""
import os
import sys
from pathlib import Path

def fix_messaging_credentials():
    """Corregir las credenciales del messaging service directamente"""
    
    print("🔧 CORRIGIENDO CREDENCIALES DEL MESSAGING SERVICE")
    print("=" * 55)
    
    # Ruta al archivo de configuración
    config_file = Path(__file__).parent / 'messaging-service' / 'src' / 'messaging' / 'config.py'
    
    if not config_file.exists():
        print(f"❌ Archivo de configuración no encontrado: {config_file}")
        return
    
    print(f"📄 Archivo de configuración: {config_file}")
    
    # Leer el archivo actual
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"🔍 Buscando configuración de base de datos...")
    
    # Mostrar configuración actual
    if 'db_user: str = Field(default_factory=lambda: os.getenv("DB_USER", "ong_user"))' in content:
        print(f"❌ Configuración actual usa 'ong_user' por defecto")
    
    # Crear backup
    backup_file = config_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup creado: {backup_file}")
    
    # Reemplazar configuración
    new_content = content.replace(
        'db_user: str = Field(default_factory=lambda: os.getenv("DB_USER", "ong_user"))',
        'db_user: str = Field(default_factory=lambda: os.getenv("DB_USER", "root"))'
    ).replace(
        'db_password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", "ong_pass"))',
        'db_password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", "root"))'
    ).replace(
        'db_host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "mysql"))',
        'db_host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))'
    )
    
    # Escribir archivo corregido
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Configuración corregida:")
    print(f"   DB_USER: ong_user → root")
    print(f"   DB_PASSWORD: ong_pass → root") 
    print(f"   DB_HOST: mysql → localhost")
    
    print(f"\n🔄 AHORA NECESITAS REINICIAR EL MESSAGING SERVICE:")
    print(f"   1. Detener el servicio actual (Ctrl+C)")
    print(f"   2. Reiniciar con: python start_messaging_local.py")
    print(f"   3. O simplemente: cd messaging-service/src && python main.py")
    
    print(f"\n💡 ALTERNATIVA RÁPIDA:")
    print(f"   Puedes reiniciar el servicio y debería usar las credenciales correctas automáticamente")

if __name__ == "__main__":
    fix_messaging_credentials()