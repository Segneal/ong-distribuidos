// Script de debugging para el API Gateway
const express = require('express');
const { inventoryService, eventsService } = require('./src/services/grpcClients');

console.log('=== API Gateway Debug Script ===');

// Test 1: Verificar que los servicios gRPC estén disponibles
async function testGrpcServices() {
  console.log('\n1. Testing gRPC Services...');
  
  try {
    console.log('Testing inventory service...');
    const inventoryResponse = await inventoryService.listDonations({});
    console.log('✅ Inventory service OK:', inventoryResponse.success);
  } catch (error) {
    console.log('❌ Inventory service ERROR:', error.message);
  }
  
  try {
    console.log('Testing events service...');
    const eventsResponse = await eventsService.listEvents({});
    console.log('✅ Events service OK:', eventsResponse.success);
  } catch (error) {
    console.log('❌ Events service ERROR:', error.message);
  }
}

// Test 2: Verificar que las rutas estén cargadas
function testRoutes() {
  console.log('\n2. Testing Route Loading...');
  
  try {
    const inventoryRoutes = require('./src/routes/inventory');
    console.log('✅ Inventory routes loaded');
  } catch (error) {
    console.log('❌ Inventory routes ERROR:', error.message);
  }
  
  try {
    const eventsRoutes = require('./src/routes/events');
    console.log('✅ Events routes loaded');
  } catch (error) {
    console.log('❌ Events routes ERROR:', error.message);
  }
}

// Test 3: Crear un servidor de prueba mínimo
function createTestServer() {
  console.log('\n3. Creating Test Server...');
  
  const app = express();
  app.use(express.json());
  
  // Ruta de prueba simple
  app.get('/test', (req, res) => {
    res.json({ message: 'Test server working' });
  });
  
  // Ruta de prueba para inventario
  app.get('/test-inventory', async (req, res) => {
    try {
      console.log('Test inventory route called');
      const response = await inventoryService.listDonations({});
      res.json({ success: true, data: response });
    } catch (error) {
      console.error('Test inventory error:', error);
      res.status(500).json({ error: error.message });
    }
  });
  
  const port = 3005;
  app.listen(port, () => {
    console.log(`✅ Test server running on port ${port}`);
    console.log(`Test endpoints:`);
    console.log(`  - http://localhost:${port}/test`);
    console.log(`  - http://localhost:${port}/test-inventory`);
  });
}

// Ejecutar todas las pruebas
async function runDiagnostics() {
  await testGrpcServices();
  testRoutes();
  createTestServer();
}

runDiagnostics().catch(console.error);