import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        database='ong_management',
        user='root',
        password='root',
        port=3306
    )
    
    cursor = conn.cursor()
    
    # Agregar la columna expuesto_red a la tabla eventos
    print("Agregando columna expuesto_red a la tabla eventos...")
    cursor.execute("ALTER TABLE eventos ADD COLUMN expuesto_red BOOLEAN DEFAULT FALSE")
    
    # Verificar que se agregó
    cursor.execute("DESCRIBE eventos")
    columns = cursor.fetchall()
    
    print("Columnas de la tabla eventos después del cambio:")
    for column in columns:
        print(f"  {column[0]} - {column[1]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Columna expuesto_red agregada exitosamente")
    
except Exception as e:
    print(f"Error: {e}")