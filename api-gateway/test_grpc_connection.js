const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// Configuración de proto loader
const protoOptions = {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
};

// Cargar archivo proto
const inventoryProtoPath = path.join(__dirname, 'proto/inventory.proto');
console.log('Loading proto from:', inventoryProtoPath);

const inventoryPackageDefinition = protoLoader.loadSync(inventoryProtoPath, protoOptions);
const inventoryProto = grpc.loadPackageDefinition(inventoryPackageDefinition).inventory;

// Crear cliente gRPC
const inventoryClient = new inventoryProto.InventoryService(
  'localhost:50052',
  grpc.credentials.createInsecure()
);

console.log('Cliente gRPC creado');

// Función para probar ListDonations
async function testListDonations() {
  return new Promise((resolve, reject) => {
    console.log('\n=== Probando ListDonations ===');
    
    const request = {
      organization: 'empuje-comunitario'
    };
    
    console.log('Request:', JSON.stringify(request, null, 2));
    
    inventoryClient.ListDonations(request, (error, response) => {
      if (error) {
        console.error('Error en ListDonations:', error);
        console.error('Error code:', error.code);
        console.error('Error details:', error.details);
        reject(error);
      } else {
        console.log('Success response:', JSON.stringify(response, null, 2));
        resolve(response);
      }
    });
  });
}

// Función para probar CreateDonation
async function testCreateDonation() {
  return new Promise((resolve, reject) => {
    console.log('\n=== Probando CreateDonation ===');
    
    const request = {
      category: 1, // ALIMENTOS
      description: 'Prueba desde Node.js',
      quantity: 5,
      created_by: 11,
      organization: 'empuje-comunitario'
    };
    
    console.log('Request:', JSON.stringify(request, null, 2));
    
    inventoryClient.CreateDonation(request, (error, response) => {
      if (error) {
        console.error('Error en CreateDonation:', error);
        console.error('Error code:', error.code);
        console.error('Error details:', error.details);
        reject(error);
      } else {
        console.log('Success response:', JSON.stringify(response, null, 2));
        resolve(response);
      }
    });
  });
}

// Ejecutar pruebas
async function runTests() {
  try {
    await testListDonations();
    await testCreateDonation();
    console.log('\n🎉 Todas las pruebas completadas');
  } catch (error) {
    console.error('\n❌ Error en las pruebas:', error);
  }
}

runTests();