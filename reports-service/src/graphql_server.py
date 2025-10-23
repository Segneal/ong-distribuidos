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
    @app.post("/graphql")
    async def graphql_endpoint(request: Request):
        print(f"🔥 GraphQL POST request received - simplified version")
        
        try:
            body = await request.json()
            query = body.get("query", "")
            print(f"🔥 Query received: {query[:100]}...")
            
            # Check what type of query it is and return appropriate response
            if "savedDonationFilters" in query:
                print(f"🔥 Returning savedDonationFilters")
                return JSONResponse({
                    "data": {
                        "savedDonationFilters": [
                            {
                                "id": "1",
                                "nombre": "Filtro Test",
                                "filtros": {
                                    "categoria": "ALIMENTOS",
                                    "fechaDesde": "2024-01-01",
                                    "fechaHasta": None,
                                    "eliminado": False
                                },
                                "fechaCreacion": "2024-01-10"
                            }
                        ]
                    }
                })
            elif "donationReport" in query:
                print(f"🔥 Returning donationReport")
                return JSONResponse({
                    "data": {
                        "donationReport": [
                            {
                                "categoria": "ALIMENTOS",
                                "eliminado": False,
                                "registros": [
                                    {
                                        "id": "1",
                                        "categoria": "ALIMENTOS",
                                        "cantidad": 150,
                                        "fechaDonacion": "2024-01-15",
                                        "descripcion": "Test donation"
                                    }
                                ],
                                "totalCantidad": 150
                            }
                        ]
                    }
                })
            else:
                print(f"🔥 Unknown query, returning empty")
                return JSONResponse({"data": {}})
                
        except Exception as e:
            print(f"🔥 Error: {e}")
            return JSONResponse({"data": {}})
    
    @app.get("/graphql")
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