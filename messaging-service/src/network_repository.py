"""
Repository para gestionar datos de la red de ONGs
Maneja ofertas externas, transferencias, adhesiones y configuración
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from messaging.database.connection import get_database_connection


class NetworkRepository:
    def __init__(self):
        pass
    
    def get_external_offers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obtiene ofertas externas de donaciones"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT * FROM ofertas_externas"
                params = []
                
                if active_only:
                    query += " WHERE activa = %s"
                    params.append(True)
                
                query += " ORDER BY fecha_creacion DESC"
                
                cursor.execute(query, params)
                offers = cursor.fetchall()
                
                # Convert JSON strings to objects
                for offer in offers:
                    if offer.get('donaciones'):
                        offer['donaciones'] = json.loads(offer['donaciones'])
                
                return offers
                
        except Exception as e:
            print(f"Error getting external offers: {e}")
            return []
    
    def create_external_offer(self, organizacion_donante: str, oferta_id: str, donaciones: List[Dict]) -> bool:
        """Crea una nueva oferta externa"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                INSERT INTO ofertas_externas (organizacion_donante, oferta_id, donaciones)
                VALUES (%s, %s, %s)
                """
                
                cursor.execute(query, (organizacion_donante, oferta_id, json.dumps(donaciones)))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error creating external offer: {e}")
            return False
    
    def get_transfer_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene el historial de transferencias"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = """
                SELECT * FROM transferencias_donaciones
                ORDER BY fecha_transferencia DESC
                LIMIT %s
                """
                
                cursor.execute(query, (limit,))
                transfers = cursor.fetchall()
                
                # Convert JSON strings to objects
                for transfer in transfers:
                    if transfer.get('donaciones'):
                        transfer['donaciones'] = json.loads(transfer['donaciones'])
                
                return transfers
                
        except Exception as e:
            print(f"Error getting transfer history: {e}")
            return []
    
    def create_transfer_record(self, tipo: str, organizacion_contraparte: str, 
                             solicitud_id: str, donaciones: List[Dict], 
                             usuario_registro: int = None, notas: str = None) -> bool:
        """Registra una transferencia de donaciones"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                INSERT INTO transferencias_donaciones 
                (tipo, organizacion_contraparte, solicitud_id, donaciones, usuario_registro, notas)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    tipo, organizacion_contraparte, solicitud_id, 
                    json.dumps(donaciones), usuario_registro, notas
                ))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error creating transfer record: {e}")
            return False
    
    def get_organization_config(self, key: str) -> Optional[str]:
        """Obtiene un valor de configuración de la organización"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT valor FROM configuracion_organizacion WHERE clave = %s"
                cursor.execute(query, (key,))
                result = cursor.fetchone()
                
                return result['valor'] if result else None
                
        except Exception as e:
            print(f"Error getting organization config: {e}")
            return None
    
    def set_organization_config(self, key: str, value: str, description: str = None) -> bool:
        """Establece un valor de configuración de la organización"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                INSERT INTO configuracion_organizacion (clave, valor, descripcion)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                valor = VALUES(valor),
                descripcion = COALESCE(VALUES(descripcion), descripcion),
                fecha_actualizacion = CURRENT_TIMESTAMP
                """
                
                cursor.execute(query, (key, value, description))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error setting organization config: {e}")
            return False