"""
Repository para gestionar datos de la red de ONGs
Maneja ofertas externas, transferencias, adhesiones y configuración
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import sys
import os

# Agregar el directorio padre al path para importar database_fixed
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'user-service', 'src'))
from database_fixed import get_db_connection


class NetworkRepository:
    def __init__(self):
        self.db = get_db_connection()
    
    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, 
                      fetch_all: bool = False, commit: bool = False) -> Any:
        """Método helper para ejecutar queries con manejo de errores"""
        conn = None
        cursor = None
        try:
            conn = self.db.connect()
            if not conn:
                print("❌ No se pudo establecer conexión a la base de datos")
                return None
                
            cursor = self.db.get_cursor()
            if not cursor:
                print("❌ No se pudo obtener cursor de la base de datos")
                return None
            
            cursor.execute(query, params or ())
            
            result = None
            if fetch_one:
                result = cursor.fetchone()
                result = dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                result = [dict(row) for row in results]
            else:
                result = cursor.rowcount
            
            if commit:
                conn.commit()
            
            return result
            
        except Exception as e:
            print(f"❌ Error ejecutando query: {e}")
            if conn and commit:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.db.close()

    # ==================== OFERTAS EXTERNAS ====================
    
    def create_external_offer(self, organizacion_donante: str, oferta_id: str, 
                            donaciones: List[Dict]) -> Optional[Dict]:
        """Crea una nueva oferta externa"""
        query = """
            INSERT INTO ofertas_externas (organizacion_donante, oferta_id, donaciones)
            VALUES (%s, %s, %s)
            RETURNING id, organizacion_donante, oferta_id, donaciones, activa, fecha_creacion
        """
        return self._execute_query(
            query, 
            (organizacion_donante, oferta_id, json.dumps(donaciones)), 
            fetch_one=True, 
            commit=True
        )
    
    def get_active_external_offers(self) -> List[Dict]:
        """Obtiene todas las ofertas externas activas"""
        query = """
            SELECT id, organizacion_donante, oferta_id, donaciones, fecha_creacion
            FROM ofertas_externas 
            WHERE activa = true 
            ORDER BY fecha_creacion DESC
        """
        return self._execute_query(query, fetch_all=True) or []
    
    def get_external_offer_by_id(self, organizacion_donante: str, oferta_id: str) -> Optional[Dict]:
        """Obtiene una oferta específica por organización y ID"""
        query = """
            SELECT id, organizacion_donante, oferta_id, donaciones, activa, fecha_creacion
            FROM ofertas_externas 
            WHERE organizacion_donante = %s AND oferta_id = %s
        """
        return self._execute_query(query, (organizacion_donante, oferta_id), fetch_one=True)
    
    def deactivate_external_offer(self, organizacion_donante: str, oferta_id: str) -> bool:
        """Desactiva una oferta externa"""
        query = """
            UPDATE ofertas_externas 
            SET activa = false, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE organizacion_donante = %s AND oferta_id = %s
        """
        result = self._execute_query(query, (organizacion_donante, oferta_id), commit=True)
        return result is not None and result > 0

    # ==================== TRANSFERENCIAS ====================
    
    def create_transfer_record(self, tipo: str, organizacion_contraparte: str, 
                             solicitud_id: str, donaciones: List[Dict], 
                             usuario_registro: int, notas: str = None) -> Optional[Dict]:
        """Registra una transferencia de donaciones"""
        query = """
            INSERT INTO transferencias_donaciones 
            (tipo, organizacion_contraparte, solicitud_id, donaciones, usuario_registro, notas)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, tipo, organizacion_contraparte, solicitud_id, donaciones, 
                     estado, fecha_transferencia, usuario_registro, notas
        """
        return self._execute_query(
            query, 
            (tipo, organizacion_contraparte, solicitud_id, json.dumps(donaciones), usuario_registro, notas),
            fetch_one=True, 
            commit=True
        )
    
    def get_transfers_history(self, tipo: str = None, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de transferencias"""
        if tipo:
            query = """
                SELECT t.id, t.tipo, t.organizacion_contraparte, t.solicitud_id, 
                       t.donaciones, t.estado, t.fecha_transferencia, t.notas,
                       u.nombre, u.apellido
                FROM transferencias_donaciones t
                LEFT JOIN usuarios u ON t.usuario_registro = u.id
                WHERE t.tipo = %s
                ORDER BY t.fecha_transferencia DESC
                LIMIT %s
            """
            return self._execute_query(query, (tipo, limit), fetch_all=True) or []
        else:
            query = """
                SELECT t.id, t.tipo, t.organizacion_contraparte, t.solicitud_id, 
                       t.donaciones, t.estado, t.fecha_transferencia, t.notas,
                       u.nombre, u.apellido
                FROM transferencias_donaciones t
                LEFT JOIN usuarios u ON t.usuario_registro = u.id
                ORDER BY t.fecha_transferencia DESC
                LIMIT %s
            """
            return self._execute_query(query, (limit,), fetch_all=True) or []
    
    def update_transfer_status(self, transfer_id: int, estado: str, notas: str = None) -> bool:
        """Actualiza el estado de una transferencia"""
        query = """
            UPDATE transferencias_donaciones 
            SET estado = %s, notas = COALESCE(%s, notas)
            WHERE id = %s
        """
        result = self._execute_query(query, (estado, notas, transfer_id), commit=True)
        return result is not None and result > 0

    # ==================== ADHESIONES A EVENTOS EXTERNOS ====================
    
    def create_external_event_adhesion(self, evento_externo_id: int, voluntario_id: int, 
                                     datos_voluntario: Dict = None) -> Optional[Dict]:
        """Registra adhesión de un voluntario a un evento externo"""
        query = """
            INSERT INTO adhesiones_eventos_externos 
            (evento_externo_id, voluntario_id, datos_voluntario)
            VALUES (%s, %s, %s)
            RETURNING id, evento_externo_id, voluntario_id, fecha_adhesion, estado
        """
        datos_json = json.dumps(datos_voluntario) if datos_voluntario else None
        return self._execute_query(
            query, 
            (evento_externo_id, voluntario_id, datos_json),
            fetch_one=True, 
            commit=True
        )
    
    def get_volunteer_adhesions(self, voluntario_id: int) -> List[Dict]:
        """Obtiene las adhesiones de un voluntario a eventos externos"""
        query = """
            SELECT a.id, a.evento_externo_id, a.fecha_adhesion, a.estado,
                   e.nombre, e.descripcion, e.fecha_evento, e.organizacion_id
            FROM adhesiones_eventos_externos a
            JOIN eventos_externos e ON a.evento_externo_id = e.id
            WHERE a.voluntario_id = %s
            ORDER BY a.fecha_adhesion DESC
        """
        return self._execute_query(query, (voluntario_id,), fetch_all=True) or []
    
    def get_event_adhesions(self, evento_externo_id: int) -> List[Dict]:
        """Obtiene todas las adhesiones a un evento externo específico"""
        query = """
            SELECT a.id, a.voluntario_id, a.fecha_adhesion, a.estado, a.datos_voluntario,
                   u.nombre, u.apellido, u.email, u.telefono
            FROM adhesiones_eventos_externos a
            JOIN usuarios u ON a.voluntario_id = u.id
            WHERE a.evento_externo_id = %s
            ORDER BY a.fecha_adhesion DESC
        """
        return self._execute_query(query, (evento_externo_id,), fetch_all=True) or []
    
    def update_adhesion_status(self, adhesion_id: int, estado: str) -> bool:
        """Actualiza el estado de una adhesión"""
        query = """
            UPDATE adhesiones_eventos_externos 
            SET estado = %s
            WHERE id = %s
        """
        result = self._execute_query(query, (estado, adhesion_id), commit=True)
        return result is not None and result > 0

    # ==================== CONFIGURACIÓN DE ORGANIZACIÓN ====================
    
    def get_organization_config(self, clave: str) -> Optional[str]:
        """Obtiene un valor de configuración de la organización"""
        query = """
            SELECT valor FROM configuracion_organizacion WHERE clave = %s
        """
        result = self._execute_query(query, (clave,), fetch_one=True)
        return result['valor'] if result else None
    
    def set_organization_config(self, clave: str, valor: str, descripcion: str = None) -> bool:
        """Establece un valor de configuración de la organización"""
        query = """
            INSERT INTO configuracion_organizacion (clave, valor, descripcion)
            VALUES (%s, %s, %s)
            ON CONFLICT (clave) 
            DO UPDATE SET valor = EXCLUDED.valor, 
                         descripcion = COALESCE(EXCLUDED.descripcion, configuracion_organizacion.descripcion),
                         fecha_actualizacion = CURRENT_TIMESTAMP
        """
        result = self._execute_query(query, (clave, valor, descripcion), commit=True)
        return result is not None
    
    def get_all_organization_config(self) -> List[Dict]:
        """Obtiene toda la configuración de la organización"""
        query = """
            SELECT clave, valor, descripcion, fecha_creacion, fecha_actualizacion
            FROM configuracion_organizacion
            ORDER BY clave
        """
        return self._execute_query(query, fetch_all=True) or []

    # ==================== HISTORIAL DE MENSAJES ====================
    
    def log_kafka_message(self, topic: str, tipo_mensaje: str, mensaje_id: str,
                         organizacion_origen: str, organizacion_destino: str,
                         contenido: Dict, estado: str = 'PROCESADO') -> Optional[Dict]:
        """Registra un mensaje de Kafka para auditoría"""
        query = """
            INSERT INTO historial_mensajes 
            (topic, tipo_mensaje, mensaje_id, organizacion_origen, organizacion_destino, contenido, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, topic, tipo_mensaje, fecha_procesamiento, estado
        """
        return self._execute_query(
            query,
            (topic, tipo_mensaje, mensaje_id, organizacion_origen, organizacion_destino, 
             json.dumps(contenido), estado),
            fetch_one=True,
            commit=True
        )
    
    def update_message_status(self, message_id: int, estado: str, error_detalle: str = None) -> bool:
        """Actualiza el estado de un mensaje procesado"""
        query = """
            UPDATE historial_mensajes 
            SET estado = %s, error_detalle = %s
            WHERE id = %s
        """
        result = self._execute_query(query, (estado, error_detalle, message_id), commit=True)
        return result is not None and result > 0
    
    def get_message_history(self, topic: str = None, limit: int = 100) -> List[Dict]:
        """Obtiene el historial de mensajes procesados"""
        if topic:
            query = """
                SELECT id, topic, tipo_mensaje, mensaje_id, organizacion_origen, 
                       organizacion_destino, estado, fecha_procesamiento, error_detalle
                FROM historial_mensajes 
                WHERE topic = %s
                ORDER BY fecha_procesamiento DESC
                LIMIT %s
            """
            return self._execute_query(query, (topic, limit), fetch_all=True) or []
        else:
            query = """
                SELECT id, topic, tipo_mensaje, mensaje_id, organizacion_origen, 
                       organizacion_destino, estado, fecha_procesamiento, error_detalle
                FROM historial_mensajes 
                ORDER BY fecha_procesamiento DESC
                LIMIT %s
            """
            return self._execute_query(query, (limit,), fetch_all=True) or []

    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def get_organization_id(self) -> str:
        """Obtiene el ID de la organización actual"""
        org_id = self.get_organization_config('ORGANIZATION_ID')
        return org_id or 'empuje-comunitario'  # Valor por defecto
    
    def is_kafka_enabled(self) -> bool:
        """Verifica si las funcionalidades de Kafka están habilitadas"""
        enabled = self.get_organization_config('KAFKA_ENABLED')
        return enabled and enabled.lower() == 'true'
    
    def get_max_transfer_amount(self) -> int:
        """Obtiene la cantidad máxima permitida para transferencias automáticas"""
        max_amount = self.get_organization_config('MAX_TRANSFER_AMOUNT')
        return int(max_amount) if max_amount else 1000