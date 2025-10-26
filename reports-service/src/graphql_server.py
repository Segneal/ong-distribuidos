"""
Alternative GraphQL server using Graphene (compatible with Python 3.13)
"""
import graphene
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from graphql import build_schema, execute

# Mock data
MOCK_DONATIONS = [
    {
        "id": "1",
        "categoria": "ALIMENTOS",
        "cantidad": 150,
        "fechaDonacion": "2024-01-15",
        "fechaAlta": "2024-01-15",
        "descripcion": "Donación de alimentos no perecederos",
        "estado": "ENTREGADA",
        "eliminado": False,
        "usuarioAlta": "admin",
        "dia": 15
    },
    {
        "id": "2",
        "categoria": "ROPA", 
        "cantidad": 75,
        "fechaDonacion": "2024-01-20",
        "fechaAlta": "2024-01-20",
        "descripcion": "Donación de ropa de invierno",
        "estado": "PENDIENTE",
        "eliminado": False,
        "usuarioAlta": "admin",
        "dia": 20
    }
]

MOCK_EVENTS = [
    {
        "id": "1",
        "nombre": "Campaña de Donación de Alimentos",
        "fecha": "2024-01-15",
        "participantes": [
            {"id": "1", "nombre": "Ana López", "email": "ana@example.com", "rol": "VOLUNTARIO"}
        ],
        "donaciones": MOCK_DONATIONS[:1]
    }
]

# SOAP Types
class PresidentType(graphene.ObjectType):
    organization_id = graphene.Int()
    president_name = graphene.String()
    president_email = graphene.String()
    president_phone = graphene.String()
    president_id = graphene.Int()
    president_address = graphene.String()
    start_date = graphene.String()
    status = graphene.String()

class OrganizationType(graphene.ObjectType):
    organization_id = graphene.Int()
    organization_name = graphene.String()
    organization_type = graphene.String()
    address = graphene.String()
    city = graphene.String()
    country = graphene.String()
    phone = graphene.String()
    email = graphene.String()
    website = graphene.String()
    registration_date = graphene.String()
    status = graphene.String()
    description = graphene.String()

class NetworkConsultationType(graphene.ObjectType):
    presidents = graphene.List(PresidentType)
    organizations = graphene.List(OrganizationType)
    query_ids = graphene.List(graphene.Int)
    total_presidents = graphene.Int()
    total_organizations = graphene.Int()
    errors = graphene.List(graphene.String)

class SOAPConnectionTestType(graphene.ObjectType):
    connected = graphene.Boolean()
    service_url = graphene.String()
    message = graphene.String()

# GraphQL Types
class DonationType(graphene.ObjectType):
    id = graphene.String()
    categoria = graphene.String()
    cantidad = graphene.Int()
    fecha_donacion = graphene.String()
    fecha_alta = graphene.String()
    descripcion = graphene.String()
    estado = graphene.String()
    eliminado = graphene.Boolean()
    usuario_alta = graphene.String()
    dia = graphene.Int()

class DonationGroupType(graphene.ObjectType):
    categoria = graphene.String()
    eliminado = graphene.Boolean()
    registros = graphene.List(DonationType)
    total_cantidad = graphene.Int()

class ParticipantType(graphene.ObjectType):
    id = graphene.String()
    nombre = graphene.String()
    email = graphene.String()
    rol = graphene.String()

class EventType(graphene.ObjectType):
    id = graphene.String()
    nombre = graphene.String()
    fecha = graphene.String()
    participantes = graphene.List(ParticipantType)
    donaciones = graphene.List(DonationType)

class MonthEventType(graphene.ObjectType):
    mes = graphene.String()
    mes_nombre = graphene.String()
    eventos = graphene.List(EventType)

class FilterInputType(graphene.ObjectType):
    categoria = graphene.String()
    fecha_desde = graphene.String()
    fecha_hasta = graphene.String()
    eliminado = graphene.Boolean()

class SavedFilterType(graphene.ObjectType):
    id = graphene.String()
    nombre = graphene.String()
    filtros = graphene.Field(FilterInputType)
    fecha_creacion = graphene.String()

