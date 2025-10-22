"""
SOAP data schemas and models for network consultation.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PresidentData(BaseModel):
    """Model for president data from SOAP service."""
    organization_id: Optional[int] = Field(None, description="ID of the organization")
    president_name: Optional[str] = Field(None, description="Name of the president")
    president_email: Optional[str] = Field(None, description="Email of the president")
    president_phone: Optional[str] = Field(None, description="Phone number of the president")
    president_id: Optional[int] = Field(None, description="ID of the president")
    start_date: Optional[str] = Field(None, description="Start date of presidency")
    status: Optional[str] = Field(None, description="Status of the president")


class OrganizationData(BaseModel):
    """Model for organization data from SOAP service."""
    organization_id: Optional[int] = Field(None, description="ID of the organization")
    organization_name: Optional[str] = Field(None, description="Name of the organization")
    organization_type: Optional[str] = Field(None, description="Type of organization")
    address: Optional[str] = Field(None, description="Address of the organization")
    city: Optional[str] = Field(None, description="City where organization is located")
    country: Optional[str] = Field(None, description="Country where organization is located")
    phone: Optional[str] = Field(None, description="Phone number of the organization")
    email: Optional[str] = Field(None, description="Email of the organization")
    website: Optional[str] = Field(None, description="Website of the organization")
    registration_date: Optional[str] = Field(None, description="Registration date")
    status: Optional[str] = Field(None, description="Status of the organization")
    description: Optional[str] = Field(None, description="Description of the organization")


class NetworkConsultationRequest(BaseModel):
    """Request model for network consultation."""
    organization_ids: List[int] = Field(..., description="List of organization IDs to query", min_items=1)


class NetworkConsultationResponse(BaseModel):
    """Response model for network consultation."""
    presidents: List[PresidentData] = Field(default_factory=list, description="List of president data")
    organizations: List[OrganizationData] = Field(default_factory=list, description="List of organization data")
    query_ids: List[int] = Field(default_factory=list, description="Original query IDs")
    total_presidents: int = Field(0, description="Total number of presidents found")
    total_organizations: int = Field(0, description="Total number of organizations found")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")


class SOAPErrorResponse(BaseModel):
    """Error response model for SOAP operations."""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code if available")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")