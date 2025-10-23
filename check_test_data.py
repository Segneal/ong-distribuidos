#!/usr/bin/env python3
"""
Script para revisar los datos de prueba existentes
"""
import pymysql

def check_test_data():
    try:
        # Conectar a la base de datos
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Verificar usuarios
        print("=== USUARIOS ===")
        cursor.execute("SELECT id, nombre_usuario, nombre, apellido, rol FROM usuarios ORDER BY id")
        users = cursor.fetchall()
        for user in users:
            print(f"  ID: {user[0]}, Usuario: {user[1]}, Nombre: {user[2]} {user[3]}, Rol: {user[4]}")
        
        # Verificar eventos
        print("\n=== EVENTOS ===")
        cursor.execute("SELECT id, nombre, descripcion, fecha_evento FROM eventos ORDER BY fecha_evento")
        events = cursor.fetchall()
        for event in events:
            print(f"  ID: {event[0]}, Nombre: {event[1]}, Fecha: {event[3]}")
            print(f"    Descripción: {event[2]}")
        
        # Verificar participaciones
        print("\n=== PARTICIPACIONES EN EVENTOS ===")
        cursor.execute("""
            SELECT pe.evento_id, pe.usuario_id, e.nombre, u.nombre_usuario, pe.fecha_adhesion
            FROM participantes_evento pe
            JOIN eventos e ON pe.evento_id = e.id
            JOIN usuarios u ON pe.usuario_id = u.id
            ORDER BY pe.evento_id, pe.usuario_id
        """)
        participations = cursor.fetchall()
        for part in participations:
            print(f"  Evento {part[0]} ({part[2]}) - Usuario {part[1]} ({part[3]}) - Fecha: {part[4]}")
        
        # Verificar donaciones repartidas
        print("\n=== DONACIONES REPARTIDAS EN EVENTOS ===")
        cursor.execute("""
            SELECT dr.evento_id, dr.donacion_id, dr.cantidad_repartida, e.nombre, d.categoria, d.descripcion
            FROM donaciones_repartidas dr
            JOIN eventos e ON dr.evento_id = e.id
            JOIN donaciones d ON dr.donacion_id = d.id
            ORDER BY dr.evento_id
        """)
        distributions = cursor.fetchall()
        for dist in distributions:
            print(f"  Evento {dist[0]} ({dist[3]}) - Donación {dist[1]} ({dist[4]}: {dist[5]}) - Cantidad: {dist[2]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_test_data()