# Queries
class Query(graphene.ObjectType):
    donation_report = graphene.List(DonationGroupType)
    event_participation_report = graphene.List(MonthEventType)
    saved_donation_filters = graphene.List(SavedFilterType)
    
    # SOAP Queries
    network_consultation = graphene.Field(
        NetworkConsultationType,
        organization_ids=graphene.List(graphene.Int, required=True)
    )
    presidents_only = graphene.List(
        PresidentType,
        organization_ids=graphene.List(graphene.Int, required=True)
    )
    organizations_only = graphene.List(
        OrganizationType,
        organization_ids=graphene.List(graphene.Int, required=True)
    )
    soap_connection_test = graphene.Field(SOAPConnectionTestType)
    
    def resolve_donation_report(self, info):
        # Group donations by category
        groups = {}
        for donation in MOCK_DONATIONS:
            key = f"{donation['categoria']}-{donation['eliminado']}"
            if key not in groups:
                groups[key] = {
                    "categoria": donation["categoria"],
                    "eliminado": donation["eliminado"],
                    "registros": [],
                    "total_cantidad": 0
                }
            groups[key]["registros"].append(donation)
            groups[key]["total_cantidad"] += donation["cantidad"]
        
        return list(groups.values())
    
    def resolve_event_participation_report(self, info):
        return [
            {
                "mes": "2024-01",
                "mes_nombre": "Enero 2024",
                "eventos": MOCK_EVENTS
            }
        ]
    
    def resolve_saved_donation_filters(self, info):
        return [
            {
                "id": "1",
                "nombre": "Filtro Alimentos",
                "filtros": {
                    "categoria": "ALIMENTOS",
                    "fecha_desde": "2024-01-01",
                    "fecha_hasta": None,
                    "eliminado": False
                },
                "fecha_creacion": "2024-01-10"
            },
            {
                "id": "2", 
                "nombre": "Filtro Ropa",
                "filtros": {
                    "categoria": "ROPA",
                    "fecha_desde": "2024-01-15",
                    "fecha_hasta": "2024-01-31",
                    "eliminado": False
                },
                "fecha_creacion": "2024-01-12"
            }
        ]
    
    # SOAP Resolvers
    def resolve_network_consultation(self, info, organization_ids):
        try:
            from .services.soap_service import get_soap_service
            
            soap_service = get_soap_service()
            response = soap_service.get_network_consultation(organization_ids)
            
            return {
                "presidents": [
                    {
                        "organization_id": p.organization_id,
                        "president_name": p.president_name,
                        "president_email": p.president_email,
                        "president_phone": p.president_phone,
                        "president_id": p.president_id,
                        "president_address": getattr(p, 'president_address', None),
                        "start_date": p.start_date,
                        "status": p.status
                    } for p in response.presidents
                ],
                "organizations": [
                    {
                        "organization_id": o.organization_id,
                        "organization_name": o.organization_name,
                        "organization_type": o.organization_type,
                        "address": o.address,
                        "city": o.city,
                        "country": o.country,
                        "phone": o.phone,
                        "email": o.email,
                        "website": o.website,
                        "registration_date": o.registration_date,
                        "status": o.status,
                        "description": o.description
                    } for o in response.organizations
                ],
                "query_ids": response.query_ids,
                "total_presidents": response.total_presidents,
                "total_organizations": response.total_organizations,
                "errors": response.errors
            }
        except Exception as e:
            return {
                "presidents": [],
                "organizations": [],
                "query_ids": organization_ids,
                "total_presidents": 0,
                "total_organizations": 0,
                "errors": [str(e)]
            }
    
    def resolve_presidents_only(self, info, organization_ids):
        try:
            from .services.soap_service import get_soap_service
            
            soap_service = get_soap_service()
            presidents = soap_service.get_president_data_only(organization_ids)
            
            return [
                {
                    "organization_id": p.organization_id,
                    "president_name": p.president_name,
                    "president_email": p.president_email,
                    "president_phone": p.president_phone,
                    "president_id": p.president_id,
                    "president_address": getattr(p, 'president_address', None),
                    "start_date": p.start_date,
                    "status": p.status
                } for p in presidents
            ]
        except Exception as e:
            return []
    
    def resolve_organizations_only(self, info, organization_ids):
        try:
            from .services.soap_service import get_soap_service
            
            soap_service = get_soap_service()
            organizations = soap_service.get_organization_data_only(organization_ids)
            
            return [
                {
                    "organization_id": o.organization_id,
                    "organization_name": o.organization_name,
                    "organization_type": o.organization_type,
                    "address": o.address,
                    "city": o.city,
                    "country": o.country,
                    "phone": o.phone,
                    "email": o.email,
                    "website": o.website,
                    "registration_date": o.registration_date,
                    "status": o.status,
                    "description": o.description
                } for o in organizations
            ]
        except Exception as e:
            return []
    
    def resolve_soap_connection_test(self, info):
        try:
            from .services.soap_service import get_soap_service
            
            soap_service = get_soap_service()
            result = soap_service.test_soap_connection()
            
            return {
                "connected": result['connected'],
                "service_url": result['service_url'],
                "message": result['message']
            }
        except Exception as e:
            return {
                "connected": False,
                "service_url": "Unknown",
                "message": f"Connection test failed: {str(e)}"
            }

