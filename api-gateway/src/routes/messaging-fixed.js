const express = require('express');
const { Pool } = require('pg');
const router = express.Router();

/**
 * Get external donation offers
 */
router.post('/external-offers', async (req, res) => {
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

/**
 * Get external donation requests
 */
router.post('/external-requests', async (req, res) => {
  try {
    console.log('=== GET EXTERNAL REQUESTS ===');
    
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
    await pool.end();

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

/**
 * Get external events
 */
router.post('/external-events', async (req, res) => {
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

/**
 * Get active requests (empty for now)
 */
router.post('/active-requests', async (req, res) => {
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

/**
 * Get transfer history
 */
router.post('/transfer-history', async (req, res) => {
  try {
    console.log('=== GET TRANSFER HISTORY ===');
    
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
        ht.transfer_id,
        ht.cantidad_transferida as quantity,
        ht.organizacion_destino as target_organization,
        ht.solicitud_id as request_id,
        ht.fecha_transferencia as timestamp,
        ht.estado as status,
        d.descripcion as donation_description,
        d.categoria as donation_category
      FROM historial_transferencias ht
      JOIN donaciones d ON ht.donacion_id = d.id
      ORDER BY ht.fecha_transferencia DESC
      LIMIT 50
    `;

    const result = await pool.query(query);
    await pool.end();

    const transfers = result.rows.map(row => ({
      id: row.transfer_id,
      tipo: 'ENVIADA', // Assuming all transfers are sent for now
      organizacion_contraparte: row.target_organization, // Frontend expects this field name
      organizacion_destino: row.target_organization, // Keep both for compatibility
      fecha_transferencia: row.timestamp, // Frontend expects this field name
      fecha: row.timestamp, // Keep both for compatibility
      estado: row.status,
      solicitud_id: row.request_id, // Frontend expects this field
      donaciones: [{
        id: row.transfer_id + '_donation',
        descripcion: row.donation_description, // Keep Spanish for compatibility
        description: row.donation_description, // Add English for frontend
        category: row.donation_category,
        cantidad: row.quantity, // Keep Spanish for compatibility
        quantity: row.quantity  // Add English for frontend
      }]
    }));

    console.log(`Found ${transfers.length} transfer records`);

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

/**
 * Transfer donations to another organization
 */
router.post('/transfer-donations', async (req, res) => {
  const pool = new Pool({
    host: process.env.DB_HOST || 'postgres',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'ong_management',
    user: process.env.DB_USER || 'ong_user',
    password: process.env.DB_PASSWORD || 'ong_pass',
  });

  try {
    console.log('=== TRANSFER DONATIONS ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    const { targetOrganization, requestId, donations, userId } = req.body;
    
    // Validate required fields
    if (!targetOrganization || !requestId || !donations || !Array.isArray(donations)) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: targetOrganization, requestId, donations'
      });
    }

    const baseTransferId = `TRF-${Date.now()}`;
    
    // Begin transaction
    await pool.query('BEGIN');
    
    try {
      // Process each donation transfer
      for (let i = 0; i < donations.length; i++) {
        const donation = donations[i];
        // Handle both frontend formats: inventoryId or donation_id
        const donationId = donation.donation_id || donation.inventoryId;
        const quantity = parseInt(donation.quantity) || donation.quantity;
        
        if (!donationId || !quantity || quantity <= 0) {
          throw new Error(`Invalid donation: ${JSON.stringify(donation)}`);
        }
        
        // Check current quantity
        const checkResult = await pool.query(
          'SELECT cantidad, descripcion FROM donaciones WHERE id = $1 AND eliminado = false',
          [donationId]
        );
        
        if (checkResult.rows.length === 0) {
          throw new Error(`Donation with ID ${donationId} not found`);
        }
        
        const currentQuantity = checkResult.rows[0].cantidad;
        const description = checkResult.rows[0].descripcion;
        
        if (currentQuantity < quantity) {
          throw new Error(`Insufficient quantity for ${description}. Available: ${currentQuantity}, Requested: ${quantity}`);
        }
        
        // Update donation quantity
        await pool.query(
          'UPDATE donaciones SET cantidad = cantidad - $1, fecha_modificacion = CURRENT_TIMESTAMP, usuario_modificacion = $2 WHERE id = $3',
          [quantity, userId || 1, donationId]
        );
        
        // Generate unique transfer_id for each donation
        const uniqueTransferId = `${baseTransferId}-${i + 1}`;
        
        // Create transfer history record
        await pool.query(
          'INSERT INTO historial_transferencias (transfer_id, donacion_id, cantidad_transferida, organizacion_destino, solicitud_id, usuario_id) VALUES ($1, $2, $3, $4, $5, $6)',
          [uniqueTransferId, donationId, quantity, targetOrganization, requestId, userId || 1]
        );
        
        console.log(`Transferred ${quantity} units of ${description} to ${targetOrganization}`);
      }
      
      // Commit transaction
      await pool.query('COMMIT');
      
      res.json({
        success: true,
        message: 'Donation transfer completed successfully',
        transfer_id: baseTransferId,
        timestamp: new Date().toISOString(),
        transferred_items: donations.length
      });

    } catch (error) {
      // Rollback transaction
      await pool.query('ROLLBACK');
      throw error;
    }

  } catch (error) {
    console.error('Error transferring donations:', error);
    res.status(500).json({
      success: false,
      error: 'Transfer failed',
      message: error.message
    });
  } finally {
    await pool.end();
  }
});

/**
 * Get volunteer adhesions
 */
router.post('/volunteer-adhesions', async (req, res) => {
  try {
    console.log('=== GET VOLUNTEER ADHESIONS ===');
    
    // For now, return empty array
    // In a real implementation, this would query the database
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

/**
 * Create event adhesion
 */
router.post('/create-event-adhesion', async (req, res) => {
  try {
    console.log('=== CREATE EVENT ADHESION ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    // For now, return success without actual creation
    res.json({
      success: true,
      message: 'Event adhesion created successfully',
      adhesion_id: `ADH-${Date.now()}`,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error creating event adhesion:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

/**
 * Publish event to network
 */
router.post('/publish-event', async (req, res) => {
  try {
    console.log('=== PUBLISH EVENT ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    // For now, return success without actual publishing
    res.json({
      success: true,
      message: 'Event published to network successfully',
      publication_id: `PUB-${Date.now()}`,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error publishing event:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

/**
 * Create donation request
 */
router.post('/create-donation-request', async (req, res) => {
  try {
    console.log('=== CREATE DONATION REQUEST ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    // For now, return success without actual creation
    res.json({
      success: true,
      message: 'Donation request created successfully',
      request_id: `REQ-${Date.now()}`,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error creating donation request:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

/**
 * Create donation offer
 */
router.post('/create-donation-offer', async (req, res) => {
  try {
    console.log('=== CREATE DONATION OFFER ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    // For now, return success without actual creation
    res.json({
      success: true,
      message: 'Donation offer created successfully',
      offer_id: `OFF-${Date.now()}`,
      timestamp: new Date().toISOString()
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

/**
 * Get event adhesions
 */
router.post('/event-adhesions', async (req, res) => {
  try {
    console.log('=== GET EVENT ADHESIONS ===');
    
    // For now, return empty array
    res.json({
      success: true,
      adhesions: []
    });

  } catch (error) {
    console.error('Error getting event adhesions:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

/**
 * Cancel donation request
 */
router.post('/cancel-donation-request', async (req, res) => {
  try {
    console.log('=== CANCEL DONATION REQUEST ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    // For now, return success
    res.json({
      success: true,
      message: 'Donation request cancelled successfully',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error cancelling donation request:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

/**
 * Cancel event
 */
router.post('/cancel-event', async (req, res) => {
  try {
    console.log('=== CANCEL EVENT ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    // For now, return success
    res.json({
      success: true,
      message: 'Event cancelled successfully',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error cancelling event:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

module.exports = router;