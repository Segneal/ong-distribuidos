const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware básico
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const { checkServiceHealth } = require('./services/grpcClients');
    const serviceHealth = await checkServiceHealth();
    res.status(200).json({
      status: 'OK',
      timestamp: new Date().toISOString(),
      service: 'API Gateway',
      microservices: serviceHealth
    });
  } catch (error) {
    console.error('Error en health check:', error);
    res.status(200).json({
      status: 'OK',
      timestamp: new Date().toISOString(),
      service: 'API Gateway',
      microservices: 'Health check no disponible'
    });
  }
});

// Importar rutas
const authRoutes = require('./routes/auth');
const usersRoutes = require('./routes/users');
const inventoryRoutes = require('./routes/inventory');
const eventsRoutes = require('./routes/events');
const donationRequestsRoutes = require('./routes/donationRequests');

// Crear rutas de messaging inline para evitar problemas de archivos
const messagingRoutes = express.Router();
const { authenticateToken } = require('./middleware/auth');

// Toggle event exposure route
messagingRoutes.post('/toggle-event-exposure', authenticateToken, async (req, res) => {
  try {
    console.log('=== TOGGLE EVENT EXPOSURE ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    const { eventId, expuesto_red } = req.body;
    
    if (!eventId) {
      return res.status(400).json({
        success: false,
        error: 'Event ID is required'
      });
    }
    
    // Database connection
    const { Pool } = require('pg');
    const pool = new Pool({
      host: process.env.DB_HOST || 'postgres',
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME || 'ong_management',
      user: process.env.DB_USER || 'ong_user',
      password: process.env.DB_PASSWORD || 'ong_pass',
    });

    // Update event exposure status
    const updateQuery = `
      UPDATE eventos 
      SET expuesto_red = $1, fecha_actualizacion = CURRENT_TIMESTAMP 
      WHERE id = $2 
      RETURNING id, nombre, expuesto_red
    `;
    
    const updateResult = await pool.query(updateQuery, [expuesto_red, eventId]);
    
    if (updateResult.rows.length === 0) {
      await pool.end();
      return res.status(404).json({
        success: false,
        error: 'Event not found'
      });
    }
    
    const event = updateResult.rows[0];
    
    if (expuesto_red) {
      // Add to external events
      const eventDetailsQuery = `
        SELECT id, nombre, descripcion, fecha_evento 
        FROM eventos 
        WHERE id = $1
      `;
      
      const eventDetails = await pool.query(eventDetailsQuery, [eventId]);
      const eventData = eventDetails.rows[0];
      
      const insertQuery = `
        INSERT INTO eventos_externos (evento_id, organizacion_id, nombre, descripcion, fecha_evento, activo)
        VALUES ($1, 'empuje-comunitario', $2, $3, $4, true)
        ON CONFLICT (organizacion_id, evento_id) 
        DO UPDATE SET 
          nombre = EXCLUDED.nombre,
          descripcion = EXCLUDED.descripcion,
          fecha_evento = EXCLUDED.fecha_evento,
          activo = true,
          fecha_creacion = CURRENT_TIMESTAMP
      `;
      
      await pool.query(insertQuery, [
        eventData.id,
        eventData.nombre,
        eventData.descripcion,
        eventData.fecha_evento
      ]);
    } else {
      // Remove from external events (set inactive)
      const deactivateQuery = `
        UPDATE eventos_externos 
        SET activo = false 
        WHERE evento_id = $1
      `;
      
      await pool.query(deactivateQuery, [eventId]);
    }
    
    await pool.end();
    
    res.json({
      success: true,
      message: expuesto_red ? 'Event exposed to network successfully' : 'Event removed from network successfully',
      event: {
        id: event.id,
        nombre: event.nombre,
        expuesto_red: event.expuesto_red
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Error toggling event exposure:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// External events route
messagingRoutes.post('/external-events', async (req, res) => {
  try {
    const { Pool } = require('pg');
    const pool = new Pool({
      host: process.env.DB_HOST || 'postgres',
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME || 'ong_management',
      user: process.env.DB_USER || 'ong_user',
      password: process.env.DB_PASSWORD || 'ong_pass',
    });

    const query = `
      SELECT 
        evento_id as event_id,
        organizacion_id as organization_id,
        organizacion_id as organization_name,
        nombre as name,
        descripcion as description,
        fecha_evento as event_date,
        fecha_creacion as timestamp,
        activo as active
      FROM eventos_externos 
      WHERE activo = true
      ORDER BY fecha_creacion DESC
    `;

    const result = await pool.query(query);
    await pool.end();

    res.json({
      success: true,
      events: result.rows
    });
    
  } catch (error) {
    console.error('Error getting external events:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// External offers route
messagingRoutes.post('/external-offers', async (req, res) => {
  try {
    const { Pool } = require('pg');
    const pool = new Pool({
      host: process.env.DB_HOST || 'postgres',
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME || 'ong_management',
      user: process.env.DB_USER || 'ong_user',
      password: process.env.DB_PASSWORD || 'ong_pass',
    });

    const query = `
      SELECT 
        oferta_id as offer_id,
        organizacion_donante as organization_id,
        organizacion_donante as organization_name,
        donaciones as donations,
        fecha_creacion as timestamp,
        activa as active
      FROM ofertas_externas 
      WHERE organizacion_donante != 'empuje-comunitario'
      AND activa = true
      ORDER BY fecha_creacion DESC
    `;

    const result = await pool.query(query);
    await pool.end();

    const offers = result.rows.map(row => ({
      offer_id: row.offer_id,
      organization_id: row.organization_id,
      organization_name: row.organization_name,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      timestamp: row.timestamp,
      active: row.active
    }));

    res.json({
      success: true,
      offers: offers
    });
    
  } catch (error) {
    console.error('Error getting external offers:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// External requests route
messagingRoutes.post('/external-requests', async (req, res) => {
  try {
    // Return empty array for now since table doesn't exist
    res.json({
      success: true,
      requests: []
    });
  } catch (error) {
    console.error('Error getting external requests:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// Transfer history route
messagingRoutes.post('/transfer-history', async (req, res) => {
  try {
    // Return empty array for now since table doesn't exist
    res.json({
      success: true,
      transfers: []
    });
  } catch (error) {
    console.error('Error getting transfer history:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// Configurar rutas
app.use('/api/auth', authRoutes);
app.use('/api/users', usersRoutes);
app.use('/api/inventory', inventoryRoutes);
app.use('/api/events', eventsRoutes);
app.use('/api/donation-requests', donationRequestsRoutes);
app.use('/api/messaging', messagingRoutes);

// Ruta por defecto
app.get('/', (req, res) => {
  res.json({
    message: 'API Gateway - Sistema de Gestión ONG Empuje Comunitario',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      auth: '/api/auth',
      users: '/api/users',
      inventory: '/api/inventory',
      events: '/api/events',
      messaging: '/api/messaging'
    }
  });
});

// Importar middleware de manejo de errores
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');

// Middleware para rutas no encontradas
app.use('*', notFoundHandler);

// Middleware de manejo de errores (debe ir al final)
app.use(errorHandler);

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 API Gateway ejecutándose en puerto ${PORT}`);
  console.log(`📊 Health check disponible en http://localhost:${PORT}/health`);
});

module.exports = app;