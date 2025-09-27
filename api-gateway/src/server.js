const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware básico
app.use(helmet()); // Seguridad básica
app.use(cors()); // CORS para frontend
app.use(morgan('combined')); // Logging básico
app.use(express.json({ limit: '10mb' })); // JSON parsing
app.use(express.urlencoded({ extended: true })); // URL encoding



// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const { checkServiceHealth } = require('./services/grpcClients');
    const serviceHealth = await checkServiceHealth();
    
    res.status(200).json({
      status: 'OK',
      timestamp: new Date().toISOString(),
      service: 'API Gateway',
      microservices: serviceHealth
    });
  } catch (error) {
    console.error('Error en health check:', error);
    res.status(200).json({
      status: 'OK',
      timestamp: new Date().toISOString(),
      service: 'API Gateway',
      microservices: 'Health check no disponible'
    });
  }
});

// Importar rutas
const authRoutes = require('./routes/auth');
const usersRoutes = require('./routes/users');
const inventoryRoutes = require('./routes/inventory');
const eventsRoutes = require('./routes/events');
const donationRequestsRoutes = require('./routes/donationRequests');

// Configurar rutas
app.use('/api/auth', authRoutes);
app.use('/api/users', usersRoutes);
app.use('/api/inventory', inventoryRoutes);
app.use('/api/events', eventsRoutes);
app.use('/api/donation-requests', donationRequestsRoutes);

// Ruta por defecto
app.get('/', (req, res) => {
  res.json({
    message: 'API Gateway - Sistema de Gestión ONG Empuje Comunitario',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      auth: '/api/auth',
      users: '/api/users',
      inventory: '/api/inventory',
      events: '/api/events',
      donationRequests: '/api/donation-requests'
    }
  });
});

// Importar middleware de manejo de errores
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');

// Middleware para rutas no encontradas
app.use('*', notFoundHandler);

// Middleware de manejo de errores (debe ir al final)
app.use(errorHandler);

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 API Gateway ejecutándose en puerto ${PORT}`);
  console.log(`📊 Health check disponible en http://localhost:${PORT}/health`);
});

module.exports = app;