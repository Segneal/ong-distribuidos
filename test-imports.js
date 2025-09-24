// Test file to check grpcMapper imports
try {
  const grpcMapper = require('./api-gateway/src/utils/grpcMapper');
  console.log('Available exports:', Object.keys(grpcMapper));
  console.log('handleGrpcError type:', typeof grpcMapper.handleGrpcError);
  console.log('inventoryTransformers type:', typeof grpcMapper.inventoryTransformers);
  console.log('userTransformers type:', typeof grpcMapper.userTransformers);
} catch (error) {
  console.error('Error importing grpcMapper:', error);
}