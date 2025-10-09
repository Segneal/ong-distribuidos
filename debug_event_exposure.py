#!/usr/bin/env python3
import mysql.connector

def debug_event_exposure():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        # Verificar eventos en tabla eventos
        print("=== EVENTOS EN TABLA 'eventos' ===")
        cursor.execute("SELECT id, nombre, descripcion, fecha_evento, expuesto_red FROM eventos")
        eventos = cursor.fetchall()
        for evento in eventos:
            print(f"ID: {evento[0]}, Nombre: {evento[1]}, Expuesto: {evento[4]}")
        
        print("\n=== EVENTOS EN TABLA 'eventos_red' ===")
        cursor.execute("SELECT evento_id, organizacion_origen, nombre, descripcion, fecha_evento, activo FROM eventos_red")
        eventos_red = cursor.fetchall()
        for evento in eventos_red:
            print(f"ID: {evento[0]}, Org: {evento[1]}, Nombre: {evento[2]}, Activo: {evento[5]}")
        
        print("\n=== EVENTOS DE NUESTRA ORGANIZACIÓN EN LA RED ===")
        cursor.execute("""
            SELECT evento_id, organizacion_origen, nombre, descripcion, fecha_evento, activo 
            FROM eventos_red 
            WHERE organizacion_origen = 'empuje-comunitario'
        """)
        nuestros_eventos = cursor.fetchall()
        for evento in nuestros_eventos:
            print(f"ID: {evento[0]}, Nombre: {evento[2]}, Activo: {evento[5]}")
        
        print("\n=== VERIFICACIÓN DE SINCRONIZACIÓN ===")
        cursor.execute("""
            SELECT e.id, e.nombre, e.expuesto_red, 
                   er.evento_id, er.activo
            FROM eventos e
            LEFT JOIN eventos_red er ON e.id = er.evento_id 
                AND er.organizacion_origen = 'empuje-comunitario'
            WHERE e.expuesto_red = true
        """)
        sincronizacion = cursor.fetchall()
        for row in sincronizacion:
            print(f"Evento {row[0]} ({row[1]}): expuesto_red={row[2]}, en_eventos_red={row[3] is not None}, activo={row[4]}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    debug_event_exposure()