const express = require('express');
const Joi = require('joi');
const { sendWelcomeEmail, verifyEmailConfig } = require('../services/emailService');

const router = express.Router();

// Esquema de validación para email de bienvenida
const welcomeEmailSchema = Joi.object({
  email: Joi.string().email().required(),
  username: Joi.string().required(),
  fullName: Joi.string().required(),
  temporaryPassword: Joi.string().required(),
  organizationName: Joi.string().default('ONG Empuje Comunitario')
});

// POST /api/email/welcome - Enviar email de bienvenida con credenciales
router.post('/welcome', async (req, res) => {
  try {
    const { error, value } = welcomeEmailSchema.validate(req.body);
    
    if (error) {
      return res.status(400).json({
        error: 'Datos inválidos',
        details: error.details.map(d => d.message)
      });
    }

    const result = await sendWelcomeEmail(value);
    
    if (result.success) {
      const response = {
        success: true,
        message: 'Email de bienvenida enviado correctamente',
        messageId: result.messageId
      };
      
      // Agregar URL de previsualización en desarrollo
      if (result.previewUrl) {
        response.previewUrl = result.previewUrl;
      }
      
      res.status(200).json(response);
    } else {
      res.status(500).json({
        error: 'Error al enviar email',
        message: result.error
      });
    }
  } catch (error) {
    console.error('Error en welcome:', error);
    res.status(500).json({
      error: 'Error interno del servidor',
      message: error.message
    });
  }
});

// GET /api/email/test - Probar configuración de email
router.get('/test', async (req, res) => {
  try {
    const result = await verifyEmailConfig();
    
    if (result.success) {
      res.status(200).json(result);
    } else {
      res.status(500).json(result);
    }
  } catch (error) {
    res.status(500).json({
      error: 'Error interno del servidor',
      message: error.message
    });
  }
});

module.exports = router;