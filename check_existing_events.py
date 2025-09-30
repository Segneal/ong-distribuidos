import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        database='ong_management',
        user='root',
        password='root',
        port=3306
    )
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM eventos LIMIT 3")
    events = cursor.fetchall()
    
    print("Eventos existentes:")
    for event in events:
        print(f"  ID: {event['id']}")
        print(f"  Nombre: {event['nombre']}")
        print(f"  expuesto_red: {event.get('expuesto_red', 'MISSING')}")
        print(f"  Keys: {list(event.keys())}")
        print("  ---")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")