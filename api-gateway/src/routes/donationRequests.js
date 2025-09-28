const express = require('express');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validateInput } = require('../utils/grpcMapper');
const router = express.Router();

// Apply authentication to all donation request routes
router.use(authenticateToken);

// POST /api/donation-requests - Create donation request
router.post('/', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  console.log('=== POST /api/donation-requests STARTED ===');
  try {
    const { donations, notes } = req.body;
    const userId = req.user?.id;

    console.log('1. POST donation-requests - donations:', JSON.stringify(donations, null, 2));
    console.log('2. POST donation-requests - userId:', userId);
    console.log('3. POST donation-requests - notes:', notes);

    // Validate input
    if (!donations || !Array.isArray(donations) || donations.length === 0) {
      return res.status(400).json({
        error: 'Se requiere al menos una donación en la solicitud'
      });
    }

    // Validate each donation item
    const validationErrors = [];
    const validCategories = ['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'];
    
    donations.forEach((donation, index) => {
      if (!donation.category || !validCategories.includes(donation.category)) {
        validationErrors.push(`Donación ${index + 1}: Categoría inválida`);
      }
      if (!donation.description || donation.description.trim().length === 0) {
        validationErrors.push(`Donación ${index + 1}: Descripción requerida`);
      }
      if (donation.description && donation.description.length > 255) {
        validationErrors.push(`Donación ${index + 1}: Descripción muy larga (máximo 255 caracteres)`);
      }
    });

    if (validationErrors.length > 0) {
      return res.status(400).json({
        error: 'Datos de entrada inválidos',
        details: validationErrors
      });
    }

    // Call messaging service to create donation request
    console.log('4. Calling messaging service...');
    const messagingResponse = await callMessagingService('createDonationRequest', {
      donations: donations,
      userId: userId,
      notes: notes
    });

    console.log('5. Messaging service response:', JSON.stringify(messagingResponse, null, 2));

    if (messagingResponse.success) {
      res.status(201).json({
        success: true,
        message: messagingResponse.message,
        request_id: messagingResponse.request_id
      });
    } else {
      res.status(400).json({
        error: messagingResponse.error || 'Error al crear solicitud de donación'
      });
    }

  } catch (error) {
    console.error('6. EXCEPTION in POST /api/donation-requests:', error);
    res.status(500).json({
      error: 'Error interno del servidor'
    });
  }
  console.log('=== POST /api/donation-requests ENDED ===');
});

// GET /api/donation-requests - List active donation requests
router.get('/', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  try {
    console.log('GET /api/donation-requests - Getting active requests');

    // Call messaging service to get active requests
    const messagingResponse = await callMessagingService('getActiveRequests', {});

    if (messagingResponse.success) {
      res.status(200).json({
        success: true,
        requests: messagingResponse.requests || []
      });
    } else {
      res.status(400).json({
        error: messagingResponse.error || 'Error al obtener solicitudes'
      });
    }

  } catch (error) {
    console.error('Error getting donation requests:', error);
    res.status(500).json({
      error: 'Error interno del servidor'
    });
  }
});

// DELETE /api/donation-requests/:requestId - Cancel donation request
router.delete('/:requestId', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  try {
    const { requestId } = req.params;
    const userId = req.user?.id;

    console.log('DELETE donation request:', requestId, 'by user:', userId);

    if (!requestId) {
      return res.status(400).json({
        error: 'ID de solicitud requerido'
      });
    }

    // Call messaging service to cancel request
    const messagingResponse = await callMessagingService('cancelDonationRequest', {
      requestId: requestId,
      userId: userId
    });

    if (messagingResponse.success) {
      res.status(200).json({
        success: true,
        message: messagingResponse.message
      });
    } else {
      res.status(400).json({
        error: messagingResponse.error || 'Error al cancelar solicitud'
      });
    }

  } catch (error) {
    console.error('Error canceling donation request:', error);
    res.status(500).json({
      error: 'Error interno del servidor'
    });
  }
});

// GET /api/donation-requests/external - List external donation requests
router.get('/external', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  try {
    const { activeOnly = 'true' } = req.query;

    console.log('GET external donation requests - activeOnly:', activeOnly);

    // Call messaging service to get external requests
    const messagingResponse = await callMessagingService('getExternalRequests', {
      activeOnly: activeOnly === 'true'
    });

    if (messagingResponse.success) {
      res.status(200).json({
        success: true,
        requests: messagingResponse.requests || []
      });
    } else {
      res.status(400).json({
        error: messagingResponse.error || 'Error al obtener solicitudes externas'
      });
    }

  } catch (error) {
    console.error('Error getting external donation requests:', error);
    res.status(500).json({
      error: 'Error interno del servidor'
    });
  }
});

// Helper function to call messaging service
async function callMessagingService(method, params) {
  try {
    // For now, we'll use HTTP calls to messaging service
    // In production, this could be gRPC or direct Python integration
    const axios = require('axios');
    
    const messagingServiceUrl = process.env.MESSAGING_SERVICE_URL || 'http://messaging-service:8000';
    
    console.log(`Calling messaging service: ${method}`, params);
    
    const response = await axios.post(`${messagingServiceUrl}/api/${method}`, params, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    return response.data;
    
  } catch (error) {
    console.error('Error calling messaging service:', error.message);
    
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      return {
        success: false,
        error: error.response.data?.error || 'Error en servicio de mensajería'
      };
    }
    
    return {
      success: false,
      error: 'No se pudo conectar con el servicio de mensajería'
    };
  }
}

module.exports = router;