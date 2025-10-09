#!/usr/bin/env python3
"""
Script para debuggear el repository directamente
"""

import sys
import os
sys.path.append('inventory-service/src')
sys.path.append('shared')

from inventory_repository_final import InventoryRepository
from donation_model_fixed import DonationCategory

def debug_repository():
    """Debug directo del repository"""
    
    print("🔍 DEBUGGING REPOSITORY DIRECTAMENTE")
    print("=" * 50)
    
    try:
        # 1. Crear instancia del repository
        print("1️⃣ Creando repository...")
        repo = InventoryRepository()
        print("✅ Repository creado")
        
        # 2. Intentar crear una donación directamente
        print("\n2️⃣ Intentando crear donación directamente...")
        
        donation = repo.create_donation(
            category=DonationCategory.ALIMENTOS,
            description="Prueba directa del repository",
            quantity=5,
            created_by=1,
            organization="empuje-comunitario"
        )
        
        print(f"📦 Resultado: {donation}")
        
        if donation:
            print("✅ Donación creada exitosamente!")
            print(f"   ID: {donation.id}")
            print(f"   Categoría: {donation.categoria}")
            print(f"   Descripción: {donation.descripcion}")
            print(f"   Cantidad: {donation.cantidad}")
            print(f"   Organización: {getattr(donation, 'organizacion', 'NO DEFINIDA')}")
        else:
            print("❌ Repository devolvió None")
        
        # 3. Intentar obtener todas las donaciones
        print("\n3️⃣ Obteniendo todas las donaciones...")
        donations = repo.get_all_donations()
        print(f"📦 Total donaciones: {len(donations)}")
        
        # Mostrar últimas 3
        for i, d in enumerate(donations[:3]):
            print(f"   {i+1}. {d.descripcion} - {getattr(d, 'organizacion', 'Sin org')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_repository()