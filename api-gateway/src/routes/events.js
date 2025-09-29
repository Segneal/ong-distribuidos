const express = require('express');
const { eventsService } = require('../services/grpcClients');
const { eventsTransformers, handleGrpcError, validateInput } = require('../utils/grpcMapper');
const { authenticateToken, requireRole, requirePermission } = require('../middleware/auth');
const router = express.Router();

// Aplicar autenticación a todas las rutas de eventos
router.use(authenticateToken);

// GET /api/events - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.get('/', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), async (req, res) => {
  try {
    const { includePastEvents, userId } = req.query;

    // Transformar filtros para gRPC
    const grpcRequest = eventsTransformers.toGrpcListEvents({
      includePastEvents: includePastEvents === 'true',
      userId
    });

    // Llamar al microservicio de eventos
    const grpcResponse = await eventsService.listEvents(grpcRequest);

    // Transformar respuesta
    const response = eventsTransformers.fromGrpcEventsList(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        events: response.events
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al obtener eventos:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// GET /api/events/:id - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.get('/:id', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), async (req, res) => {
  try {
    const { id } = req.params;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de evento inválido'
      });
    }

    // Llamar al microservicio de eventos
    const grpcRequest = { id: parseInt(id) };
    const grpcResponse = await eventsService.getEvent(grpcRequest);

    // Transformar respuesta
    const response = eventsTransformers.fromGrpcEventResponse(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        event: response.event
      });
    } else {
      res.status(404).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al obtener evento:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// POST /api/events - PRESIDENTE y COORDINADOR
router.post('/', requireRole(['PRESIDENTE', 'COORDINADOR']), async (req, res) => {
  try {
    const eventData = req.body;

    // Validar datos de entrada
    const validationErrors = validateInput.event(eventData);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        error: 'Datos de entrada inválidos',
        details: validationErrors
      });
    }

    // Transformar datos para gRPC
    const grpcRequest = eventsTransformers.toGrpcCreateEvent(eventData);

    // Llamar al microservicio de eventos
    const grpcResponse = await eventsService.createEvent(grpcRequest);

    // Transformar respuesta
    const response = eventsTransformers.fromGrpcEventResponse(grpcResponse);

    if (response.success) {
      // Automatically publish event to the network if creation was successful
      try {
        const axios = require('axios');
        const MESSAGING_SERVICE_URL = process.env.MESSAGING_SERVICE_URL || 'http://messaging-service:50054';
        
        console.log('Auto-publishing event to network:', response.event.id);
        
        await axios.post(`${MESSAGING_SERVICE_URL}/api/publishEvent`, {
          eventId: response.event.id.toString(),
          name: response.event.name,
          description: response.event.description,
          eventDate: response.event.event_date,
          userId: req.user.id
        });
        
        console.log('Event published to network successfully');
      } catch (publishError) {
        console.error('Error auto-publishing event to network:', publishError);
        // Don't fail the event creation if network publishing fails
      }

      res.status(201).json({
        success: true,
        message: response.message,
        event: response.event
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al crear evento:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// PUT /api/events/:id - PRESIDENTE y COORDINADOR
router.put('/:id', requireRole(['PRESIDENTE', 'COORDINADOR']), async (req, res) => {
  try {
    const { id } = req.params;
    const eventData = req.body;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de evento inválido'
      });
    }

    // Validar datos de entrada
    const validationErrors = validateInput.event(eventData);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        error: 'Datos de entrada inválidos',
        details: validationErrors
      });
    }

    // Transformar datos para gRPC
    const grpcRequest = eventsTransformers.toGrpcUpdateEvent(id, eventData);

    // Llamar al microservicio de eventos
    const grpcResponse = await eventsService.updateEvent(grpcRequest);

    // Transformar respuesta
    const response = eventsTransformers.fromGrpcEventResponse(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        event: response.event
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al actualizar evento:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// DELETE /api/events/:id - PRESIDENTE y COORDINADOR
router.delete('/:id', requireRole(['PRESIDENTE', 'COORDINADOR']), async (req, res) => {
  try {
    const { id } = req.params;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de evento inválido'
      });
    }

    // Llamar al microservicio de eventos
    const grpcRequest = { id: parseInt(id) };
    const grpcResponse = await eventsService.deleteEvent(grpcRequest);

    if (grpcResponse.success) {
      // Automatically publish event cancellation to the network
      try {
        const axios = require('axios');
        const MESSAGING_SERVICE_URL = process.env.MESSAGING_SERVICE_URL || 'http://messaging-service:50054';
        
        console.log('Auto-publishing event cancellation to network:', id);
        
        await axios.post(`${MESSAGING_SERVICE_URL}/api/cancelEvent`, {
          eventId: id.toString(),
          userId: req.user.id
        });
        
        console.log('Event cancellation published to network successfully');
      } catch (publishError) {
        console.error('Error auto-publishing event cancellation to network:', publishError);
        // Don't fail the event deletion if network publishing fails
      }

      res.status(200).json({
        success: true,
        message: grpcResponse.message
      });
    } else {
      res.status(400).json({
        error: grpcResponse.message
      });
    }
  } catch (error) {
    console.error('Error al eliminar evento:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// GET /api/events/:id/participants - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.get('/:id/participants', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), async (req, res) => {
  try {
    const { id } = req.params;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de evento inválido'
      });
    }

    // Llamar al microservicio de eventos
    const grpcRequest = { event_id: parseInt(id) };
    const grpcResponse = await eventsService.listParticipants(grpcRequest);

    // Transformar respuesta
    const response = eventsTransformers.fromGrpcParticipantsList(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        participants: response.participants
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al obtener participantes:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// POST /api/events/:id/participants - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.post('/:id/participants', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), async (req, res) => {
  try {
    const { id } = req.params;
    const { userId } = req.body;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de evento inválido'
      });
    }

    if (!userId || isNaN(parseInt(userId))) {
      return res.status(400).json({
        error: 'ID de usuario inválido'
      });
    }

    // Transformar datos para gRPC
    const grpcRequest = eventsTransformers.toGrpcAddParticipant(id, userId);

    // Llamar al microservicio de eventos
    const grpcResponse = await eventsService.addParticipant(grpcRequest);

    if (grpcResponse.success) {
      res.status(201).json({
        success: true,
        message: grpcResponse.message,
        participant: grpcResponse.participant
      });
    } else {
      res.status(400).json({
        error: grpcResponse.message
      });
    }
  } catch (error) {
    console.error('Error al agregar participante:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// DELETE /api/events/:id/participants/:userId - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.delete('/:id/participants/:userId', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), async (req, res) => {
  try {
    const { id, userId } = req.params;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de evento inválido'
      });
    }

    if (!userId || isNaN(parseInt(userId))) {
      return res.status(400).json({
        error: 'ID de usuario inválido'
      });
    }

    // Transformar datos para gRPC
    const grpcRequest = {
      event_id: parseInt(id),
      user_id: parseInt(userId)
    };

    // Llamar al microservicio de eventos
    const grpcResponse = await eventsService.removeParticipant(grpcRequest);

    if (grpcResponse.success) {
      res.status(200).json({
        success: true,
        message: grpcResponse.message
      });
    } else {
      res.status(400).json({
        error: grpcResponse.message
      });
    }
  } catch (error) {
    console.error('Error al quitar participante:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// POST /api/events/:id/distributed-donations - PRESIDENTE y COORDINADOR
router.post('/:id/distributed-donations', requireRole(['PRESIDENTE', 'COORDINADOR']), async (req, res) => {
  try {
    const { id } = req.params;
    const { donations } = req.body;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de evento inválido'
      });
    }

    if (!donations || !Array.isArray(donations) || donations.length === 0) {
      return res.status(400).json({
        error: 'Se requiere una lista de donaciones para registrar'
      });
    }

    // Validar estructura de donaciones
    for (const donation of donations) {
      if (!donation.donationId || isNaN(parseInt(donation.donationId))) {
        return res.status(400).json({
          error: 'ID de donación inválido'
        });
      }
      if (!donation.quantity || isNaN(parseInt(donation.quantity)) || parseInt(donation.quantity) <= 0) {
        return res.status(400).json({
          error: 'Cantidad de donación inválida'
        });
      }
    }

    // Transformar datos para gRPC
    const grpcRequest = eventsTransformers.toGrpcRegisterDistributedDonations(
      id, 
      donations, 
      req.user.id
    );

    // Llamar al microservicio de eventos
    const grpcResponse = await eventsService.registerDistributedDonations(grpcRequest);

    // Transformar respuesta
    const response = eventsTransformers.fromGrpcDistributedDonationsResponse(grpcResponse);

    if (response.success) {
      res.status(201).json({
        success: true,
        message: response.message,
        distributedDonations: response.distributedDonations
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al registrar donaciones repartidas:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// GET /api/events/:id/distributed-donations - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.get('/:id/distributed-donations', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), async (req, res) => {
  try {
    const { id } = req.params;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de evento inválido'
      });
    }

    // Llamar al microservicio de eventos
    const grpcRequest = { event_id: parseInt(id) };
    const grpcResponse = await eventsService.getDistributedDonations(grpcRequest);

    // Transformar respuesta
    const response = eventsTransformers.fromGrpcGetDistributedDonationsResponse(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        distributedDonations: response.distributedDonations
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al obtener donaciones repartidas:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

module.exports = router;