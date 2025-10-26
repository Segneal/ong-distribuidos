// Simular exactamente lo que hace el API Gateway
const { inventoryService } = require('./src/services/grpcClients');
const { inventoryTransformers } = require('./src/utils/grpcMapper');

async function testInventoryFlow() {
  console.log('=== Simulando flujo del API Gateway ===');
  
  try {
    // Simular datos de usuario autenticado
    const mockUser = {
      id: 11,
      username: 'admin',
      role: 'PRESIDENTE',
      organization: 'empuje-comunitario'
    };
    
    console.log('1. Usuario simulado:', mockUser);
    
    // Simular request de listado
    console.log('\n2. Probando listDonations...');
    const listFilters = {
      category: undefined,
      includeDeleted: false,
      organization: mockUser.organization
    };
    
    const grpcListRequest = inventoryTransformers.toGrpcListDonations(listFilters);
    console.log('3. gRPC List Request:', JSON.stringify(grpcListRequest, null, 2));
    
    const listResponse = await inventoryService.listDonations(grpcListRequest);
    console.log('4. List Response success:', listResponse.success);
    console.log('5. List Response donations count:', listResponse.donations?.length || 0);
    
    // Simular request de creación
    console.log('\n6. Probando createDonation...');
    const donationData = {
      category: 'ALIMENTOS',
      description: 'Prueba desde simulación API Gateway',
      quantity: 3
    };
    
    const grpcCreateRequest = inventoryTransformers.toGrpcCreateDonation(
      donationData, 
      mockUser.id, 
      mockUser.organization
    );
    console.log('7. gRPC Create Request:', JSON.stringify(grpcCreateRequest, null, 2));
    
    const createResponse = await inventoryService.createDonation(grpcCreateRequest);
    console.log('8. Create Response success:', createResponse.success);
    console.log('9. Create Response message:', createResponse.message);
    
    console.log('\n✅ Simulación completada exitosamente');
    
  } catch (error) {
    console.error('\n❌ Error en simulación:', error);
    console.error('Error code:', error.code);
    console.error('Error details:', error.details);
    console.error('Error message:', error.message);
  }
}

testInventoryFlow();