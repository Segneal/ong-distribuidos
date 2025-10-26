#!/usr/bin/env python3
"""
Create test user for REST API testing.
"""
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import get_db, engine, Base
from src.models.user import User, UserRole
from sqlalchemy.orm import Session

def create_test_user():
    """Create a test president user for API testing."""
    print("👤 Creating test user for API testing...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.id == 1).first()
        
        if existing_user:
            print(f"   Test user already exists: {existing_user.nombre_usuario} ({existing_user.rol.value})")
            
            # Update to president role if needed
            if existing_user.rol != UserRole.PRESIDENTE:
                existing_user.rol = UserRole.PRESIDENTE
                existing_user.activo = True
                db.commit()
                print(f"   Updated user role to PRESIDENTE")
            
            return existing_user
        
        # Create new test user
        test_user = User(
            id=1,
            nombre_usuario="test_president",
            nombre="Test",
            apellido="President",
            telefono="+1234567890",
            email="test.president@example.com",
            password_hash="test_hash",  # Not used for JWT auth
            rol=UserRole.PRESIDENTE,
            activo=True,
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow()
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"   ✅ Created test user: {test_user.nombre_usuario} ({test_user.rol.value})")
        return test_user
        
    except Exception as e:
        print(f"   ❌ Error creating test user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_test_non_president_user():
    """Create a test non-president user for role testing."""
    print("👤 Creating test non-president user for role testing...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.id == 2).first()
        
        if existing_user:
            print(f"   Test non-president user already exists: {existing_user.nombre_usuario} ({existing_user.rol.value})")
            return existing_user
        
        # Create new test user
        test_user = User(
            id=2,
            nombre_usuario="test_vocal",
            nombre="Test",
            apellido="Vocal",
            telefono="+1234567891",
            email="test.vocal@example.com",
            password_hash="test_hash",  # Not used for JWT auth
            rol=UserRole.VOCAL,
            activo=True,
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow()
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"   ✅ Created test non-president user: {test_user.nombre_usuario} ({test_user.rol.value})")
        return test_user
        
    except Exception as e:
        print(f"   ❌ Error creating test non-president user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def main():
    """Create test users for API testing."""
    print("🧪 Setting up test users for REST API testing")
    print("=" * 50)
    
    # Create test president user
    president_user = create_test_user()
    
    # Create test non-president user
    non_president_user = create_test_non_president_user()
    
    if president_user and non_president_user:
        print("\n✅ Test users created successfully!")
        print("   Ready for REST API testing with authentication")
        return True
    else:
        print("\n❌ Failed to create test users")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)