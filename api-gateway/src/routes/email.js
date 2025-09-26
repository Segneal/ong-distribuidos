const express = require('express');
const axios = require('axios');
const { authenticateToken, requireRole } = require('../middleware/auth');

const router = express.Router();

// URL del servicio de email
const EMAIL_SERVICE_URL = process.env.EMAIL_SERVICE_URL || 'http://email-service:3002';

// Middleware de autenticación para todas las rutas
router.use(authenticateToken);

// POST /api/email/welcome - Solo PRESIDENTE
router.post('/welcome', requireRole(['PRESIDENTE']), async (req, res) => {
  try {
    const { email, username, fullName, temporaryPassword } = req.body;

    if (!email || !username || !fullName || !temporaryPassword) {
      return res.status(400).json({
        error: 'Datos requeridos faltantes',
        message: 'Se requieren email, username, fullName y temporaryPassword'
      });
    }

    // Llamar al servicio de email
    const response = await axios.post(`${EMAIL_SERVICE_URL}/api/email/welcome`, {
      email,
      username,
      fullName,
      temporaryPassword,
      organizationName: 'ONG Empuje Comunitario'
    });

    res.status(200).json({
      success: true,
      message: 'Email de bienvenida enviado correctamente',
      messageId: response.data.messageId,
      previewUrl: response.data.previewUrl || null
    });
  } catch (error) {
    console.error('Error enviando email de bienvenida:', error);
    
    if (error.response) {
      return res.status(error.response.status).json({
        error: 'Error del servicio de email',
        message: error.response.data.message || 'Error al enviar email'
      });
    }

    res.status(500).json({
      error: 'Error interno del servidor',
      message: 'No se pudo conectar con el servicio de email'
    });
  }
});

// GET /api/email/test - Solo PRESIDENTE (para probar configuración)
router.get('/test', requireRole(['PRESIDENTE']), async (req, res) => {
  try {
    const response = await axios.get(`${EMAIL_SERVICE_URL}/api/email/test`);
    
    res.status(200).json({
      success: true,
      message: 'Servicio de email funcionando correctamente',
      config: response.data.config
    });
  } catch (error) {
    console.error('Error probando servicio de email:', error);
    
    if (error.response) {
      return res.status(error.response.status).json({
        error: 'Error del servicio de email',
        message: error.response.data.message || 'Servicio no disponible'
      });
    }

    res.status(500).json({
      error: 'Servicio de email no disponible',
      message: 'No se pudo conectar con el servicio de email'
    });
  }
});

module.exports = router;