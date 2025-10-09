const express = require('express');
const { authenticateToken, requireRole } = require('../middleware/auth');
const usersController = require('../controllers/usersController');
const router = express.Router();

// Aplicar autenticación a todas las rutas de usuarios
router.use(authenticateToken);

// GET /api/users - Solo PRESIDENTE
router.get('/', requireRole(['PRESIDENTE']), usersController.getUsers);

// GET /api/users/:id - Solo PRESIDENTE
router.get('/:id', requireRole(['PRESIDENTE']), usersController.getUserById);

// POST /api/users - Solo PRESIDENTE
router.post('/', requireRole(['PRESIDENTE']), usersController.createUser);

// PUT /api/users/:id - Solo PRESIDENTE
router.put('/:id', requireRole(['PRESIDENTE']), usersController.updateUser);

// DELETE /api/users/:id - Solo PRESIDENTE
router.delete('/:id', requireRole(['PRESIDENTE']), usersController.deleteUser);

module.exports = router;