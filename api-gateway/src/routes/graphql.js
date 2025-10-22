const express = require('express');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// GraphQL endpoint with mock data for development
router.post('/graphql', authenticateToken, (req, res) => {
  const { query, variables } = req.body;
  
  try {
    // Log the query for debugging
    console.log('GraphQL Query:', query);
    console.log('Variables:', variables);
    
    // Handle introspection queries
    if (query && query.includes('__schema')) {
      return res.json({
        data: {
          __schema: {
            types: [
              {
                name: "Query",
                kind: "OBJECT",
                fields: [
                  { name: "donationReport", type: { name: "[DonationReport]" } },
                  { name: "eventParticipationReport", type: { name: "[EventParticipationReport]" } },
                  { name: "savedDonationFilters", type: { name: "[SavedFilter]" } },
                  { name: "users", type: { name: "[User]" } }
                ]
              }
            ]
          }
        }
      });
    }

    // Handle donation report query
    if (query && query.includes('GetDonationReport')) {
      // Create grouped donation data structure that matches frontend expectations
      const mockDonations = [
        {
          id: "1",
          categoria: "ALIMENTOS",
          cantidad: 150,
          fechaDonacion: "2024-01-15",
          organizacion: req.user.organization,
          donante: {
            id: "1",
            nombre: "Juan Pérez",
            email: "juan@example.com"
          },
          estado: "ENTREGADA",
          eliminado: false
        },
        {
          id: "2", 
          categoria: "ALIMENTOS",
          cantidad: 200,
          fechaDonacion: "2024-01-18",
          organizacion: req.user.organization,
          donante: {
            id: "3",
            nombre: "Ana Martínez",
            email: "ana@example.com"
          },
          estado: "ENTREGADA",
          eliminado: false
        },
        {
          id: "3",
          categoria: "ROPA",
          cantidad: 75,
          fechaDonacion: "2024-01-20",
          organizacion: req.user.organization,
          donante: {
            id: "2",
            nombre: "María García",
            email: "maria@example.com"
          },
          estado: "PENDIENTE",
          eliminado: false
        }
      ];

      // Filter by category if specified
      const filteredDonations = variables?.categoria 
        ? mockDonations.filter(d => d.categoria === variables.categoria)
        : mockDonations;

      // Group donations by category and eliminado status
      const groupedData = filteredDonations.reduce((groups, donation) => {
        const key = `${donation.categoria}-${donation.eliminado}`;
        if (!groups[key]) {
          groups[key] = {
            categoria: donation.categoria,
            eliminado: donation.eliminado,
            registros: [],
            totalCantidad: 0
          };
        }
        groups[key].registros.push(donation);
        groups[key].totalCantidad += donation.cantidad;
        return groups;
      }, {});

      return res.json({
        data: {
          donationReport: Object.values(groupedData)
        }
      });
    }

    // Handle event participation report query
    if (query && query.includes('GetEventParticipationReport')) {
      return res.json({
        data: {
          eventParticipationReport: [
            {
              id: "1",
              nombre: "Campaña de Donación de Alimentos",
              fecha: "2024-01-15",
              organizacion: req.user.organization,
              participantes: [
                {
                  id: "1",
                  nombre: "Ana López",
                  email: "ana@example.com",
                  rol: "VOLUNTARIO"
                },
                {
                  id: "2", 
                  nombre: "Carlos Ruiz",
                  email: "carlos@example.com",
                  rol: "COORDINADOR"
                }
              ],
              totalParticipantes: 2
            }
          ]
        }
      });
    }

    // Handle saved donation filters query
    if (query && query.includes('GetSavedDonationFilters')) {
      return res.json({
        data: {
          savedDonationFilters: [
            {
              id: "1",
              nombre: "Filtro Alimentos",
              filtros: {
                categoria: "ALIMENTOS",
                fechaDesde: "2024-01-01",
                fechaHasta: null,
                eliminado: false
              },
              fechaCreacion: "2024-01-10"
            },
            {
              id: "2",
              nombre: "Filtro Ropa",
              filtros: {
                categoria: "ROPA",
                fechaDesde: "2024-01-15",
                fechaHasta: "2024-01-31",
                eliminado: false
              },
              fechaCreacion: "2024-01-12"
            }
          ]
        }
      });
    }

    // Handle users list query
    if (query && query.includes('GetUsersList')) {
      return res.json({
        data: {
          users: [
            {
              id: "1",
              nombre: "Ana López",
              email: "ana@example.com",
              rol: "VOLUNTARIO"
            },
            {
              id: "2",
              nombre: "Carlos Ruiz", 
              email: "carlos@example.com",
              rol: "COORDINADOR"
            }
          ]
        }
      });
    }

    // Handle mutations
    if (query && query.includes('SaveDonationFilter')) {
      return res.json({
        data: {
          saveDonationFilter: {
            id: "new-filter-id",
            nombre: variables?.nombre || "Nuevo Filtro",
            filtros: variables?.filtros || {},
            fechaCreacion: new Date().toISOString()
          }
        }
      });
    }

    if (query && query.includes('UpdateDonationFilter')) {
      return res.json({
        data: {
          updateDonationFilter: {
            id: variables?.id || "1",
            nombre: variables?.nombre || "Filtro Actualizado",
            filtros: variables?.filtros || {},
            fechaCreacion: "2024-01-10"
          }
        }
      });
    }

    if (query && query.includes('DeleteDonationFilter')) {
      return res.json({
        data: {
          deleteDonationFilter: true
        }
      });
    }

    // Default response for unhandled queries
    res.json({
      data: {
        message: "GraphQL endpoint is working with mock data",
        user: {
          id: req.user.userId || req.user.id,
          role: req.user.role,
          organization: req.user.organization
        }
      }
    });

  } catch (error) {
    console.error('GraphQL Error:', error);
    res.status(500).json({
      errors: [
        {
          message: "Internal server error processing GraphQL query",
          extensions: {
            code: "INTERNAL_ERROR"
          }
        }
      ]
    });
  }
});

// GET endpoint for GraphQL playground/introspection (no auth required)
router.get('/graphql', (req, res) => {
  res.json({
    message: "GraphQL endpoint is available",
    note: "Send POST requests with GraphQL queries",
    authentication: "Bearer token required in Authorization header",
    example: {
      query: "{ hello }",
      variables: {}
    }
  });
});

// Health check endpoint (no auth required)
router.get('/graphql/health', (req, res) => {
  res.json({
    status: "healthy",
    service: "GraphQL Gateway",
    timestamp: new Date().toISOString(),
    authentication: "required"
  });
});

module.exports = router;