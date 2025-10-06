#!/usr/bin/env python3
"""
Script para debuggear el modelo Donation
"""

import sys
import os
sys.path.append('shared')
sys.path.append('inventory-service/src')

def debug_donation_model():
    """Debug del modelo Donation"""
    
    print("🔍 DEBUGGING MODELO DONATION")
    print("=" * 40)
    
    try:
        # Importar el modelo
        print("1️⃣ Importando modelo...")
        from models.donation import Donation, DonationCategory
        print("✅ Modelo importado exitosamente")
        
        # Verificar el constructor
        print("\n2️⃣ Verificando constructor...")
        print(f"Donation.__init__ signature:")
        import inspect
        sig = inspect.signature(Donation.__init__)
        print(f"   {sig}")
        
        # Intentar crear una instancia con nombres en español
        print("\n3️⃣ Creando instancia con nombres en español...")
        donation = Donation(
            id=1,
            categoria=DonationCategory.ALIMENTOS,
            descripcion="Prueba",
            cantidad=10,
            organizacion="empuje-comunitario"
        )
        print("✅ Instancia creada exitosamente")
        print(f"   ID: {donation.id}")
        print(f"   Categoría: {donation.categoria}")
        print(f"   Descripción: {donation.descripcion}")
        print(f"   Cantidad: {donation.cantidad}")
        print(f"   Organización: {getattr(donation, 'organizacion', 'NO DEFINIDA')}")
        
        # Intentar crear con nombres en inglés
        print("\n4️⃣ Probando con nombres en inglés...")
        try:
            donation2 = Donation(
                id=2,
                category=DonationCategory.ALIMENTOS,
                description="Test",
                quantity=5,
                organization="test-org"
            )
            print("✅ También funciona con nombres en inglés")
        except Exception as e:
            print(f"❌ No funciona con nombres en inglés: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_donation_model()