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
    cursor.execute("DESCRIBE eventos")
    columns = cursor.fetchall()
    
    print("Columnas de la tabla eventos:")
    for column in columns:
        print(f"  {column[0]} - {column[1]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")