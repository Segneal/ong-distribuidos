const express = require('express');
const axios = require('axios');
const { authenticateToken } = require('../middleware/auth');
const { handleGrpcError } = require('../utils/grpcErrorHandler');

const router = express.Router();

// Messaging service URL
const MESSAGING_SERVICE_URL = process.env.MESSAGING_SERVICE_URL || 'http://messaging-service:50054';

/**
 * Transfer donations to another organization
 */
router.post('/transfer-donations', authenticateToken, async (req, res) => {
  try {
    console.log('=== TRANSFER DONATIONS REQUEST ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const { targetOrganization, requestId, donations } = req.body;
    const userId = req.user.id;

    // Validate required fields
    if (!targetOrganization) {
      return res.status(400).json({
        success: false,
        error: 'Target organization is required'
      });
    }

    if (!requestId) {
      return res.status(400).json({
        success: false,
        error: 'Request ID is required'
      });
    }

    if (!donations || !Array.isArray(donations) || donations.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Donations array is required and must not be empty'
      });
    }

    // Validate donation items
    for (const donation of donations) {
      if (!donation.donation_id || !donation.quantity) {
        return res.status(400).json({
          success: false,
          error: 'Each donation must have donation_id and quantity'
        });
      }

      if (donation.quantity <= 0) {
        return res.status(400).json({
          success: false,
          error: 'Donation quantity must be positive'
        });
      }
    }

    console.log('Calling messaging service for transfer...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/transferDonations`, {
      targetOrganization,
      requestId,
      donations,
      userId
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error in transfer donations:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Get transfer history
 */
router.post('/transfer-history', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET TRANSFER HISTORY REQUEST ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));

    const { organizationId, limit } = req.body;

    console.log('Calling messaging service for transfer history...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/getTransferHistory`, {
      organizationId,
      limit: limit || 50
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error getting transfer history:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Create donation request (network-wide)
 */
router.post('/create-donation-request', authenticateToken, async (req, res) => {
  try {
    console.log('=== CREATE DONATION REQUEST ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const { donations, notes } = req.body;
    const userId = req.user.id;

    // Validate donations
    if (!donations || !Array.isArray(donations) || donations.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Donations array is required and must not be empty'
      });
    }

    // Validate donation items
    for (const donation of donations) {
      if (!donation.category || !donation.description) {
        return res.status(400).json({
          success: false,
          error: 'Each donation must have category and description'
        });
      }
    }

    console.log('Calling messaging service for donation request...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/createDonationRequest`, {
      donations,
      userId,
      notes
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error creating donation request:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Get external donation requests
 */
router.post('/external-requests', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EXTERNAL REQUESTS ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));

    const { activeOnly } = req.body;

    console.log('Calling messaging service for external requests...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/getExternalRequests`, {
      activeOnly: activeOnly !== false // Default to true
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error getting external requests:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Cancel donation request
 */
router.post('/cancel-donation-request', authenticateToken, async (req, res) => {
  try {
    console.log('=== CANCEL DONATION REQUEST ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const { requestId } = req.body;
    const userId = req.user.id;

    if (!requestId) {
      return res.status(400).json({
        success: false,
        error: 'Request ID is required'
      });
    }

    console.log('Calling messaging service to cancel request...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/cancelDonationRequest`, {
      requestId,
      userId
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error canceling donation request:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Get active donation requests (our own)
 */
router.post('/active-requests', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET ACTIVE REQUESTS ===');

    console.log('Calling messaging service for active requests...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/getActiveRequests`, {});

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error getting active requests:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Create donation offer
 */
router.post('/create-donation-offer', authenticateToken, async (req, res) => {
  try {
    console.log('=== CREATE DONATION OFFER ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const { donations, notes } = req.body;
    const userId = req.user.id;

    // Validate donations
    if (!donations || !Array.isArray(donations) || donations.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Donations array is required and must not be empty'
      });
    }

    // Validate donation items
    for (const donation of donations) {
      if (!donation.category || !donation.description || !donation.quantity) {
        return res.status(400).json({
          success: false,
          error: 'Each donation must have category, description, and quantity'
        });
      }
    }

    console.log('Calling messaging service for donation offer...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/createDonationOffer`, {
      donations,
      userId,
      notes
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error creating donation offer:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});



/**
 * Publish solidarity event to the network
 */
router.post('/publish-event', authenticateToken, async (req, res) => {
  try {
    console.log('=== PUBLISH SOLIDARITY EVENT ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const { eventId, name, description, eventDate } = req.body;
    const userId = req.user.id;

    // Validate required fields
    if (!eventId) {
      return res.status(400).json({
        success: false,
        error: 'Event ID is required'
      });
    }

    if (!name) {
      return res.status(400).json({
        success: false,
        error: 'Event name is required'
      });
    }

    if (!eventDate) {
      return res.status(400).json({
        success: false,
        error: 'Event date is required'
      });
    }

    console.log('Calling messaging service to publish event...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/publishEvent`, {
      eventId,
      name,
      description: description || '',
      eventDate,
      userId
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error publishing solidarity event:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});



/**
 * Cancel solidarity event
 */
router.post('/cancel-event', authenticateToken, async (req, res) => {
  try {
    console.log('=== CANCEL SOLIDARITY EVENT ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const { eventId } = req.body;
    const userId = req.user.id;

    if (!eventId) {
      return res.status(400).json({
        success: false,
        error: 'Event ID is required'
      });
    }

    console.log('Calling messaging service to cancel event...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/cancelEvent`, {
      eventId,
      userId
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error canceling solidarity event:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Create event adhesion
 */
router.post('/create-event-adhesion', authenticateToken, async (req, res) => {
  try {
    console.log('=== CREATE EVENT ADHESION ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const { eventId, targetOrganization } = req.body;
    const volunteerId = req.user.id;

    // Validate required fields
    if (!eventId) {
      return res.status(400).json({
        success: false,
        error: 'Event ID is required'
      });
    }

    if (!targetOrganization) {
      return res.status(400).json({
        success: false,
        error: 'Target organization is required'
      });
    }

    console.log('Calling messaging service to create event adhesion...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/createEventAdhesion`, {
      eventId,
      volunteerId,
      targetOrganization
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error creating event adhesion:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Get volunteer adhesions
 */
router.post('/volunteer-adhesions', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET VOLUNTEER ADHESIONS ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const volunteerId = req.user.id;

    console.log('Calling messaging service for volunteer adhesions...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/getVolunteerAdhesions`, {
      volunteerId
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error getting volunteer adhesions:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Get event adhesions (for administrators)
 */
router.post('/event-adhesions', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EVENT ADHESIONS ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    console.log('User:', req.user);

    const { eventId } = req.body;

    if (!eventId) {
      return res.status(400).json({
        success: false,
        error: 'Event ID is required'
      });
    }

    console.log('Calling messaging service for event adhesions...');

    // Call messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/getEventAdhesions`, {
      eventId
    });

    console.log('Messaging service response:', response.data);

    res.json(response.data);

  } catch (error) {
    console.error('Error getting event adhesions:', error);
    
    if (error.response) {
      // Error from messaging service
      console.error('Messaging service error:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      // Network or other error
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    }
  }
});

/**
 * Get external solidarity events
 */
router.post('/external-events', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EXTERNAL EVENTS ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));

    const { activeOnly = true } = req.body;

    // Temporary solution: Query database directly
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
      ${activeOnly ? 'AND activo = true' : ''}
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
 * Get external donation offers
 */
router.post('/external-offers', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EXTERNAL OFFERS ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));

    const { activeOnly = true } = req.body;

    // Temporary solution: Query database directly
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
      ${activeOnly ? 'AND activa = true' : ''}
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
 * Get active donation requests (our own)
 */
router.post('/active-requests', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET ACTIVE REQUESTS ===');

    // For now, return empty array since we don't have our own requests in the test data
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
router.post('/transfer-history', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET TRANSFER HISTORY ===');

    // For now, return empty array since we don't have transfer history in the test data
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