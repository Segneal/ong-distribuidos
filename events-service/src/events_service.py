"""
Events gRPC Service Implementation
"""
import grpc
from concurrent import futures
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

import events_pb2
import events_pb2_grpc
from events_repository import EventsRepository
from datetime import datetime

class EventsService(events_pb2_grpc.EventsServiceServicer):
    """gRPC service for events management"""
    
    def __init__(self):
        self.repository = EventsRepository()
    
    def _create_event_message(self, event_data):
        """Create Event message from database data"""
        return events_pb2.Event(
            id=event_data['id'],
            name=event_data['nombre'],
            description=event_data.get('descripcion', ''),
            event_date=str(event_data['fecha_evento']),
            created_at=str(event_data['fecha_creacion']),
            updated_at=str(event_data.get('fecha_actualizacion', ''))
        )
    
    def _create_participant_message(self, participant_data):
        """Create Participant message from database data"""
        return events_pb2.Participant(
            event_id=participant_data.get('evento_id', 0),
            user_id=participant_data['id'],
            user_name=participant_data['nombre'],
            user_last_name=participant_data['apellido'],
            adhesion_date=str(participant_data['fecha_adhesion'])
        )
    
    def _create_distributed_donation_message(self, donation_data):
        """Create DistributedDonation message from database data"""
        registered_by_name = ""
        if donation_data.get('registered_by_name') and donation_data.get('registered_by_lastname'):
            registered_by_name = f"{donation_data['registered_by_name']} {donation_data['registered_by_lastname']}"
        
        return events_pb2.DistributedDonation(
            id=donation_data.get('id', 0),
            event_id=donation_data['event_id'],
            donation_id=donation_data['donation_id'],
            donation_description=donation_data.get('donation_description', ''),
            distributed_quantity=donation_data['distributed_quantity'],
            registered_by=donation_data['registered_by'],
            registration_date=str(donation_data.get('registration_date', datetime.now())),
            registered_by_name=registered_by_name
        )
    
    def CreateEvent(self, request, context):
        """Create a new event"""
        try:
            # Validate required fields
            if not request.name.strip():
                return events_pb2.EventResponse(
                    success=False,
                    message="El nombre del evento es requerido"
                )
            
            if not request.event_date.strip():
                return events_pb2.EventResponse(
                    success=False,
                    message="La fecha del evento es requerida"
                )
            
            # Validate future date
            try:
                event_datetime = datetime.fromisoformat(request.event_date.replace('Z', '+00:00'))
                if event_datetime <= datetime.now():
                    return events_pb2.EventResponse(
                        success=False,
                        message="La fecha del evento debe ser futura"
                    )
            except ValueError:
                return events_pb2.EventResponse(
                    success=False,
                    message="Formato de fecha inválido"
                )
            
            # Create event
            participant_ids = list(request.participant_ids) if request.participant_ids else None
            event_data = self.repository.create_event(
                request.name,
                request.description,
                request.event_date,
                participant_ids
            )
            
            if event_data:
                event_message = self._create_event_message(event_data)
                return events_pb2.EventResponse(
                    success=True,
                    message="Evento creado exitosamente",
                    event=event_message
                )
            else:
                return events_pb2.EventResponse(
                    success=False,
                    message="Error creando el evento"
                )
                
        except Exception as e:
            print(f"Error en CreateEvent: {e}")
            return events_pb2.EventResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def GetEvent(self, request, context):
        """Get event by ID"""
        try:
            event_data = self.repository.get_event_by_id(request.id)
            
            if event_data:
                event_message = self._create_event_message(event_data)
                return events_pb2.EventResponse(
                    success=True,
                    message="Evento encontrado",
                    event=event_message
                )
            else:
                return events_pb2.EventResponse(
                    success=False,
                    message="Evento no encontrado"
                )
                
        except Exception as e:
            print(f"Error en GetEvent: {e}")
            return events_pb2.EventResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def UpdateEvent(self, request, context):
        """Update an existing event"""
        try:
            # Validate required fields
            if not request.name.strip():
                return events_pb2.EventResponse(
                    success=False,
                    message="El nombre del evento es requerido"
                )
            
            # Validate future date
            try:
                event_datetime = datetime.fromisoformat(request.event_date.replace('Z', '+00:00'))
                if event_datetime <= datetime.now():
                    return events_pb2.EventResponse(
                        success=False,
                        message="La fecha del evento debe ser futura"
                    )
            except ValueError:
                return events_pb2.EventResponse(
                    success=False,
                    message="Formato de fecha inválido"
                )
            
            # Check if event exists
            existing_event = self.repository.get_event_by_id(request.id)
            if not existing_event:
                return events_pb2.EventResponse(
                    success=False,
                    message="Evento no encontrado"
                )
            
            # Update event
            event_data = self.repository.update_event(
                request.id,
                request.name,
                request.description,
                request.event_date
            )
            
            if event_data:
                event_message = self._create_event_message(event_data)
                return events_pb2.EventResponse(
                    success=True,
                    message="Evento actualizado exitosamente",
                    event=event_message
                )
            else:
                return events_pb2.EventResponse(
                    success=False,
                    message="Error actualizando el evento"
                )
                
        except Exception as e:
            print(f"Error en UpdateEvent: {e}")
            return events_pb2.EventResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def DeleteEvent(self, request, context):
        """Delete event (only future events)"""
        try:
            success = self.repository.delete_event(request.id)
            
            if success:
                return events_pb2.DeleteEventResponse(
                    success=True,
                    message="Evento eliminado exitosamente"
                )
            else:
                return events_pb2.DeleteEventResponse(
                    success=False,
                    message="No se puede eliminar el evento (no existe o es un evento pasado)"
                )
                
        except Exception as e:
            print(f"Error en DeleteEvent: {e}")
            return events_pb2.DeleteEventResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def ListEvents(self, request, context):
        """List events with optional filters"""
        try:
            include_past = request.include_past_events if hasattr(request, 'include_past_events') else True
            user_id = request.user_id if hasattr(request, 'user_id') and request.user_id > 0 else None
            
            events_data = self.repository.list_events(include_past, user_id)
            
            events_messages = []
            for event_data in events_data:
                event_message = self._create_event_message(event_data)
                events_messages.append(event_message)
            
            return events_pb2.ListEventsResponse(
                success=True,
                message=f"Se encontraron {len(events_messages)} eventos",
                events=events_messages
            )
            
        except Exception as e:
            print(f"Error en ListEvents: {e}")
            return events_pb2.ListEventsResponse(
                success=False,
                message="Error interno del servidor",
                events=[]
            )
    
    def AddParticipant(self, request, context):
        """Add participant to event"""
        try:
            # Check if event exists
            event_data = self.repository.get_event_by_id(request.event_id)
            if not event_data:
                return events_pb2.ParticipantResponse(
                    success=False,
                    message="Evento no encontrado"
                )
            
            success = self.repository.add_participant(request.event_id, request.user_id)
            
            if success:
                # Get participant data for response
                participants = self.repository.list_participants(request.event_id)
                participant_data = next((p for p in participants if p['id'] == request.user_id), None)
                
                if participant_data:
                    participant_data['evento_id'] = request.event_id
                    participant_message = self._create_participant_message(participant_data)
                    return events_pb2.ParticipantResponse(
                        success=True,
                        message="Participante agregado exitosamente",
                        participant=participant_message
                    )
                else:
                    return events_pb2.ParticipantResponse(
                        success=True,
                        message="Participante agregado exitosamente"
                    )
            else:
                return events_pb2.ParticipantResponse(
                    success=False,
                    message="Error agregando participante (usuario inactivo o ya participa)"
                )
                
        except Exception as e:
            print(f"Error en AddParticipant: {e}")
            return events_pb2.ParticipantResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def RemoveParticipant(self, request, context):
        """Remove participant from event"""
        try:
            success = self.repository.remove_participant(request.event_id, request.user_id)
            
            if success:
                return events_pb2.ParticipantResponse(
                    success=True,
                    message="Participante removido exitosamente"
                )
            else:
                return events_pb2.ParticipantResponse(
                    success=False,
                    message="Participante no encontrado en el evento"
                )
                
        except Exception as e:
            print(f"Error en RemoveParticipant: {e}")
            return events_pb2.ParticipantResponse(
                success=False,
                message="Error interno del servidor"
            )
    
    def ListParticipants(self, request, context):
        """List event participants"""
        try:
            participants_data = self.repository.list_participants(request.event_id)
            
            participants_messages = []
            for participant_data in participants_data:
                participant_data['evento_id'] = request.event_id
                participant_message = self._create_participant_message(participant_data)
                participants_messages.append(participant_message)
            
            return events_pb2.ListParticipantsResponse(
                success=True,
                message=f"Se encontraron {len(participants_messages)} participantes",
                participants=participants_messages
            )
            
        except Exception as e:
            print(f"Error en ListParticipants: {e}")
            return events_pb2.ListParticipantsResponse(
                success=False,
                message="Error interno del servidor",
                participants=[]
            )
    
    def RegisterDistributedDonations(self, request, context):
        """Register donations distributed in a past event"""
        try:
            # Validate donations data
            if not request.donations:
                return events_pb2.RegisterDistributedDonationsResponse(
                    success=False,
                    message="No se especificaron donaciones para repartir"
                )
            
            # Convert donations to dict format
            donations_data = []
            for donation in request.donations:
                donations_data.append({
                    'donation_id': donation.donation_id,
                    'quantity': donation.quantity
                })
            
            # Register distributed donations
            distributed_donations = self.repository.register_distributed_donations(
                request.event_id,
                donations_data,
                request.registered_by
            )
            
            if distributed_donations:
                # Create response messages
                distributed_messages = []
                for donation_data in distributed_donations:
                    distributed_message = self._create_distributed_donation_message(donation_data)
                    distributed_messages.append(distributed_message)
                
                return events_pb2.RegisterDistributedDonationsResponse(
                    success=True,
                    message=f"Se registraron {len(distributed_messages)} donaciones repartidas",
                    distributed_donations=distributed_messages
                )
            else:
                return events_pb2.RegisterDistributedDonationsResponse(
                    success=False,
                    message="No se pudieron registrar las donaciones (evento futuro o donaciones inválidas)"
                )
                
        except Exception as e:
            print(f"Error en RegisterDistributedDonations: {e}")
            return events_pb2.RegisterDistributedDonationsResponse(
                success=False,
                message="Error interno del servidor",
                distributed_donations=[]
            )
    
    def GetDistributedDonations(self, request, context):
        """Get donations distributed in an event"""
        try:
            distributed_donations = self.repository.get_distributed_donations(request.event_id)
            
            distributed_messages = []
            for donation_data in distributed_donations:
                distributed_message = self._create_distributed_donation_message(donation_data)
                distributed_messages.append(distributed_message)
            
            return events_pb2.GetDistributedDonationsResponse(
                success=True,
                message=f"Se encontraron {len(distributed_messages)} donaciones repartidas",
                distributed_donations=distributed_messages
            )
            
        except Exception as e:
            print(f"Error en GetDistributedDonations: {e}")
            return events_pb2.GetDistributedDonationsResponse(
                success=False,
                message="Error interno del servidor",
                distributed_donations=[]
            )


def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    events_pb2_grpc.add_EventsServiceServicer_to_server(EventsService(), server)
    
    port = os.getenv('EVENTS_SERVICE_PORT', '50053')
    server.add_insecure_port(f'0.0.0.0:{port}')
    
    server.start()
    print(f"✅ Servidor gRPC de eventos iniciado en puerto {port}")
    print(f"🌐 Escuchando en 0.0.0.0:{port}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("🛑 Deteniendo servidor...")
        server.stop(0)


if __name__ == '__main__':
    serve()