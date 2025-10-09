const express = require('express');
const router = express.Router();

// GET /api/test - Test endpoint
router.get('/', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'API Gateway test endpoint working',
    timestamp: new Date().toISOString(),
    service: 'API Gateway'
  });
});

// GET /api/test/health - Health check for testing
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    service: 'API Gateway',
    timestamp: new Date().toISOString()
  });
});

module.exports = router;