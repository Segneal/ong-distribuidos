const express = require('express');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Helper function for database connection with correct credentials (copied from user-service)
async function createDbConnection() {
  const mysql = require('mysql2/promise');
  return await mysql.createConnection({
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'ong_management',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    port: parseInt(process.env.DB_PORT || '3306'),
    charset: 'utf8mb4'
  });
}

router.post('/active-requests', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET ACTIVE REQUESTS ===');
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        solicitud_id as request_id,
        donaciones as donations,
        estado as status,
        fecha_creacion as timestamp,
        notas as notes
      FROM solicitudes_donaciones 
      WHERE estado = 'ACTIVA'
      ORDER BY fecha_creacion DESC
    `;

    const [rows] = await connection.execute(query);
    await connection.end();

    const requests = rows.map(row => ({
      request_id: row.request_id,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      status: row.status,
      timestamp: row.timestamp,
      notes: row.notes
    }));

    res.json({
      success: true,
      requests: requests
    });
  } catch (error) {
    console.error('Error getting active requests:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

router.post('/external-offers', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EXTERNAL OFFERS ===');
    
    const connection = await createDbConnection();

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

    const [rows] = await connection.execute(query);
    await connection.end();

    const offers = rows.map(row => ({
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
      error: 'Internal server error',
      message: error.message
    });
  }
});

router.post('/transfer-history', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET TRANSFER HISTORY ===');
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        tipo as type,
        organizacion_contraparte as counterpart_organization,
        solicitud_id as request_id,
        donaciones as donations,
        estado as status,
        fecha_transferencia as timestamp,
        notas as notes
      FROM transferencias_donaciones 
      ORDER BY fecha_transferencia DESC
      LIMIT 50
    `;

    const [rows] = await connection.execute(query);
    await connection.end();

    const transfers = rows.map(row => ({
      type: row.type,
      counterpart_organization: row.counterpart_organization,
      request_id: row.request_id,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      status: row.status,
      timestamp: row.timestamp,
      notes: row.notes
    }));

    res.json({
      success: true,
      transfers: transfers
    });
  } catch (error) {
    console.error('Error getting transfer history:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

module.exports = router;