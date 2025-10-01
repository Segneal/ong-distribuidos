#!/usr/bin/env python3
"""
Debug de la signatura del repository
"""
import sys
import os
sys.path.append('user-service/src')

def debug_repository_signature():
    print("🔍 DEBUG REPOSITORY SIGNATURE")
    print("=" * 40)
    
    try:
        # Verificar qué archivo se está importando
        from user_repository_mysql import UserRepository
        import inspect
        
        repo = UserRepository()
        
        # Verificar la ubicación del archivo
        module = inspect.getmodule(repo.create_user)
        print(f"Módulo: {module}")
        print(f"Archivo: {module.__file__}")
        
        # Verificar la signatura
        sig = inspect.signature(repo.create_user)
        print(f"\nSignatura actual:")
        print(f"  Parámetros: {list(sig.parameters.keys())}")
        print(f"  Total: {len(sig.parameters)}")
        
        # Verificar el código fuente
        source = inspect.getsource(repo.create_user)
        print(f"\nPrimeras líneas del código:")
        lines = source.split('\n')[:3]
        for line in lines:
            print(f"  {line}")
        
        # Verificar si hay otros archivos user_repository
        import glob
        repo_files = glob.glob("**/user_repository*.py", recursive=True)
        print(f"\nArchivos user_repository encontrados:")
        for file in repo_files:
            print(f"  - {file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_repository_signature()