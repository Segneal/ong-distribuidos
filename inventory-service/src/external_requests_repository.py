"""
Repository para gestionar solicitudes externas de donaciones
Extiende la funcionalidad del inventory-service para manejar solicitudes de la red
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from database_mysql import get_db_connection


class ExternalRequestsRepository:
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

    # ==================== SOLICITUDES EXTERNAS ====================
    
    def create_external_request(self, organizacion_solicitante: str, solicitud_id: str, 
                              donaciones: List[Dict]) -> Optional[Dict]:
        """Crea una nueva solicitud externa de donaciones"""
        query = """
            INSERT INTO solicitudes_externas (organizacion_solicitante, solicitud_id, donaciones)
            VALUES (%s, %s, %s)
            ON CONFLICT (organizacion_solicitante, solicitud_id) 
            DO UPDATE SET donaciones = EXCLUDED.donaciones, fecha_creacion = CURRENT_TIMESTAMP
            RETURNING id, organizacion_solicitante, solicitud_id, donaciones, activa, fecha_creacion
        """
        return self._execute_query(
            query, 
            (organizacion_solicitante, solicitud_id, json.dumps(donaciones)), 
            fetch_one=True, 
            commit=True
        )
    
    def get_active_external_requests(self) -> List[Dict]:
        """Obtiene todas las solicitudes externas activas"""
        query = """
            SELECT id, organizacion_solicitante, solicitud_id, donaciones, fecha_creacion
            FROM solicitudes_externas 
            WHERE activa = true 
            ORDER BY fecha_creacion DESC
        """
        return self._execute_query(query, fetch_all=True) or []
    
    def get_external_request_by_id(self, organizacion_solicitante: str, solicitud_id: str) -> Optional[Dict]:
        """Obtiene una solicitud específica por organización y ID"""
        query = """
            SELECT id, organizacion_solicitante, solicitud_id, donaciones, activa, fecha_creacion
            FROM solicitudes_externas 
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """
        return self._execute_query(query, (organizacion_solicitante, solicitud_id), fetch_one=True)
    
    def deactivate_external_request(self, organizacion_solicitante: str, solicitud_id: str) -> bool:
        """Desactiva una solicitud externa (cuando se da de baja)"""
        query = """
            UPDATE solicitudes_externas 
            SET activa = false
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """
        result = self._execute_query(query, (organizacion_solicitante, solicitud_id), commit=True)
        return result is not None and result > 0
    
    def get_requests_by_category(self, categoria: str) -> List[Dict]:
        """Obtiene solicitudes externas filtradas por categoría de donación"""
        query = """
            SELECT id, organizacion_solicitante, solicitud_id, donaciones, fecha_creacion
            FROM solicitudes_externas 
            WHERE activa = true 
            AND donaciones::text LIKE %s
            ORDER BY fecha_creacion DESC
        """
        # Buscar la categoría en el JSON de donaciones
        search_pattern = f'%"categoria": "{categoria}"%'
        return self._execute_query(query, (search_pattern,), fetch_all=True) or []
    
    def cleanup_old_requests(self, days_old: int = 30) -> int:
        """Limpia solicitudes externas antiguas (más de X días)"""
        query = """
            DELETE FROM solicitudes_externas 
            WHERE fecha_creacion < CURRENT_TIMESTAMP - INTERVAL '%s days'
            AND activa = false
        """
        result = self._execute_query(query, (days_old,), commit=True)
        return result if result is not None else 0

    # ==================== VALIDACIONES PARA TRANSFERENCIAS ====================
    
    def can_fulfill_request(self, solicitud_id: int, donaciones_solicitadas: List[Dict]) -> Dict:
        """Verifica si podemos cumplir con una solicitud externa"""
        result = {
            'can_fulfill': True,
            'available_items': [],
            'missing_items': [],
            'partial_items': []
        }
        
        for donacion in donaciones_solicitadas:
            categoria = donacion.get('categoria')
            descripcion = donacion.get('descripcion', '')
            cantidad_solicitada = donacion.get('cantidad', 1)
            
            # Buscar donaciones disponibles en nuestro inventario
            query = """
                SELECT id, descripcion, cantidad
                FROM donaciones 
                WHERE categoria = %s 
                AND eliminado = false 
                AND cantidad > 0
                AND descripcion ILIKE %s
                ORDER BY cantidad DESC
            """
            
            available = self._execute_query(
                query, 
                (categoria, f'%{descripcion}%'), 
                fetch_all=True
            ) or []
            
            total_available = sum(item['cantidad'] for item in available)
            
            if total_available >= cantidad_solicitada:
                result['available_items'].append({
                    'categoria': categoria,
                    'descripcion': descripcion,
                    'cantidad_solicitada': cantidad_solicitada,
                    'cantidad_disponible': total_available,
                    'items': available
                })
            elif total_available > 0:
                result['partial_items'].append({
                    'categoria': categoria,
                    'descripcion': descripcion,
                    'cantidad_solicitada': cantidad_solicitada,
                    'cantidad_disponible': total_available,
                    'items': available
                })
                result['can_fulfill'] = False
            else:
                result['missing_items'].append({
                    'categoria': categoria,
                    'descripcion': descripcion,
                    'cantidad_solicitada': cantidad_solicitada
                })
                result['can_fulfill'] = False
        
        return result
    
    def reserve_items_for_transfer(self, items_to_reserve: List[Dict]) -> bool:
        """Reserva items del inventario para una transferencia"""
        try:
            conn = self.db.connect()
            cursor = self.db.get_cursor()
            
            for item in items_to_reserve:
                donacion_id = item['donacion_id']
                cantidad_reservar = item['cantidad']
                
                # Verificar disponibilidad actual
                check_query = """
                    SELECT cantidad FROM donaciones 
                    WHERE id = %s AND eliminado = false
                """
                cursor.execute(check_query, (donacion_id,))
                current = cursor.fetchone()
                
                if not current or current['cantidad'] < cantidad_reservar:
                    conn.rollback()
                    return False
                
                # Descontar la cantidad
                update_query = """
                    UPDATE donaciones 
                    SET cantidad = cantidad - %s,
                        fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                cursor.execute(update_query, (cantidad_reservar, donacion_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error reservando items: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.db.close()

    # ==================== ESTADÍSTICAS ====================
    
    def get_requests_statistics(self) -> Dict:
        """Obtiene estadísticas de solicitudes externas"""
        stats = {
            'total_active': 0,
            'total_inactive': 0,
            'by_organization': {},
            'by_category': {}
        }
        
        # Total de solicitudes activas e inactivas
        query = """
            SELECT activa, COUNT(*) as count
            FROM solicitudes_externas
            GROUP BY activa
        """
        results = self._execute_query(query, fetch_all=True) or []
        
        for result in results:
            if result['activa']:
                stats['total_active'] = result['count']
            else:
                stats['total_inactive'] = result['count']
        
        # Por organización
        query = """
            SELECT organizacion_solicitante, COUNT(*) as count
            FROM solicitudes_externas
            WHERE activa = true
            GROUP BY organizacion_solicitante
            ORDER BY count DESC
        """
        org_results = self._execute_query(query, fetch_all=True) or []
        stats['by_organization'] = {r['organizacion_solicitante']: r['count'] for r in org_results}
        
        return stats