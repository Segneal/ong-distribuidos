#!/usr/bin/env python3
import mysql.connector
import hashlib
import sys
import os
sys.path.append('user-service/src')

from user_repository_mysql import UserRepository

def debug_auth():
    try:
        repo = UserRepository()
        
        print("🔍 DEBUG USER SERVICE")
        print("=" * 30)
        
        # Probar get_user_by_username_or_email
        user = repo.get_user_by_username_or_email("esperanza_admin")
        
        if user:
            print("✅ Usuario encontrado:")
            for key, value in user.items():
                print(f"   {key}: {value}")
            
            # Verificar password
            password_hash = hashlib.sha256("password123".encode()).hexdigest()
            stored_hash = user.get('password_hash')
            
            print(f"\nPassword check:")
            print(f"   Input hash: {password_hash[:20]}...")
            print(f"   Stored hash: {stored_hash[:20]}...")
            print(f"   Match: {password_hash == stored_hash}")
            
        else:
            print("❌ Usuario no encontrado")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_auth()