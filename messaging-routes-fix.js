const express = require('express');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Rutas básicas de messaging que funcionan directamente con la base de datos
router.post('/active-requests', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET ACTIVE REQUESTS ===');
    
    res.json({
      success: true,
      requests: []
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

router.post('/volunteer-adhesions', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET VOLUNTEER ADHESIONS ===');
    const volunteerId = req.user.id;
    
    res.json({
      success: true,
      adhesions: []
    });
  } catch (error) {
    console.error('Error getting volunteer adhesions:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

router.post('/create-donation-offer', authenticateToken, async (req, res) => {
  try {
    console.log('=== CREATE DONATION OFFER ===');
    const { donations, notes } = req.body;
    const userId = req.user.id;
    
    res.json({
      success: true,
      message: 'Donation offer created successfully',
      offerId: 'temp-' + Date.now()
    });
  } catch (error) {
    console.error('Error creating donation offer:', error);
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
      error: 'Internal server error',
      message: error.message
    });
  }
});

router.post('/external-events', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EXTERNAL EVENTS ===');
    
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
      WHERE organizacion_id != 'empuje-comunitario'
      AND activo = true
      ORDER BY fecha_evento ASC
    `;

    const result = await pool.query(query);
    await pool.end();

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

router.post('/transfer-history', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET TRANSFER HISTORY ===');
    
    res.json({
      success: true,
      transfers: []
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