#!/usr/bin/env python3
"""
Script para arreglar el uso del modelo Donation en el repository
"""

def fix_donation_repository():
    """Arreglar todas las instancias de creación de objetos Donation"""
    
    file_path = "inventory-service/src/inventory_repository_mysql.py"
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazos necesarios
    replacements = [
        # Cambiar nombres de parámetros de inglés a español
        ("category=DonationCategory(", "categoria=DonationCategory("),
        ("description=", "descripcion="),
        ("quantity=", "cantidad="),
        ("deleted=", "eliminado="),
        ("created_at=", "fecha_alta="),
        ("created_by=", "usuario_alta="),
        ("updated_at=", "fecha_modificacion="),
        ("updated_by=", "usuario_modificacion="),
    ]
    
    # Aplicar reemplazos
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Agregar organizacion donde no esté
    # Buscar patrones de creación de Donation y agregar organizacion
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Si encontramos una línea que crea un Donation
        if "donation = Donation(" in line:
            # Buscar el cierre del constructor
            j = i + 1
            while j < len(lines) and not lines[j].strip().endswith(')'):
                new_lines.append(lines[j])
                j += 1
            
            # Agregar organizacion antes del cierre si no está
            if j < len(lines):
                closing_line = lines[j]
                if "organizacion=" not in closing_line and "organizacion=" not in '\n'.join(lines[i:j+1]):
                    # Insertar organizacion antes del cierre
                    indent = len(closing_line) - len(closing_line.lstrip())
                    org_line = " " * indent + "organizacion=row.get('organizacion', 'empuje-comunitario'),"
                    new_lines.append(org_line)
                new_lines.append(closing_line)
                i = j
        
        i += 1
    
    # Escribir el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Archivo corregido exitosamente")

if __name__ == "__main__":
    print("🔧 ARREGLANDO USO DEL MODELO DONATION")
    print("=" * 40)
    fix_donation_repository()