#!/usr/bin/env python3
"""
Simular procesamiento del consumer
"""
import mysql.connector
import json
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def process_pending_transfers():
    """Procesar transferencias pendientes"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Buscar transferencias ENVIADAS que no tienen su contraparte RECIBIDA
        cursor.execute("""
            SELECT t1.* FROM transferencias_donaciones t1
            WHERE t1.tipo = 'ENVIADA' 
            AND t1.fecha_transferencia > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            AND NOT EXISTS (
                SELECT 1 FROM transferencias_donaciones t2 
                WHERE t2.tipo = 'RECIBIDA' 
                AND t2.solicitud_id = t1.solicitud_id 
                AND t2.organizacion_contraparte = t1.organizacion_propietaria
                AND t2.organizacion_propietaria = t1.organizacion_contraparte
            )
            ORDER BY t1.fecha_transferencia DESC
        """)
        
        pending_transfers = cursor.fetchall()
        
        print(f"Transferencias pendientes de procesar: {len(pending_transfers)}")
        
        for transfer in pending_transfers:
            print(f"Procesando transferencia ID {transfer['id']}...")
            
            # Crear transferencia RECIBIDA
            cursor.execute("""
                INSERT INTO transferencias_donaciones 
                (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, usuario_registro, notas, organizacion_propietaria)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'RECIBIDA',
                transfer['organizacion_propietaria'],  # Quien envió
                transfer['solicitud_id'],
                transfer['donaciones'],
                'COMPLETADA',
                datetime.now(),
                None,
                f'Transferencia recibida automáticamente - procesada por consumer simulado',
                transfer['organizacion_contraparte']  # Quien recibe
            ))
            
            recibida_id = cursor.lastrowid
            print(f"  ✅ Transferencia RECIBIDA creada: ID {recibida_id}")
            
            # Buscar admin de la organización receptora
            cursor.execute("""
                SELECT id FROM usuarios 
                WHERE organizacion = %s AND rol IN ('PRESIDENTE', 'COORDINADOR') 
                LIMIT 1
            """, (transfer['organizacion_contraparte'],))
            
            user_row = cursor.fetchone()
            
            if user_row:
                target_user_id = user_row['id']
                
                # Parsear donaciones
                try:
                    donations = json.loads(transfer['donaciones'])
                except:
                    donations = []
                
                donations_text = "\n".join([
                    f"• {d.get('descripcion', d.get('description', 'Donación'))} ({d.get('cantidad', d.get('quantity', '1'))})"
                    for d in donations
                ])
                
                # Crear notificación
                cursor.execute("""
                    INSERT INTO notificaciones 
                    (usuario_id, tipo, titulo, mensaje, datos_adicionales, leida, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s, false, NOW())
                """, (
                    target_user_id,
                    'transferencia_recibida',
                    '🎁 ¡Nueva donación recibida!',
                    f'Has recibido una donación de {transfer["organizacion_propietaria"]}:\n\n{donations_text}\n\nLas donaciones ya están disponibles en tu inventario.',
                    json.dumps({
                        'organizacion_origen': transfer['organizacion_propietaria'],
                        'request_id': transfer['solicitud_id'],
                        'cantidad_items': len(donations),
                        'transfer_id': f'simulated-{transfer["id"]}'
                    })
                ))
                
                notification_id = cursor.lastrowid
                print(f"  ✅ Notificación creada: ID {notification_id}")
            else:
                print(f"  ⚠️  No se encontró usuario admin para {transfer['organizacion_contraparte']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Procesadas {len(pending_transfers)} transferencias")
        return len(pending_transfers)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    print("🔄 SIMULANDO PROCESAMIENTO DEL CONSUMER")
    print("=" * 50)
    
    processed = process_pending_transfers()
    
    if processed > 0:
        print("\n✅ Ahora deberías ver las donaciones recibidas en:")
        print("1. Historial de transferencias")
        print("2. Notificaciones")
    else:
        print("\n📝 No hay transferencias pendientes de procesar")