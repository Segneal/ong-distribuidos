const express = require('express');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

// Test route
app.post('/api/messaging/external-offers', async (req, res) => {
  try {
    console.log('=== GET EXTERNAL OFFERS ===');
    
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

app.listen(3005, () => {
  console.log('Test server running on port 3005');
});