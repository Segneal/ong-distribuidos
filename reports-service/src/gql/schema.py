"""
GraphQL Schema definition using Strawberry
"""
import strawberry
from typing import List, Optional
from .types.user import UserType
from .types.donation import DonationType, DonationReportType, DonationFilterInput
from .types.event import EventType, EventParticipationReportType, EventFilterInput
from .types.filter import SavedFilterType, SavedFilterInput
from .resolvers.donation_resolvers import DonationResolver
from .resolvers.event_resolvers import EventResolver
from .resolvers.filter_resolvers import FilterResolver


@strawberry.type
class Query:
    """GraphQL Query root"""
    
    # Donation queries
    donation_report: List[DonationReportType] = strawberry.field(resolver=DonationResolver.get_donation_report)
    
    # Event queries
    event_participation_report: List[EventParticipationReportType] = strawberry.field(resolver=EventResolver.get_event_participation_report)
    
    # Filter queries
    saved_donation_filters: List[SavedFilterType] = strawberry.field(resolver=FilterResolver.get_saved_donation_filters)


@strawberry.type
class Mutation:
    """GraphQL Mutation root"""
    
    # Filter mutations
    save_donation_filter: SavedFilterType = strawberry.field(resolver=FilterResolver.save_donation_filter)
    update_donation_filter: SavedFilterType = strawberry.field(resolver=FilterResolver.update_donation_filter)
    delete_donation_filter: bool = strawberry.field(resolver=FilterResolver.delete_donation_filter)


# Create the GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)