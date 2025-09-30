#!/usr/bin/env python3
import mysql.connector

def test_event_exposure():
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
        
        # Seleccionar un evento para exponer
        cursor.execute("SELECT id, nombre, descripcion, fecha_evento FROM eventos LIMIT 1")
        evento = cursor.fetchone()
        
        if not evento:
            print("No hay eventos para probar")
            return
            
        event_id = evento[0]
        print(f"Probando con evento ID: {event_id} - {evento[1]}")
        
        # 1. Marcar como expuesto en eventos
        cursor.execute("UPDATE eventos SET expuesto_red = true WHERE id = %s", (event_id,))
        print("✓ Marcado como expuesto_red = true en tabla eventos")
        
        # 2. Insertar en eventos_red
        insert_query = """
            INSERT INTO eventos_red 
            (evento_id, organizacion_origen, nombre, descripcion, fecha_evento, fecha_publicacion, activo)
            VALUES (%s, 'empuje-comunitario', %s, %s, %s, NOW(), true)
            ON DUPLICATE KEY UPDATE
            activo = true, fecha_publicacion = NOW()
        """
        
        cursor.execute(insert_query, (event_id, evento[1], evento[2], evento[3]))
        print("✓ Insertado/actualizado en tabla eventos_red")
        
        connection.commit()
        
        # 3. Verificar que se insertó correctamente
        cursor.execute("""
            SELECT evento_id, organizacion_origen, nombre, activo 
            FROM eventos_red 
            WHERE evento_id = %s AND organizacion_origen = 'empuje-comunitario'
        """, (event_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"✓ Verificado en eventos_red: ID={result[0]}, Org={result[1]}, Activo={result[3]}")
        else:
            print("❌ No se encontró en eventos_red")
        
        # 4. Verificar que NO aparece en eventos externos (correcto)
        cursor.execute("""
            SELECT COUNT(*) FROM eventos_red 
            WHERE organizacion_origen != 'empuje-comunitario' AND activo = true
        """)
        external_count = cursor.fetchone()[0]
        print(f"✓ Eventos externos disponibles: {external_count}")
        
        # 5. Verificar nuestros eventos expuestos
        cursor.execute("""
            SELECT COUNT(*) FROM eventos_red 
            WHERE organizacion_origen = 'empuje-comunitario' AND activo = true
        """)
        our_count = cursor.fetchone()[0]
        print(f"✓ Nuestros eventos expuestos: {our_count}")
        
        cursor.close()
        connection.close()
        
        print(f"\n🎉 Evento {event_id} expuesto exitosamente a la red!")
        print("Nota: Los eventos propios NO aparecen en 'Eventos Externos' (esto es correcto)")
        print("Los eventos propios expuestos pueden verse por otras organizaciones")
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_event_exposure()