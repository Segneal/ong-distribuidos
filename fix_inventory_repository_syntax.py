#!/usr/bin/env python3
"""
Script para arreglar errores de sintaxis en inventory_repository_mysql.py
"""

def fix_syntax_errors():
    """Arreglar todos los errores de sintaxis"""
    
    file_path = "inventory-service/src/inventory_repository_mysql.py"
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Arreglar el problema específico: organizacion fuera del constructor
    # Buscar patrones problemáticos y arreglarlos
    
    # Patrón 1: organizacion fuera del constructor
    content = content.replace(
        "                    usuario_alta=result['usuario_alta']\n                organizacion=row.get('organizacion', 'empuje-comunitario'),",
        "                    usuario_alta=result['usuario_alta'],\n                    organizacion=result.get('organizacion', 'empuje-comunitario')"
    )
    
    content = content.replace(
        "                    usuario_alta=row['usuario_alta']\n                organizacion=row.get('organizacion', 'empuje-comunitario'),",
        "                    usuario_alta=row['usuario_alta'],\n                    organizacion=row.get('organizacion', 'empuje-comunitario')"
    )
    
    # Arreglar cualquier referencia a 'row' que debería ser 'result'
    lines = content.split('\n')
    new_lines = []
    
    in_donation_constructor = False
    for i, line in enumerate(lines):
        if "donation = Donation(" in line:
            in_donation_constructor = True
        elif in_donation_constructor and line.strip().endswith(')'):
            in_donation_constructor = False
        
        # Si estamos en un constructor de Donation y hay una referencia a 'row'
        # pero debería ser 'result', arreglarlo
        if in_donation_constructor and "organizacion=row.get" in line:
            line = line.replace("organizacion=row.get", "organizacion=result.get")
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Escribir el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Errores de sintaxis corregidos")

if __name__ == "__main__":
    print("🔧 ARREGLANDO ERRORES DE SINTAXIS")
    print("=" * 40)
    fix_syntax_errors()