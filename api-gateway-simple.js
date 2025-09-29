const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();
const PORT = 3010;

app.use(cors());
app.use(express.json());

// Database connection
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'ong_management',
  user: 'ong_user',
  password: 'ong_pass',
});

// External offers endpoint
app.post('/api/messaging/external-offers', async (req, res) => {
  try {
    console.log('=== GET EXTERNAL OFFERS ===');
    
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

    const offers = result.rows.map(row => ({
      offer_id: row.offer_id,
      organization_id: row.organization_id,
      organization_name: row.organization_name,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      timestamp: row.timestamp,
      active: row.active
    }));

    console.log(`Found ${offers.length} external offers`);

    res.json({
      success: true,
      offers: offers
    });

  } catch (error) {
    console.error('Error getting external offers:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// External requests endpoint
app.post('/api/messaging/external-requests', async (req, res) => {
  try {
    console.log('=== GET EXTERNAL REQUESTS ===');
    
    const query = `
      SELECT 
        solicitud_id as request_id,
        organizacion_solicitante as organization_id,
        organizacion_solicitante as organization_name,
        donaciones as donations,
        fecha_creacion as timestamp,
        activa as active
      FROM solicitudes_externas 
      WHERE organizacion_solicitante != 'empuje-comunitario'
      AND activa = true
      ORDER BY fecha_creacion DESC
    `;

    const result = await pool.query(query);

    const requests = result.rows.map(row => ({
      request_id: row.request_id,
      organization_id: row.organization_id,
      organization_name: row.organization_name,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      timestamp: row.timestamp,
      active: row.active
    }));

    console.log(`Found ${requests.length} external requests`);

    res.json({
      success: true,
      requests: requests
    });

  } catch (error) {
    console.error('Error getting external requests:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// External events endpoint
app.post('/api/messaging/external-events', async (req, res) => {
  try {
    console.log('=== GET EXTERNAL EVENTS ===');
    
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
      WHERE organizacion_id != 'empuje-comunitario'
      AND activo = true
      ORDER BY fecha_evento ASC
    `;

    const result = await pool.query(query);

    const events = result.rows.map(row => ({
      event_id: row.event_id,
      organization_id: row.organization_id,
      organization_name: row.organization_name,
      name: row.name,
      description: row.description,
      event_date: row.event_date,
      timestamp: row.timestamp,
      active: row.active
    }));

    console.log(`Found ${events.length} external events`);

    res.json({
      success: true,
      events: events
    });

  } catch (error) {
    console.error('Error getting external events:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Empty endpoints for other functionality
app.post('/api/messaging/active-requests', (req, res) => {
  res.json({ success: true, requests: [] });
});

app.post('/api/messaging/transfer-history', (req, res) => {
  res.json({ success: true, transfers: [] });
});

app.listen(PORT, () => {
  console.log(`Simple API Gateway running on port ${PORT}`);
});