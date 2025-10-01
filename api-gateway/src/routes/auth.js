const express = require('express');
const { authenticateToken } = require('../middleware/auth');
const authController = require('../controllers/authController');
const router = express.Router();

// POST /api/auth/login
router.post('/login', authController.login);

// POST /api/auth/logout
router.post('/logout', authenticateToken, authController.logout);

// GET /api/auth/me - Obtener información del usuario actual
router.get('/me', authenticateToken, authController.me);

// POST /api/auth/verify - Verificar si un token es válido
router.post('/verify', authController.verify);

module.exports = router;