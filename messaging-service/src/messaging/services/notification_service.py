"""
Notification Service for managing user notifications
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

from ..database.connection import get_database_connection
from ..config import settings

logger = structlog.get_logger(__name__)


class NotificationService:
    """Service for managing user notifications"""
    
    def __init__(self):
        self.organization_id = settings.organization_id
    
    def create_notification(self, user_id: int, title: str, message: str, 
                          notification_type: str = 'INFO') -> bool:
        """
        Create a notification for a specific user
        
        Args:
            user_id: ID of the user to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification (INFO, WARNING, ERROR, SUCCESS)
            
        Returns:
            True if notification was created successfully
        """
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO notificaciones_usuarios 
                    (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
                    VALUES (%s, %s, %s, %s, NOW(), false)
                """, (user_id, title, message, notification_type))
                
                conn.commit()
                
                logger.info(
                    "Notification created",
                    user_id=user_id,
                    title=title,
                    type=notification_type
                )
                
                return True
                
        except Exception as e:
            logger.error("Error creating notification", error=str(e))
            return False
    
    def create_notification_for_organization_admins(self, title: str, message: str, 
                                                  notification_type: str = 'INFO') -> bool:
        """
        Create notifications for all organization administrators
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            
        Returns:
            True if notifications were created successfully
        """
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Get all administrators (PRESIDENTE, VOCAL) of the organization
                cursor.execute("""
                    SELECT id FROM usuarios 
                    WHERE organizacion = %s 
                    AND rol IN ('PRESIDENTE', 'VOCAL')
                    AND activo = true
                """, (self.organization_id,))
                
                admin_users = cursor.fetchall()
                
                if not admin_users:
                    logger.warning("No administrators found for organization", org=self.organization_id)
                    return False
                
                # Create notification for each admin
                for (user_id,) in admin_users:
                    cursor.execute("""
                        INSERT INTO notificaciones_usuarios 
                        (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
                        VALUES (%s, %s, %s, %s, NOW(), false)
                    """, (user_id, title, message, notification_type))
                
                conn.commit()
                
                logger.info(
                    "Notifications created for organization admins",
                    org=self.organization_id,
                    admin_count=len(admin_users),
                    title=title
                )
                
                return True
                
        except Exception as e:
            logger.error("Error creating notifications for admins", error=str(e))
            return False
    
    def notify_new_event_adhesion(self, event_id: str, volunteer_name: str, 
                                volunteer_email: str, volunteer_org: str) -> bool:
        """
        Notify event administrators about a new event adhesion
        
        Args:
            event_id: ID of the event
            volunteer_name: Name of the volunteer
            volunteer_email: Email of the volunteer
            volunteer_org: Organization of the volunteer
            
        Returns:
            True if notification was sent
        """
        try:
            # Get event name and find administrators who can manage events
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Get event name
                cursor.execute("""
                    SELECT nombre FROM eventos WHERE id = %s
                """, (event_id,))
                
                event_row = cursor.fetchone()
                event_name = event_row[0] if event_row else f"Evento {event_id}"
                
                # Get users who can manage events (PRESIDENTE, COORDINADOR)
                cursor.execute("""
                    SELECT id FROM usuarios 
                    WHERE organizacion = %s 
                    AND rol IN ('PRESIDENTE', 'COORDINADOR')
                    AND activo = true
                """, (self.organization_id,))
                
                event_admins = cursor.fetchall()
                
                if not event_admins:
                    logger.warning("No event administrators found for organization", org=self.organization_id)
                    return False
                
                # Create notification for each event admin
                title = "🎯 Nueva solicitud de adhesión a evento"
                message = f"{volunteer_name} ({volunteer_org}) quiere participar en '{event_name}'. Ve a 'Gestión de Adhesiones' para aprobar o rechazar la solicitud."
                
                for (user_id,) in event_admins:
                    cursor.execute("""
                        INSERT INTO notificaciones_usuarios 
                        (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
                        VALUES (%s, %s, %s, %s, NOW(), false)
                    """, (user_id, title, message, 'INFO'))
                
                conn.commit()
                
                logger.info(
                    "Notifications created for event administrators",
                    org=self.organization_id,
                    admin_count=len(event_admins),
                    event_name=event_name,
                    volunteer_name=volunteer_name,
                    volunteer_org=volunteer_org
                )
                
                return True
            
        except Exception as e:
            logger.error("Error notifying new event adhesion", error=str(e))
            return False
    
    def notify_adhesion_approved(self, user_id: int, event_name: str) -> bool:
        """
        Notify user that their event adhesion was approved
        
        Args:
            user_id: ID of the user
            event_name: Name of the event
            
        Returns:
            True if notification was sent
        """
        title = "Adhesión a evento aprobada"
        message = f"¡Genial! Tu solicitud para participar en '{event_name}' ha sido aprobada. ¡Nos vemos en el evento!"
        
        return self.create_notification(user_id, title, message, 'SUCCESS')
    
    def notify_adhesion_rejected(self, user_id: int, event_name: str, reason: str = None) -> bool:
        """
        Notify user that their event adhesion was rejected
        
        Args:
            user_id: ID of the user
            event_name: Name of the event
            reason: Reason for rejection
            
        Returns:
            True if notification was sent
        """
        title = "Adhesión a evento rechazada"
        message = f"Tu solicitud para participar en '{event_name}' no fue aprobada."
        if reason:
            message += f" Motivo: {reason}"
        
        return self.create_notification(user_id, title, message, 'WARNING')
    
    def notify_event_cancelled(self, event_name: str, reason: str = None) -> bool:
        """
        Notify organization admins about event cancellation
        
        Args:
            event_name: Name of the cancelled event
            reason: Reason for cancellation
            
        Returns:
            True if notification was sent
        """
        title = "Evento cancelado"
        message = f"El evento '{event_name}' ha sido cancelado."
        if reason:
            message += f" Motivo: {reason}"
        
        return self.create_notification_for_organization_admins(
            title, message, 'ERROR'
        )
    
    def notify_donation_received(self, donation_details: str, sender_org: str) -> bool:
        """
        Notify organization admins about received donation
        
        Args:
            donation_details: Details of the donation
            sender_org: Organization that sent the donation
            
        Returns:
            True if notification was sent
        """
        title = "Donación recibida"
        message = f"Has recibido una donación de {sender_org}: {donation_details}"
        
        return self.create_notification_for_organization_admins(
            title, message, 'SUCCESS'
        )
    
    def notify_donation_request_received(self, request_details: str, requesting_org: str) -> bool:
        """
        Notify organization admins about new donation request
        
        Args:
            request_details: Details of the request
            requesting_org: Organization making the request
            
        Returns:
            True if notification was sent
        """
        title = "Nueva solicitud de donación"
        message = f"{requesting_org} solicita: {request_details}. Revisa las solicitudes externas para responder."
        
        return self.create_notification_for_organization_admins(
            title, message, 'INFO'
        )