# Mutations
class DonationFilterInput(graphene.InputObjectType):
    categoria = graphene.String()
    fecha_desde = graphene.String()
    fecha_hasta = graphene.String()
    eliminado = graphene.Boolean()

class SaveDonationFilter(graphene.Mutation):
    class Arguments:
        nombre = graphene.String(required=True)
        filtros = graphene.Argument(DonationFilterInput, required=True)
    
    save_donation_filter = graphene.Field(SavedFilterType)
    
    def mutate(self, info, nombre, filtros):
        return SaveDonationFilter(save_donation_filter={
            "id": f"filter-{hash(nombre)}",
            "nombre": nombre,
            "filtros": {
                "categoria": filtros.categoria,
                "fecha_desde": filtros.fecha_desde,
                "fecha_hasta": filtros.fecha_hasta,
                "eliminado": filtros.eliminado or False
            },
            "fecha_creacion": "2024-01-22"
        })

class UpdateDonationFilter(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        nombre = graphene.String()
        filtros = graphene.Argument(DonationFilterInput)
    
    update_donation_filter = graphene.Field(SavedFilterType)
    
    def mutate(self, info, id, nombre=None, filtros=None):
        return UpdateDonationFilter(update_donation_filter={
            "id": id,
            "nombre": nombre or "Filtro Actualizado",
            "filtros": {
                "categoria": filtros.categoria if filtros else None,
                "fecha_desde": filtros.fecha_desde if filtros else None,
                "fecha_hasta": filtros.fecha_hasta if filtros else None,
                "eliminado": filtros.eliminado if filtros else False
            },
            "fecha_creacion": "2024-01-10"
        })

class DeleteDonationFilter(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
    
    delete_donation_filter = graphene.Boolean()
    
    def mutate(self, info, id):
        # En una implementación real, aquí eliminarías el filtro de la base de datos
        return DeleteDonationFilter(delete_donation_filter=True)

class Mutation(graphene.ObjectType):
    save_donation_filter = SaveDonationFilter.Field()
    update_donation_filter = UpdateDonationFilter.Field()
    delete_donation_filter = DeleteDonationFilter.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# FastAPI app
def create_app():
    app = FastAPI(
        title="Reports Service with GraphQL",
        description="Sistema de Reportes con GraphQL usando Graphene",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Reports Service with GraphQL is running",
            "version": "1.0.0",
            "graphql_endpoint": "/graphql"
        }
    
    @app.get("/health")
    async def health():
        print(f"🔥 Health check request received")
        return {
            "status": "healthy",
            "service": "reports-service",
            "graphql": "enabled"
        }
    
    # Add GraphQL endpoint
    @app.post("/api/graphql")
    async def graphql_endpoint(request: Request):
        print(f"🔥 GraphQL POST request received - simplified version")
        
        try:
            body = await request.json()
            query = body.get("query", "")
            print(f"🔥 Query received: {query[:100]}...")
            
            # Execute GraphQL query using the schema
            variables = body.get("variables", {})
            result = schema.execute(query, variables=variables)
            
            if result.errors:
                print(f"🔥 GraphQL errors: {result.errors}")
                return JSONResponse({
                    "data": result.data,
                    "errors": [{"message": str(error)} for error in result.errors]
                })
            
            print(f"🔥 GraphQL query executed successfully")
            return JSONResponse({"data": result.data})
                
        except Exception as e:
            print(f"🔥 Error: {e}")
            return JSONResponse({"data": {}})
    
    @app.get("/api/graphql")
    async def graphql_playground():
        print(f"🔥 GraphQL GET request received")
        return {
            "message": "GraphQL endpoint is available",
            "note": "Send POST requests with GraphQL queries",
            "example": {
                "query": "{ donationReport { categoria totalCantidad } }",
                "variables": {}
            }
        }
    
    return app