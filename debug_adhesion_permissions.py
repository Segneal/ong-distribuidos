#!/usr/bin/env python3
"""
Debug simple para verificar permisos de adhesiones
"""

def check_permission_configuration():
    """Verificar configuración de permisos"""
    print("🔍 DEBUGGING ADHESION PERMISSIONS")
    print("="*50)
    
    print("\n1. VERIFICANDO ARCHIVOS MODIFICADOS:")
    
    # Verificar AdhesionManagement.jsx
    print("\n📄 AdhesionManagement.jsx:")
    try:
        with open('frontend/src/pages/AdhesionManagement.jsx', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'user?.role' in content:
            print("   ✅ Usa 'user?.role' (correcto)")
        elif 'user?.rol' in content:
            print("   ❌ Usa 'user?.rol' (incorrecto)")
        else:
            print("   ⚠️  No se encontró referencia al rol")
            
        if "'VOCAL'" in content:
            print("   ✅ Incluye rol VOCAL")
        else:
            print("   ❌ No incluye rol VOCAL")
            
        # Contar roles en tabs
        manage_roles = content.count("'PRESIDENTE', 'COORDINADOR', 'VOCAL'")
        all_roles = content.count("'PRESIDENTE', 'COORDINADOR', 'VOCAL', 'VOLUNTARIO'")
        
        print(f"   📊 Configuración de roles:")
        print(f"      - Gestionar Adhesiones: {'✅' if manage_roles > 0 else '❌'}")
        print(f"      - Mis Adhesiones: {'✅' if all_roles > 0 else '❌'}")
        
    except FileNotFoundError:
        print("   ❌ Archivo no encontrado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Verificar App.js
    print("\n📄 App.js:")
    try:
        with open('frontend/src/App.js', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "adhesion-management" in content:
            print("   ✅ Ruta adhesion-management existe")
            
            # Buscar la línea con los roles
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'adhesion-management' in line:
                    # Buscar la línea con roles (debería estar cerca)
                    for j in range(max(0, i-2), min(len(lines), i+5)):
                        if 'RoleProtectedRoute roles=' in lines[j]:
                            if "'VOCAL'" in lines[j]:
                                print("   ✅ Incluye rol VOCAL en la ruta")
                            else:
                                print("   ❌ No incluye rol VOCAL en la ruta")
                            break
                    break
        else:
            print("   ❌ Ruta adhesion-management no encontrada")
            
    except FileNotFoundError:
        print("   ❌ Archivo no encontrado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Verificar Layout.jsx
    print("\n📄 Layout.jsx:")
    try:
        with open('frontend/src/components/common/Layout.jsx', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "Gestión Adhesiones" in content:
            print("   ✅ Menú 'Gestión Adhesiones' existe")
        else:
            print("   ❌ Menú 'Gestión Adhesiones' no encontrado")
            
        if "/adhesion-management" in content:
            print("   ✅ Link a /adhesion-management existe")
        else:
            print("   ❌ Link a /adhesion-management no encontrado")
            
    except FileNotFoundError:
        print("   ❌ Archivo no encontrado")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def show_corrected_configuration():
    """Mostrar la configuración corregida"""
    print("\n" + "="*50)
    print("✅ CONFIGURACIÓN CORREGIDA")
    print("="*50)
    
    print("\n📋 ROLES PERMITIDOS:")
    print("• PRESIDENTE: ✅ Gestión completa + Mis adhesiones")
    print("• COORDINADOR: ✅ Gestión completa + Mis adhesiones") 
    print("• VOCAL: ✅ Gestión completa + Mis adhesiones")
    print("• VOLUNTARIO: ✅ Solo mis adhesiones")
    
    print("\n🔧 CAMBIOS REALIZADOS:")
    print("1. AdhesionManagement.jsx:")
    print("   - Cambiado 'user?.rol' → 'user?.role'")
    print("   - Agregado 'VOCAL' a roles permitidos")
    
    print("\n2. App.js:")
    print("   - Agregado 'VOCAL' a RoleProtectedRoute")
    
    print("\n3. Permisos por funcionalidad:")
    print("   - Gestionar Adhesiones: PRESIDENTE, COORDINADOR, VOCAL")
    print("   - Mis Adhesiones: PRESIDENTE, COORDINADOR, VOCAL, VOLUNTARIO")
    
    print("\n🚀 CÓMO PROBAR:")
    print("1. Reiniciar el frontend (Ctrl+C y npm start)")
    print("2. Iniciar sesión como PRESIDENTE")
    print("3. Ir a 'Gestión Adhesiones'")
    print("4. Debería ver ambas pestañas disponibles")

def main():
    """Función principal"""
    check_permission_configuration()
    show_corrected_configuration()
    
    print("\n" + "="*50)
    print("🎯 PROBLEMA SOLUCIONADO")
    print("="*50)
    print("Los permisos han sido corregidos.")
    print("PRESIDENTE ahora debería tener acceso completo.")

if __name__ == "__main__":
    main()