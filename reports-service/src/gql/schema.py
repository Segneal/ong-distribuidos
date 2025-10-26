"""
GraphQL Schema definition using Strawberry
"""
import strawberry
from typing import List, Optional
from .types.user import UserType
from .types.donation import DonationType, DonationReportType, DonationFilterInput
from .types.event import EventType, EventParticipationReportType, EventFilterInput, SavedEventFilterType
from .types.filter import SavedFilterType, SavedFilterInput
from .types.transfer import TransferReportType, DonationTransferType, SavedTransferFilterType, TransferFilterInput
from .resolvers.donation_resolvers import DonationResolver
from .resolvers.event_resolvers import EventResolver
from .resolvers.filter_resolvers import FilterResolver
from .resolvers.transfer_resolvers import TransferResolver
from .resolvers.soap_resolvers import SOAPResolver
from .types.soap import NetworkConsultationType, PresidentType, OrganizationType, SOAPConnectionTestType


@strawberry.type
class Query:
    """GraphQL Query root"""
    
    # Donation queries
    donation_report: List[DonationReportType] = strawberry.field(resolver=DonationResolver.get_donation_report)
    
    # Transfer queries
    transfer_report: List[TransferReportType] = strawberry.field(resolver=TransferResolver.get_transfer_report)
    saved_transfer_filters: List[SavedTransferFilterType] = strawberry.field(resolver=TransferResolver.get_saved_transfer_filters)
    
    # Event queries
    event_participation_report: List[EventParticipationReportType] = strawberry.field(resolver=EventResolver.get_event_participation_report)
    saved_event_filters: List[SavedEventFilterType] = strawberry.field(resolver=EventResolver.get_saved_event_filters)
    # organization_users: List[UserType] = strawberry.field(resolver=EventResolver.get_organization_users)  # Temporarily disabled
    
    # Filter queries
    saved_donation_filters: List[SavedFilterType] = strawberry.field(resolver=FilterResolver.get_saved_donation_filters)
    
    # SOAP queries
    network_consultation: NetworkConsultationType = strawberry.field(resolver=SOAPResolver.network_consultation)
    presidents_only: List[PresidentType] = strawberry.field(resolver=SOAPResolver.presidents_only)
    organizations_only: List[OrganizationType] = strawberry.field(resolver=SOAPResolver.organizations_only)
    soap_connection_test: SOAPConnectionTestType = strawberry.field(resolver=SOAPResolver.soap_connection_test)


@strawberry.type
class Mutation:
    """GraphQL Mutation root"""
    
    # Filter mutations
    save_donation_filter: SavedFilterType = strawberry.field(resolver=FilterResolver.save_donation_filter)
    update_donation_filter: SavedFilterType = strawberry.field(resolver=FilterResolver.update_donation_filter)
    delete_donation_filter: bool = strawberry.field(resolver=FilterResolver.delete_donation_filter)
    
    # Event filter mutations
    save_event_filter: SavedEventFilterType = strawberry.field(resolver=EventResolver.save_event_filter)
    update_event_filter: SavedEventFilterType = strawberry.field(resolver=EventResolver.update_event_filter)
    delete_event_filter: bool = strawberry.field(resolver=EventResolver.delete_event_filter)
    
    # Transfer filter mutations
    save_transfer_filter: SavedTransferFilterType = strawberry.field(resolver=TransferResolver.save_transfer_filter)
    update_transfer_filter: SavedTransferFilterType = strawberry.field(resolver=TransferResolver.update_transfer_filter)
    delete_transfer_filter: bool = strawberry.field(resolver=TransferResolver.delete_transfer_filter)


# Create the GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)