#!/usr/bin/env python3
"""
Debug para verificar el estado de las adhesiones en la base de datos
"""
import mysql.connector
import json
from datetime import datetime

def connect_to_database():
    """Conectar a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='ong_management',
            user='root',
            password='root'
        )
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def check_adhesion_status():
    """Verificar el estado de las adhesiones en la base de datos"""
    print("=== DEBUGGING ADHESION STATUS ===")
    
    connection = connect_to_database()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    # Verificar tabla adhesiones_eventos_externos
    print("\n1. VERIFICANDO TABLA adhesiones_eventos_externos:")
    try:
        cursor.execute("""
            SELECT 
                id,
                evento_externo_id,
                voluntario_id,
                estado,
                fecha_adhesion,
                fecha_aprobacion,
                datos_voluntario
            FROM adhesiones_eventos_externos 
            ORDER BY fecha_adhesion DESC 
            LIMIT 10
        """)
        
        adhesions = cursor.fetchall()
        
        if adhesions:
            print(f"   Encontradas {len(adhesions)} adhesiones:")
            for adhesion in adhesions:
                volunteer_data = {}
                try:
                    if adhesion['datos_voluntario']:
                        volunteer_data = json.loads(adhesion['datos_voluntario'])
                except:
                    pass
                
                volunteer_name = volunteer_data.get('name', 'No especificado')
                volunteer_org = volunteer_data.get('organization_id', 'No especificada')
                
                print(f"     ID: {adhesion['id']}")
                print(f"     Evento: {adhesion['evento_externo_id']}")
                print(f"     Voluntario: {volunteer_name} (ID: {adhesion['voluntario_id']})")
                print(f"     Organización: {volunteer_org}")
                print(f"     Estado: {adhesion['estado']}")
                print(f"     Fecha adhesión: {adhesion['fecha_adhesion']}")
                print(f"     Fecha aprobación: {adhesion['fecha_aprobacion']}")
                print("     " + "-"*50)
        else:
            print("   No se encontraron adhesiones")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    # Verificar tabla eventos_red
    print("\n2. VERIFICANDO TABLA eventos_red:")
    try:
        cursor.execute("""
            SELECT 
                evento_id,
                nombre,
                descripcion,
                fecha_evento,
                organizacion_origen
            FROM eventos_red 
            ORDER BY fecha_evento DESC 
            LIMIT 5
        """)
        
        events = cursor.fetchall()
        
        if events:
            print(f"   Encontrados {len(events)} eventos:")
            for event in events:
                print(f"     ID: {event['evento_id']}")
                print(f"     Nombre: {event['nombre']}")
                print(f"     Organización: {event['organizacion_origen']}")
                print(f"     Fecha: {event['fecha_evento']}")
                print("     " + "-"*30)
        else:
            print("   No se encontraron eventos")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    # Verificar notificaciones
    print("\n3. VERIFICANDO NOTIFICACIONES:")
    try:
        cursor.execute("""
            SELECT 
                id,
                usuario_id,
                titulo,
                mensaje,
                tipo,
                fecha_creacion,
                leida
            FROM notificaciones_usuarios 
            WHERE titulo LIKE '%adhesión%' OR titulo LIKE '%evento%'
            ORDER BY fecha_creacion DESC 
            LIMIT 5
        """)
        
        notifications = cursor.fetchall()
        
        if notifications:
            print(f"   Encontradas {len(notifications)} notificaciones:")
            for notif in notifications:
                print(f"     ID: {notif['id']}")
                print(f"     Usuario: {notif['usuario_id']}")
                print(f"     Título: {notif['titulo']}")
                print(f"     Mensaje: {notif['mensaje'][:100]}...")
                print(f"     Tipo: {notif['tipo']}")
                print(f"     Fecha: {notif['fecha_creacion']}")
                print(f"     Leída: {notif['leida']}")
                print("     " + "-"*30)
        else:
            print("   No se encontraron notificaciones relacionadas")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    # Verificar usuarios
    print("\n4. VERIFICANDO USUARIOS:")
    try:
        cursor.execute("""
            SELECT 
                id,
                nombre_usuario,
                nombre,
                apellido,
                email,
                rol
            FROM usuarios 
            WHERE id IN (
                SELECT DISTINCT voluntario_id 
                FROM adhesiones_eventos_externos
            )
            LIMIT 5
        """)
        
        users = cursor.fetchall()
        
        if users:
            print(f"   Encontrados {len(users)} usuarios con adhesiones:")
            for user in users:
                print(f"     ID: {user['id']}")
                print(f"     Usuario: {user['nombre_usuario']}")
                print(f"     Nombre: {user['nombre']} {user['apellido']}")
                print(f"     Email: {user['email']}")
                print(f"     Rol: {user['rol']}")
                print("     " + "-"*30)
        else:
            print("   No se encontraron usuarios")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    cursor.close()
    connection.close()

def simulate_status_update():
    """Simular actualización de estado para debug"""
    print("\n=== SIMULANDO ACTUALIZACIÓN DE ESTADO ===")
    
    connection = connect_to_database()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Buscar una adhesión pendiente
        cursor.execute("""
            SELECT id, evento_externo_id, voluntario_id, estado
            FROM adhesiones_eventos_externos 
            WHERE estado = 'PENDIENTE'
            LIMIT 1
        """)
        
        adhesion = cursor.fetchone()
        
        if adhesion:
            print(f"Encontrada adhesión pendiente: ID {adhesion['id']}")
            print(f"Estado actual: {adhesion['estado']}")
            
            # Actualizar a CONFIRMADA
            cursor.execute("""
                UPDATE adhesiones_eventos_externos 
                SET estado = 'CONFIRMADA', fecha_aprobacion = NOW()
                WHERE id = %s
            """, (adhesion['id'],))
            
            connection.commit()
            
            # Verificar actualización
            cursor.execute("""
                SELECT estado, fecha_aprobacion
                FROM adhesiones_eventos_externos 
                WHERE id = %s
            """, (adhesion['id'],))
            
            updated = cursor.fetchone()
            print(f"Estado después de actualización: {updated['estado']}")
            print(f"Fecha aprobación: {updated['fecha_aprobacion']}")
            
        else:
            print("No se encontraron adhesiones pendientes")
    
    except Exception as e:
        print(f"Error en simulación: {e}")
    
    cursor.close()
    connection.close()

def main():
    """Función principal"""
    print("🔍 DEBUGGING ADHESION STATUS IN DATABASE")
    print("="*60)
    
    check_adhesion_status()
    
    print("\n" + "="*60)
    print("🔧 POSIBLES PROBLEMAS Y SOLUCIONES")
    print("="*60)
    
    print("\n1. SI LAS ADHESIONES ESTÁN PENDIENTES EN LA BD:")
    print("   - El botón de aprobar no está funcionando")
    print("   - Verificar logs del API Gateway")
    print("   - Verificar permisos de la ruta approve-event-adhesion")
    
    print("\n2. SI LAS ADHESIONES ESTÁN CONFIRMADAS EN LA BD:")
    print("   - El frontend no está refrescando los datos")
    print("   - Verificar la consulta volunteer-adhesions")
    print("   - Verificar el mapeo de estados en el frontend")
    
    print("\n3. SI NO HAY ADHESIONES:")
    print("   - Los mensajes Kafka no se están procesando")
    print("   - Verificar el AdhesionConsumer")
    print("   - Verificar la tabla eventos_red")
    
    print("\n4. PARA PROBAR MANUALMENTE:")
    print("   - Ejecutar simulate_status_update()")
    print("   - Verificar en el frontend si se actualiza")
    print("   - Revisar logs del navegador")

if __name__ == "__main__":
    main()