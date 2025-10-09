const express = require('express');
const { authenticateToken, requireRole } = require('../middleware/auth');
const eventsController = require('../controllers/eventsController');
const router = express.Router();

// Aplicar autenticación a todas las rutas de eventos
router.use(authenticateToken);

// GET /api/events - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.get('/', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), eventsController.getEvents);

// GET /api/events/:id - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.get('/:id', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), eventsController.getEventById);

// POST /api/events - PRESIDENTE y COORDINADOR
router.post('/', requireRole(['PRESIDENTE', 'COORDINADOR']), eventsController.createEvent);

// PUT /api/events/:id - PRESIDENTE y COORDINADOR
router.put('/:id', requireRole(['PRESIDENTE', 'COORDINADOR']), eventsController.updateEvent);

// DELETE /api/events/:id - PRESIDENTE y COORDINADOR
router.delete('/:id', requireRole(['PRESIDENTE', 'COORDINADOR']), eventsController.deleteEvent);

// GET /api/events/:id/participants - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.get('/:id/participants', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), eventsController.getParticipants);

// POST /api/events/:id/participants - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.post('/:id/participants', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), eventsController.addParticipant);

// DELETE /api/events/:id/participants/:userId - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.delete('/:id/participants/:userId', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), eventsController.removeParticipant);

// POST /api/events/:id/distributed-donations - PRESIDENTE y COORDINADOR
router.post('/:id/distributed-donations', requireRole(['PRESIDENTE', 'COORDINADOR']), eventsController.addDistributedDonations);

// GET /api/events/:id/distributed-donations - PRESIDENTE, COORDINADOR y VOLUNTARIO
router.get('/:id/distributed-donations', requireRole(['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']), eventsController.getDistributedDonations);

module.exports = router;