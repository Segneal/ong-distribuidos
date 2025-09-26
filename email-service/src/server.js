const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

const emailRoutes = require('./routes/email');
const { errorHandler } = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware de seguridad
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Rutas
app.use('/api/email', emailRoutes);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    service: 'Email Service',
    timestamp: new Date().toISOString()
  });
});

// Middleware de manejo de errores
app.use(errorHandler);

// Manejo de rutas no encontradas
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Ruta no encontrada',
    message: `La ruta ${req.method} ${req.originalUrl} no existe`,
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Email Service corriendo en puerto ${PORT}`);
  console.log(`📧 Configuración SMTP: ${process.env.SMTP_HOST || 'No configurado'}`);
});

module.exports = app;